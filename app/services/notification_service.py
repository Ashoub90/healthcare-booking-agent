from sqlalchemy.orm import Session
from app.db import models
from app.services.logging_service import log_agent_action_service

def send_notification_service(
    appointment_id: int,
    channel: str,
    recipient: str,
    message: str,
    db: Session
) -> models.Notification:
    """
    Creates a notification record and logs the event.
    """

    # 1. Create the Notification Record
    notification = models.Notification(
        appointment_id=appointment_id,
        channel=channel,
        recipient=recipient,
        message=message,
        status="pending", # Stays pending until the actual API call succeeds later
    )

    db.add(notification)
    
    # 2. Find the patient_id for the audit log
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    patient_id = appointment.patient_id if appointment else None

    # 3. Log the action for the Dashboard
    log_agent_action_service(
        db=db,
        patient_id=patient_id,
        log_context="[System Auto-Log]",
        agent_action="NOTIFICATION_SENT",
        system_decision=f"Notification initialized for Appt {appointment_id} via {channel}.",
        confidence_score=1.0
    )

    db.commit()
    db.refresh(notification)

    return notification