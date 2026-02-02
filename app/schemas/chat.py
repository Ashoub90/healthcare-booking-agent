from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    user_id: Optional[int]
    message: str


class ChatResponse(BaseModel):
    reply: str
