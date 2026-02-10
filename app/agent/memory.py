from abc import ABC, abstractmethod
from typing import List, Dict
from sqlalchemy.orm import Session

from app.db import models


# =========================
# Abstract Memory Interface
# =========================

class MemoryStore(ABC):

    @abstractmethod
    def get(self, session_id: str) -> List[Dict[str, str]]:
        """Return list of messages for a session"""
        pass

    @abstractmethod
    def save(self, session_id: str, role: str, content: str) -> None:
        """Save a single message"""
        pass


# =========================
# In-Memory Implementation
# =========================

class InMemoryStore(MemoryStore):
    def __init__(self):
        self.data: Dict[str, List[Dict[str, str]]] = {}

    def get(self, session_id: str) -> List[Dict[str, str]]:
        return self.data.get(session_id, [])

    def save(self, session_id: str, role: str, content: str) -> None:
        self.data.setdefault(session_id, []).append({
            "role": role,
            "content": content
        })


# =========================
# Database Implementation
# =========================

class DBMemoryStore(MemoryStore):
    def __init__(self, db: Session):
        self.db = db

    def get(self, session_id: str) -> List[Dict[str, str]]:
        rows = (
            self.db.query(models.Conversation)
            .filter(models.Conversation.session_id == session_id)
            .order_by(models.Conversation.timestamp.asc())
            .all()
        )

        return [
            {"role": row.role, "content": row.content}
            for row in rows
        ]

    def save(self, session_id: str, role: str, content: str) -> None:
        msg = models.Conversation(
            session_id=session_id,
            role=role,
            content=content
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
