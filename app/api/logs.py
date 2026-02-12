from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.logging_service import get_logs # Using the function we added
from app.schemas.agent_log import AgentLogOut

router = APIRouter()

@router.get("/", response_model=List[AgentLogOut])
def list_logs(
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Returns the recent audit logs for the admin dashboard using the AgentLogOut schema.
    """
    try:
        logs = get_logs(db=db, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")