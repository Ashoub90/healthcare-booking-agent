from langchain.tools import StructuredTool
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date, time

from app.tools.agent_tools import (
    lookup_patient_tool,
    create_patient_tool,
    check_availability_tool,
    create_appointment_tool,
    send_notification_tool,
    get_patient_appointments_tool,
    cancel_appointment_tool       
)


def get_langchain_tools(
    db: Session,
    session_state: Dict[str, Any]
):
    return [
        StructuredTool.from_function(
            name="lookup_patient",
            description="ALWAYS call this immediately when a phone number is provided to see if the patient exists.",
            func=lambda phone_number:
                lookup_patient_tool(
                    phone_number=phone_number,
                    db=db,
                    session_state=session_state
                )
        ),

        StructuredTool.from_function(
            name="create_patient",
            description=(
                "Register a new patient. For 'is_insured', you can accept 'yes', 'no', 'true', or 'false'. "
                "The system will handle the conversion automatically."
            ),
            func=lambda full_name, phone_number, email, is_insured, insurance_provider:
                create_patient_tool(
                    full_name=full_name,
                    phone_number=phone_number,
                    email=email,
                    is_insured=is_insured,
                    insurance_provider=insurance_provider,
                    db=db,
                    session_state=session_state
                )
        ),

        StructuredTool.from_function(
            name="check_availability",
            description="Check available slots for a date (YYYY-MM-DD) and service_type_id (1: Initial, 2: Follow-up, 3: Lab Review).",
            func=lambda appointment_date, service_type_id:
                check_availability_tool(
                    appointment_date=appointment_date,
                    service_type_id=service_type_id,
                    db=db,
                    session_state=session_state
                )
),

        StructuredTool.from_function(
            name="create_appointment",
            description="Create an appointment after the patient confirms a specific date and time.",
            func=lambda patient_id, service_type_id, appointment_date, start_time:
                create_appointment_tool(
                    patient_id=patient_id,
                    service_type_id=service_type_id,
                    appointment_date=appointment_date,
                    start_time=start_time,
                    db=db,
                    session_state=session_state
                )
        ),

        StructuredTool.from_function(
            name="get_patient_appointments",
            description="Retrieves upcoming appointments. Use the 'ID' from this list when calling cancel_appointment.",
            func=lambda patient_id:
                get_patient_appointments_tool(
                    patient_id=patient_id,
                    db=db
                )
        ),

        StructuredTool.from_function(
            name="cancel_appointment",
            description="Cancels an appointment. You MUST provide the exact appointment_id retrieved from get_patient_appointments. Never guess or use '1' as a default.",
            func=lambda appointment_id:
                cancel_appointment_tool(
                    appointment_id=appointment_id,
                    db=db
                )
        ),

        StructuredTool.from_function(
            name="send_notification",
            description="Send appointment confirmation via WhatsApp or Email.",
            func=lambda appointment_id, channel, recipient, message:
                send_notification_tool(
                    appointment_id=appointment_id,
                    channel=channel,
                    recipient=recipient,
                    message=message,
                    db=db
                )
        ),

    ]

