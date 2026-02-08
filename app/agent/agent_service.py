from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agent.memory import MemoryStore, InMemoryStore, memory_store_instance
from app.agent.session_state import SessionStateStore, state_store_instance
from app.agent.langchain_tools import get_langchain_tools


# =========================
# System Prompt
# =========================


SYSTEM_PROMPT = """
You are an AI Appointment Booking Assistant for a medical clinic.

You help patients:
- Identify themselves or register if new
- Check appointment availability
- Book appointments
- Confirm bookings
- Send confirmations

CORE OPERATING RULES:
1. NO MEDICAL ADVICE: You are not a doctor. Never provide medical info.
2. ONE AT A TIME: Ask ONLY ONE question for missing information. Do not overwhelm the user with a list of requirements.
3. IMMEDIATE ACTION: If a user provides a phone number, call 'lookup_patient' immediately. Do not ask for permission to use your tools.
4. NO REPEATS: If a piece of information (like phone_number) is visible in the 'CURRENT SESSION STATE' message, NEVER ask for it again. Use it directly to fill tool arguments.
5. NO DESCRIBING: Do not tell the user what tool you are calling. Just provide the natural language result.
6. MILESTONE LOGGING: You must call log_action only when a major step is completed (Identification, Registration, or Booking). Do not log general greetings or clarifications.

LOGIC FLOW:
- If patient_id is null in State → The patient is NOT identified. Ask for Name, then Email, then Insurance (one by one) to register them.
- If patient_id exists in State → The patient is identified. Proceed to check availability.
- Never book unless the user explicitly confirms a specific date and time.

The current date is {current_date}. 
When a user asks for 'tomorrow' or 'next week', calculate the date based on this.
Always use YYYY-MM-DD format for tool calls.

When an appointment is booked, always ask the patient if they prefer confirmation via Email or WhatsApp. Based on their choice, set the notification channel accordingly. If they don't specify, default to WhatsApp.

Respond in natural language only. Do not expose system internal keys (like IDs) to the user.
"""


# =========================
# Agent Service
# =========================

class AgentService:
    def __init__(
        self,
        db: Session,
        memory_store: MemoryStore | None = None,
        state_store: SessionStateStore | None = None,
    ):
        self.db = db
        self.memory_store = memory_store or memory_store_instance
        self.state_store = state_store or state_store_instance

        # LLM
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
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
        print("\n" + "="*50)
        print(f"BEFORE RUN - SESSION: {session_id}")
        session_state = self.state_store.get(session_id)
        print(f"STATE LOADED: {json.dumps(session_state, indent=2)}")
        print("="*50 + "\n")
        # --- DEBUG END ---
        
        current_date_str = datetime.now().strftime("%A, %B %d, %Y")

        # Load memory & state
        chat_history = self.memory_store.get(session_id)

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
                "chat_history": chat_history,
                "session_state": json.dumps(session_state),
                "current_date": current_date_str,
            }
        )

        reply = result["output"]

        # Persist memory + state
        self.memory_store.save(session_id, "user", user_message)
        self.memory_store.save(session_id, "assistant", reply)
        self.state_store.set(session_id, session_state)


        # --- DEBUG START ---
        print("\n" + "!"*50)
        print(f"AFTER RUN - STATE SAVED: {json.dumps(session_state, indent=2)}")
        print("!"*50 + "\n")
        # --- DEBUG END ---
        return {"reply": reply}
