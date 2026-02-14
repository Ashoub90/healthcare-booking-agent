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
            # We reuse your email logic here
            # In a real app, you'd pass name/date separately, 
            # but for now we can just use the message string.
            send_confirmation_email(recipient, "Patient", message) 
            notification.status = "sent" # Update status to sent if successful
        except Exception:
            notification.status = "failed"

    # ... rest of your logging logic ...
    db.commit()
    db.refresh(notification)
    return notification