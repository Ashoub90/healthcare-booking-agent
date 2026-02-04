from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.agent.memory import InMemoryStore
from app.tools.agent_tools import (
    lookup_patient_tool,
    create_patient_tool,
    check_availability_tool,
    create_appointment_tool,
    send_notification_tool,
    log_agent_action_tool,
)


# =========================
# Initialize Memory Store
# =========================

memory_store = InMemoryStore()


# =========================
# Agent Service
# =========================

class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def handle_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        """

        # 1. Load memory
        memory = memory_store.get(session_id)

        # 2. Save user message
        memory_store.save(session_id, "user", user_message)

        # 3. Extract intent (temporary simple logic — later replace with LLM)
        intent = self._detect_intent(user_message)

        # 4. Route based on intent
        if intent == "lookup_patient":
            return self._handle_lookup_patient(session_id, user_message)

        elif intent == "check_availability":
            return self._handle_check_availability(session_id, user_message)

        elif intent == "create_appointment":
            return self._handle_create_appointment(session_id, user_message)

        else:
            reply = "Sorry, I didn't understand. Could you please rephrase?"
            memory_store.save(session_id, "assistant", reply)
            return {"reply": reply}


    # =========================
    # Intent Detection (placeholder)
    # =========================

    def _detect_intent(self, user_message: str) -> str:
        text = user_message.lower()

        if "phone" in text or text.isdigit():
            return "lookup_patient"
        if "book" in text or "appointment" in text:
            return "check_availability"
        if "confirm" in text:
            return "create_appointment"

        return "unknown"


    # =========================
    # Handlers
    # =========================

    def _handle_lookup_patient(self, session_id: str, user_message: str) -> Dict[str, Any]:
        phone_number = user_message.strip()

        patient = lookup_patient_tool(phone_number=phone_number, db=self.db)

        if not patient:
            reply = "I couldn't find your record. May I have your full name and email to register you?"
            memory_store.save(session_id, "assistant", reply)

            log_agent_action_tool(
                patient_id=None,
                user_message=user_message,
                agent_action="lookup_patient",
                system_decision="not_found",
                confidence_score=0.7,
                db=self.db
            )

            return {"reply": reply}

        reply = f"Welcome back {patient['full_name']}! What service would you like to book?"
        memory_store.save(session_id, "assistant", reply)

        log_agent_action_tool(
            patient_id=patient["id"],
            user_message=user_message,
            agent_action="lookup_patient",
            system_decision="found",
            confidence_score=0.9,
            db=self.db
        )

        return {"reply": reply, "patient": patient}


    def _handle_check_availability(self, session_id: str, user_message: str) -> Dict[str, Any]:
        # (Placeholder extraction — later LLM will extract date/service/time)
        appointment_date = "2026-02-05"
        service_type_id = 1
        preferred_time = None

        result = check_availability_tool(
            appointment_date=appointment_date,
            service_type_id=service_type_id,
            preferred_time=preferred_time,
            db=self.db
        )

        if "available_slots" in result:
            reply = f"Available times are: {', '.join(result['available_slots'])}. Which one do you prefer?"
        else:
            reply = "That time is not available. I can suggest another slot."

        memory_store.save(session_id, "assistant", reply)

        log_agent_action_tool(
            patient_id=None,
            user_message=user_message,
            agent_action="check_availability",
            system_decision="slots_returned",
            confidence_score=0.85,
            db=self.db
        )

        return {"reply": reply, "availability": result}


    def _handle_create_appointment(self, session_id: str, user_message: str) -> Dict[str, Any]:
        # Placeholder values — in real version extracted from memory
        patient_id = 1
        service_type_id = 1
        appointment_date = "2026-02-05"
        start_time = "15:00"

        appointment = create_appointment_tool(
            patient_id=patient_id,
            service_type_id=service_type_id,
            appointment_date=appointment_date,
            start_time=start_time,
            db=self.db
        )

        reply = f"✅ Your appointment is confirmed for {appointment['date']} at {appointment['start_time']}."

        memory_store.save(session_id, "assistant", reply)

        send_notification_tool(
            appointment_id=appointment["appointment_id"],
            channel="email",
            recipient="user@example.com",
            message=reply,
            db=self.db
        )

        log_agent_action_tool(
            patient_id=patient_id,
            user_message=user_message,
            agent_action="book_appointment",
            system_decision="booked",
            confidence_score=0.95,
            db=self.db
        )

        return {"reply": reply, "appointment": appointment}
