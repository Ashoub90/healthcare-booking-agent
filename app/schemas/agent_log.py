from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AgentLogBase(BaseModel):
    patient_id: Optional[int] = None
    log_context: str
    agent_action: str
    system_decision: str
    confidence_score: Optional[float] = None

class AgentLogCreate(AgentLogBase):
    pass


class AgentLogOut(AgentLogBase): 
    id: int
    
    created_at: datetime 

    class Config:
        from_attributes = True