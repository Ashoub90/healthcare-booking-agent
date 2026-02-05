from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from app.db.session import get_db
from app.agent.agent_service import AgentService


router = APIRouter()


# =========================
# Request / Response Schemas
# =========================

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    data: Dict[str, Any] | None = None


# =========================
# Chat Endpoint
# =========================

@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint for the AI Booking Agent.
    """

    agent = AgentService(db)

    result = agent.handle_message(
        session_id=request.session_id,
        user_message=request.message
    )

    # result may contain extra data (patient, appointment, availability)
    reply = result.get("reply")
    data = {k: v for k, v in result.items() if k != "reply"}

    return ChatResponse(reply=reply, data=data if data else None)
