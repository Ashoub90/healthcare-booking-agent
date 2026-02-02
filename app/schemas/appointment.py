from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AppointmentBase(BaseModel):
    scheduled_at: datetime


class AppointmentCreate(AppointmentBase):
    patient_id: int


class Appointment(AppointmentBase):
    id: int
    patient_id: int

    class Config:
        orm_mode = True
