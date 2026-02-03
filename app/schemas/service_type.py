from pydantic import BaseModel

class ServiceTypeCreate(BaseModel):
    name: str
    duration_minutes: int
    requires_confirmation: bool = False
    active: bool = True


class ServiceTypeOut(BaseModel):
    id: int
    name: str
    duration_minutes: int
    requires_confirmation: bool
    active: bool

    class Config:
        from_attributes = True
