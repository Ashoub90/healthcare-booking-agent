from pydantic import BaseModel
from datetime import date, time, datetime

class AppointmentCreate(BaseModel):
    patient_id: int
    service_type_id: int
    appointment_date: date
    start_time: time


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    service_type_id: int
    appointment_date: date
    start_time: time
    end_time: time
    status: str
    external_calendar_id: str | None
    sync_status: str
    created_at: datetime

    class Config:
        from_attributes = True
