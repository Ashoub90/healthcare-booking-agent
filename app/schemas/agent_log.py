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

# THIS IS THE ONE THAT WAS CAUSING THE 500 ERROR
class AgentLogOut(AgentLogBase): 
    id: int
    # Change 'created_at' to 'timestamp' to match what your terminal error was looking for
    created_at: datetime 

    class Config:
        from_attributes = True