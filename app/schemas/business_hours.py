from pydantic import BaseModel
from datetime import time

class BusinessHourCreate(BaseModel):
    day_of_week: str
    open_time: time | None
    close_time: time | None
    is_closed: bool = False


class BusinessHourOut(BaseModel):
    id: int
    day_of_week: str
    open_time: time | None
    close_time: time | None
    is_closed: bool

    class Config:
        from_attributes = True
