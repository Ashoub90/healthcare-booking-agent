# app/services/notification_service.py
from sqlalchemy.orm import Session
from app.db import models


def send_notification_service(
    appointment_id: int,
    channel: str,
    recipient: str,
    message: str,
    db: Session
) -> models.Notification:
    """
    Minimal implementation.
    Later this will call Email / WhatsApp APIs.
    """

    notification = models.Notification(
        appointment_id=appointment_id,
        channel=channel,
        recipient=recipient,
        message=message,
        status="sent",
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification
