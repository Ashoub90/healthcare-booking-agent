from pydantic import BaseModel
from datetime import datetime

class NotificationOut(BaseModel):
    id: int
    appointment_id: int
    channel: str
    recipient: str
    message: str
    status: str
    sent_at: datetime

    class Config:
        from_attributes = True
