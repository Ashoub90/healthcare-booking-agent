from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date, time

from app.services.patient_service import (
    get_patient_by_phone,
    create_patient
)
from app.services.availability_service import check_availability
from app.services.appointment_service import create_appointment_service
from app.services.notification_service import send_notification_service
from app.services.logging_service import log_agent_action_service


# =========================
# Tool 1: Lookup Patient
# =========================

def lookup_patient_tool(
    phone_number: str,
    db: Session,
    session_state: Dict[str, Any]
) -> Optional[Dict[str, Any]]:

    session_state["phone_number"] = phone_number

    patient = get_patient_by_phone(db, phone_number)

    if not patient:
        session_state["patient_id"] = None
        return None

    session_state["patient_id"] = patient.id

    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "phone_number": patient.phone_number,
        "email": patient.email,
        "is_insured": patient.is_insured,
        "insurance_provider": patient.insurance_provider
    }


# =========================
# Tool 2: Create Patient
# =========================

def create_patient_tool(
    full_name: str,
    phone_number: str,
    email: Optional[str],
    is_insured: bool,
    insurance_provider: Optional[str],
    db: Session,
    session_state: Dict[str, Any]
) -> Dict[str, Any]:

    patient = create_patient(
        db=db,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        is_insured=is_insured,
        insurance_provider=insurance_provider
    )

    session_state["patient_id"] = patient.id
    session_state["phone_number"] = phone_number

    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "phone_number": patient.phone_number
    }


# =========================
# Tool 3: Check Availability
# =========================

def check_availability_tool(
    appointment_date: str,
    service_type_id: int,
    db: Session,
    session_state: Dict[str, Any]
) -> Dict[str, Any]:

    if hasattr(appointment_date, 'isoformat'):
        session_state["appointment_date"] = appointment_date.isoformat()
    else:
        session_state["appointment_date"] = str(appointment_date)

    session_state["service_type_id"] = service_type_id

    slots = check_availability(
        appointment_date=appointment_date,
        service_type_id=service_type_id,
        db=db
    )

    return {"available_slots": slots}


# =========================
# Tool 4: Create Appointment
# =========================

def create_appointment_tool(
    patient_id: int,
    service_type_id: int,
    appointment_date: date,
    start_time: time,
    db: Session,
    session_state: Dict[str, Any]
) -> Dict[str, Any]:

    appointment = create_appointment_service(
        db=db,
        patient_id=patient_id,
        service_type_id=service_type_id,
        appointment_date=appointment_date,
        start_time=start_time
    )

    session_state["appointment_id"] = appointment.id

    return {
        "appointment_id": appointment.id,
        "status": appointment.status,
        "date": appointment.appointment_date.isoformat(),
        "start_time": appointment.start_time.isoformat(),
        "end_time": appointment.end_time.isoformat()
    }


# =========================
# Tool 5: Send Notification
# =========================

def send_notification_tool(
    appointment_id: int,
    channel: str,
    recipient: str,
    message: str,
    db: Session
) -> Dict[str, Any]:

    notification = send_notification_service(
        appointment_id=appointment_id,
        channel=channel,
        recipient=recipient,
        message=message,
        db=db
    )

    return {
        "notification_id": notification.id,
        "status": notification.status
    }


# =========================
# Tool 6: Log Agent Action
# =========================

def log_agent_action_tool(
    user_message: str,           # Required (No default)
    agent_action: str,            # Required (No default)
    system_decision: str,         # Required (No default)
    db: Session,                  # Required (No default)
    patient_id: Optional[int] = None,      # Optional (Has default)
    confidence_score: Optional[float] = 1.0 # Optional (Has default)
) -> str:

    log_agent_action_service(
        patient_id=patient_id,
        user_message=user_message,
        agent_action=agent_action,
        system_decision=system_decision,
        confidence_score=confidence_score,
        db=db
    )
    
    return "Action logged successfully."