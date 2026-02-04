from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.services.booking_service import create_appointment_service
from app.services.availability_service import check_availability_service
from app.services.notification_service import send_notification_service
from app.services.logging_service import log_agent_action_service
from app.db import models


# =========================
# Tool 1: Lookup Patient
# =========================

def lookup_patient_tool(phone_number: str, db: Session) -> Optional[Dict[str, Any]]:
    patient = db.query(models.Patient).filter(
        models.Patient.phone_number == phone_number
    ).first()

    if not patient:
        return None

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
    db: Session
) -> Dict[str, Any]:

    patient = models.Patient(
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        is_insured=is_insured,
        insurance_provider=insurance_provider
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

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
    preferred_time: Optional[str],
    db: Session
) -> Dict[str, Any]:
    """
    If preferred_time is provided → check that specific slot.
    If not provided → return all available slots for the day.
    """

    result = check_availability_service(
        appointment_date=appointment_date,
        service_type_id=service_type_id,
        preferred_time=preferred_time,
        db=db
    )

    return result


# =========================
# Tool 4: Create Appointment
# =========================

def create_appointment_tool(
    patient_id: int,
    service_type_id: int,
    appointment_date: str,
    start_time: str,
    db: Session
) -> Dict[str, Any]:

    appointment = create_appointment_service(
        patient_id=patient_id,
        service_type_id=service_type_id,
        appointment_date=appointment_date,
        start_time=start_time,
        db=db
    )

    return {
        "appointment_id": appointment.id,
        "status": appointment.status,
        "date": str(appointment.appointment_date),
        "start_time": str(appointment.start_time),
        "end_time": str(appointment.end_time)
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
    patient_id: Optional[int],
    user_message: str,
    agent_action: str,
    system_decision: str,
    confidence_score: Optional[float],
    db: Session
) -> None:

    log_agent_action_service(
        patient_id=patient_id,
        user_message=user_message,
        agent_action=agent_action,
        system_decision=system_decision,
        confidence_score=confidence_score,
        db=db
    )
