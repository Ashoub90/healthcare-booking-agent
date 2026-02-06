from langchain.tools import StructuredTool
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, time

from app.tools.agent_tools import (
    lookup_patient_tool,
    create_patient_tool,
    check_availability_tool,
    create_appointment_tool,
    send_notification_tool,
    log_agent_action_tool,
)


# NOTE:
# We inject `db` at runtime from AgentService,
# so LangChain will NOT see it as an argument.


def lookup_patient(phone_number: str) -> Optional[dict]:
    return lookup_patient_tool(phone_number=phone_number, db=lookup_patient.db)


def create_patient(
    full_name: str,
    phone_number: str,
    email: Optional[str],
    is_insured: bool,
    insurance_provider: Optional[str],
) -> dict:
    return create_patient_tool(
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        is_insured=is_insured,
        insurance_provider=insurance_provider,
        db=create_patient.db
    )


def check_availability(
    appointment_date: date,
    service_type_id: int,
) -> dict:
    return check_availability_tool(
        appointment_date=appointment_date,
        service_type_id=service_type_id,
        db=check_availability.db
    )


def create_appointment(
    patient_id: int,
    service_type_id: int,
    appointment_date: date,
    start_time: time,
) -> dict:
    return create_appointment_tool(
        patient_id=patient_id,
        service_type_id=service_type_id,
        appointment_date=appointment_date,
        start_time=start_time,
        db=create_appointment.db
    )


def send_notification(
    appointment_id: int,
    channel: str,
    recipient: str,
    message: str,
) -> dict:
    return send_notification_tool(
        appointment_id=appointment_id,
        channel=channel,
        recipient=recipient,
        message=message,
        db=send_notification.db
    )


def log_action(
    patient_id: Optional[int],
    user_message: str,
    agent_action: str,
    system_decision: str,
    confidence_score: Optional[float],
) -> None:
    log_agent_action_tool(
        patient_id=patient_id,
        user_message=user_message,
        agent_action=agent_action,
        system_decision=system_decision,
        confidence_score=confidence_score,
        db=log_action.db
    )


# =========================
# Tool registry
# =========================

def get_langchain_tools(db: Session):
    """
    Attach DB session dynamically and return LangChain tools.
    """

    # Inject db into tool functions
    lookup_patient.db = db
    create_patient.db = db
    check_availability.db = db
    create_appointment.db = db
    send_notification.db = db
    log_action.db = db

    return [
        StructuredTool.from_function(
            name="lookup_patient",
            description="Look up an existing patient by phone number.",
            func=lookup_patient,
        ),
        StructuredTool.from_function(
            name="create_patient",
            description="Register a new patient with contact and insurance details.",
            func=create_patient,
        ),
        StructuredTool.from_function(
            name="check_availability",
            description="Check available appointment slots for a given date and service type.",
            func=check_availability,
        ),
        StructuredTool.from_function(
            name="create_appointment",
            description="Create an appointment after the user confirms date and time.",
            func=create_appointment,
        ),
        StructuredTool.from_function(
            name="send_notification",
            description="Send appointment confirmation via email or WhatsApp.",
            func=send_notification,
        ),
        StructuredTool.from_function(
            name="log_action",
            description="Log an agent action for audit and debugging.",
            func=log_action,
        ),
    ]
