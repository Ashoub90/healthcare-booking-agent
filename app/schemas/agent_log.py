from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentLogCreate(BaseModel):
    patient_id: Optional[int]
    log_message: str
    agent_action: str
    system_decision: str
    confidence_score: Optional[float]  

class AgentLogOut(AgentLogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
