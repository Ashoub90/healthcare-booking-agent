from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime
import logging

from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agent.memory import DBMemoryStore
from app.agent.session_state import DBSessionStateStore
from app.agent.langchain_tools import get_langchain_tools
from langchain_core.messages import trim_messages

logger = logging.getLogger(__name__)

# =========================
# System Prompt
# =========================


SYSTEM_PROMPT = """
You are an AI Appointment Booking Assistant for a medical clinic.

You help patients:
- Identify themselves or register if new.
- View, book, or cancel appointments.
- Confirm bookings and send notifications.

SERVICE_TYPES:
- Initial Consultation: ID 1 (30 mins)
- Follow-up: ID 2 (15 mins)
- Lab Review: ID 3 (15 mins)

CORE OPERATING RULES:
1. NO MEDICAL ADVICE: You are not a doctor.
2. ONE AT A TIME: Ask ONLY ONE question for missing information. 
3. IMMEDIATE ACTION: If a user provides a phone number, call 'lookup_patient' immediately.
4. MAPPING RULE: Use the integer ID from the SERVICE_TYPES list above when calling booking tools.
5. TWO-PHASE BOOKING: When a user picks a time, you must FIRST repeat the details and ask for explicit confirmation. NEVER call 'create_appointment' until the user says "Yes" or "Go ahead".
6. NO TECHNICAL JARGON: Never ask the user for specific date formats (like YYYY-MM-DD) or technical IDs. Accept dates in natural language (e.g., "tomorrow", "next Friday", "March 2nd").
7. NO REPEATS: If 'phone_number' or 'patient_id' is in the 'CURRENT SESSION STATE', NEVER ask for them again.
8. NO DESCRIBING: Do not tell the user what tool you are calling. Just provide the natural language result.
9. MILESTONE LOGGING: Call log_action ONLY when Identification, Registration, or Booking is completed.

LOGIC FLOW:
1. IDENTIFICATION: Obtain 'phone_number' and call 'lookup_patient'.
2. REGISTRATION: Collect Name -> Email -> Insurance (one by one) and call 'create_patient'.
3. VIEWING: Call 'get_patient_appointments'.
4. CANCELLATION: List choices, confirm ID, then call 'cancel_appointment'.
5. BOOKING: 
   - Step A: Check availability and present options.
   - Step B: Once a user selects a slot, VERIFY intent (Ask: "Confirm 9:30 AM on Feb ?").
   - Step C: Only after "Yes", call 'create_appointment'.
   - POST-BOOKING: Transition to asking for notification preference (Email or WhatsApp).

The current date is {current_date}. Always use YYYY-MM-DD format for tool calls internally.

CLINIC HOURS: The clinic is open Monday through Friday, 9:00 AM to 5:00 PM. We are closed on Saturdays and Sundays. If a user asks for these days, politely inform them we are closed and suggest the next available Monday.

Respond in natural language only.
"""


# =========================
# Agent Service
# =========================

class AgentService:
    def __init__(
        self,
        db: Session,
        memory_store: Any = None,
        state_store: Any = None,
    ):
        self.db = db
        self.memory_store = memory_store or DBMemoryStore(db)
        self.state_store = state_store or DBSessionStateStore(db)


        # LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            stream_usage=True
        )

        self.trimmer = trim_messages(
            max_tokens=1000,
            strategy="last",
            token_counter=self.llm, 
            include_system=True,    
            allow_partial=False,
            start_on="human",       
        )


        # Prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
        ("system", SYSTEM_PROMPT), # Remove {session_state} from the string in SYSTEM_PROMPT
        ("system", "CURRENT SESSION STATE: {session_state}"), # New dedicated line
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    # =========================
    # Public API
    # =========================

    def handle_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        
        logger.debug(f"BEFORE RUN - SESSION: {session_id}")
        
        session_state = self.state_store.get(session_id)
        chat_history = self.memory_store.get(session_id)
        
        logger.debug(f"STATE LOADED: {json.dumps(session_state, indent=2)}")
        
        
        trimmed_history = self.trimmer.invoke(chat_history)
        
        current_date_str = datetime.now().strftime("%A, %B %d, %Y")


        self.memory_store.save(session_id, "user", user_message)


        # Build tools WITH state reference
        tools = get_langchain_tools(
            db=self.db,
            session_state=session_state
        )

        # Build agent dynamically (important!)
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=tools,
            prompt=self.prompt,
        )

        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
        )

        # Invoke
        result = executor.invoke(
            {
                "input": user_message,
                "chat_history": trimmed_history,
                "session_state": json.dumps(session_state),
                "current_date": current_date_str,
            }
        )

        reply = result["output"]

        # Persist memory + state
        self.memory_store.save(session_id, "assistant", reply)
        self.state_store.set(session_id, session_state)



        logger.debug(f"AFTER RUN - STATE SAVED: {json.dumps(session_state, indent=2)}")
        

        return {"reply": reply}
