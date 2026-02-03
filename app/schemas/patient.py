from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientCreate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[str]
    is_insured: bool
    insurance_provider: Optional[str]


class PatientOut(BaseModel):
    id: int
    full_name: str
    phone_number: str
    email: Optional[str]
    is_insured: bool
    insurance_provider: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
