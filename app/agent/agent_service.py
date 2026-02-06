from sqlalchemy.orm import Session
from typing import Dict, Any

import langchain
print(f"--- DEBUG: LangChain version is {langchain.__version__} ---")

from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agent.memory import MemoryStore, InMemoryStore
from app.agent.langchain_tools import get_langchain_tools


# =========================
# System Prompt
# =========================

SYSTEM_PROMPT = """
You are an AI Appointment Booking Assistant for a medical clinic.

Your role is to help patients:
- identify themselves or register if new
- check appointment availability
- book appointments
- confirm bookings
- send confirmations

You MUST strictly follow the rules below.

1. You are NOT a medical professional.
   Never provide medical advice.

2. Never book an appointment unless:
   - the patient is identified
   - availability has been checked
   - the user explicitly confirms the date and time

3. Never assume missing information.
   Ask one question at a time if something is missing.

4. Never invent data.
   Use tools to perform actions.

5. Log important actions using the logging tool.

Respond in natural language only.
Do not expose internal system details.
"""


# =========================
# Agent Service
# =========================

class AgentService:
    def __init__(
        self,
        db: Session,
        memory_store: MemoryStore | None = None,
    ):
        self.db = db
        self.memory_store = memory_store or InMemoryStore()

        # 1️⃣ LLM
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
        )

        # 2️⃣ Tools
        self.tools = get_langchain_tools(db)

        # 3️⃣ Prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # 4️⃣ Agent
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,

        )    


        # 5️⃣ Executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,               # set False in prod if needed
            handle_parsing_errors=True,
        )

    # =========================
    # Public API
    # =========================

    def handle_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Main entry point used by /chat API
        """

        # Load memory
        chat_history = self.memory_store.get(session_id)

        # Run agent
        result = self.executor.invoke(
            {
                "input": user_message,
                "chat_history": chat_history,
            }
        )

        reply = result["output"]

        # Save memory
        self.memory_store.save(session_id, "user", user_message)
        self.memory_store.save(session_id, "assistant", reply)

        return {
            "reply": reply
        }
