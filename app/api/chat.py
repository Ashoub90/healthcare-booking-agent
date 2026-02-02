from fastapi import APIRouter
from app.schemas.chat import ChatMessage, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def post_chat(message: ChatMessage):
    """Placeholder endpoint for chat/assistant interactions."""
    return {"reply": "This is a placeholder reply."}
