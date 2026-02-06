# app/services/logging_service.py
from sqlalchemy.orm import Session
from typing import Optional
from app.db import models


def log_agent_action_service(
    patient_id: Optional[int],
    user_message: str,
    agent_action: str,
    system_decision: str,
    confidence_score: Optional[float],
    db: Session
) -> None:
    """
    Minimal audit logging.
    """

    log = models.AgentLog(
        patient_id=patient_id,
        user_message=user_message,
        agent_action=agent_action,
        system_decision=system_decision,
        confidence_score=confidence_score,
    )

    db.add(log)
    db.commit()
