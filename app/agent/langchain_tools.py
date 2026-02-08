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
    log_agent_action_tool,
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
            description="Register a new patient.",
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
            description="Check available appointment slots.",
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
            description="Create an appointment after confirmation.",
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
            name="send_notification",
            description="Send appointment confirmation.",
            func=lambda appointment_id, channel, recipient, message:
                send_notification_tool(
                    appointment_id=appointment_id,
                    channel=channel,
                    recipient=recipient,
                    message=message,
                    db=db
                )
        ),

        StructuredTool.from_function(
            name="log_action",
            description="Call this ONLY after a significant milestone is reached: a patient is identified, a new patient is registered, or an appointment is successfully booked.",
            func=lambda user_message, agent_action, system_decision, patient_id=None, confidence_score=1.0:
                log_agent_action_tool(
                user_message=user_message,
                agent_action=agent_action,
                system_decision=system_decision,
                patient_id=patient_id,
                confidence_score=confidence_score,
                db=db
                )
        ),
    ]
