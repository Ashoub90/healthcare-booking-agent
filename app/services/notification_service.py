from sqlalchemy.orm import Session
from app.db import models
from app.services.logging_service import log_agent_action_service
from app.services.email_service import send_confirmation_email


def send_notification_service(
    appointment_id: int,
    channel: str,
    recipient: str,
    message: str,
    db: Session
) -> models.Notification:
    
    # 1. Create the DB record (Your existing code)
    notification = models.Notification(
        appointment_id=appointment_id,
        channel=channel,
        recipient=recipient,
        message=message,
        status="pending", 
    )
    db.add(notification)
    
    # 2. ACTUALLY SEND THE EMAIL
    if channel == "email":
        try:
            
            send_confirmation_email(recipient, "Patient", message) 
            notification.status = "sent" 
        except Exception:
            notification.status = "failed"

    
    db.commit()
    db.refresh(notification)
    return notification