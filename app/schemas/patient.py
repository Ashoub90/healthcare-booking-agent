from pydantic import BaseModel
from typing import Optional


class PatientBase(BaseModel):
    name: str


class PatientCreate(PatientBase):
    pass


class Patient(PatientBase):
    id: int

    class Config:
        orm_mode = True
