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
9. NO "HOLD ON": Do not tell the user to "wait" or "hold on" while you call a tool. Just execute the tool and report the result once it is finished.

10. NO ACTION NARRATION:
NEVER EVER say that you are going to do something unless you are actually doing it immediately.
NEVER EVER SAY phrases like:
- "Let me check..."
- "I will look that up..."
- "One moment..."

Only:
- Ask for missing information, OR
- Provide a result after completing an action.

11.PHONE NUMBER UNDERSTANDING (CRITICAL):
Users may provide phone numbers as:
- Spoken words ("zero one one three...")
- Split across messages ("zero one one..." then "seven")

12. STRICT ID VALIDATION (CRITICAL):
You MUST NEVER call 'cancel_appointment' unless the appointment_id was explicitly provided by the system from 'get_patient_appointments'.

- NEVER guess an ID
- NEVER use default values like 1
- If the ID is not confirmed, you MUST ask the user again
- If unsure, say: "Please choose which appointment to cancel from your list."

13. TOOL OUTPUT IS SOURCE OF TRUTH (CRITICAL):

- You MUST NOT guess availability.
- You MUST ONLY rely on the output of 'check_availability'.
- If the tool says a time is available, you MUST treat it as available.
- If the tool says it is not available, you MUST NOT contradict it.

This rule is mandatory and cannot be bypassed.

When a tool returns structured data:
- Convert it into natural language for the user.
- Match the language of the conversation.
- Never repeat raw JSON.

14. NEVER say "write" something (e.g., please write your phone number). ALWAYS use "provide" (whether in English or Arabic).

LOGIC FLOW:
1. IDENTIFICATION: Obtain 'phone_number' and call 'lookup_patient'.
2. REGISTRATION: 
   - Collect Full Name -> Email.
   - Ask: "Do you have insurance?"
   - IF YES: Ask for the Insurance Provider Name.
   - Call 'create_patient' only after you have Name, Email, and Provider (if applicable).
3. VIEWING: Call 'get_patient_appointments'.
4. CANCELLATION: List choices, confirm ID, then call 'cancel_appointment'. 
5. BOOKING: 
    - Step A: Ask for date if missing.

    - Step B: Ask the user for their PREFERRED TIME (do NOT list all slots).

    - Step C: Call 'check_availability' internally.

    CRITICAL:
    When the user provides a preferred time, you MUST extract it and pass it as "requested_time" in HH:MM format when calling 'check_availability'.

    NEVER call 'check_availability' without "requested_time" if the user already mentioned a time.

    NEVER infer availability by reading or interpreting a list of times.
    Always rely on the tool's structured response.

    - Step D:
        - If the requested time is available:
            → Ask for confirmation.
        - If NOT available:
            → Suggest the closest available times (MAX 2 options).

    NEVER list all available slots unless the user explicitly asks.
   - POST-BOOKING: Transition to asking for notification preference (Email or WhatsApp).
   - If the patient's email is already available in the patient record, do not ask for it again.

- Reference the current date ({current_date}) for all calculations.
- If the user provides a date, the system will determine weekdays. Do not assume a day is closed unless the availability tool confirms it.   

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
            model="gpt-4o",
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
        ("system", SYSTEM_PROMPT),
        ("system", "CURRENT SESSION STATE: {session_state}"),
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
            max_iterations=10,
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
        

        return {"reply": reply,
                "session_state": session_state}
