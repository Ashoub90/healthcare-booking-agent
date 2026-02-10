from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db import models

class SessionStateStore:
    def __init__(self):
        self._state: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        return self._state.get(session_id, {})

    def set(self, session_id: str, state: Dict[str, Any]) -> None:
        self._state[session_id] = state

    def clear(self, session_id: str) -> None:
        self._state.pop(session_id, None)


class DBSessionStateStore:
    def __init__(self, db: Session):
        self.db = db

    def get(self, session_id: str) -> Dict[str, Any]:
        """Fetch the JSON state from the DB. Returns empty dict if not found."""
        record = self.db.query(models.SessionState).filter(
            models.SessionState.session_id == session_id
        ).first()
        return record.data if record else {}

    def set(self, session_id: str, state: Dict[str, Any]) -> None:
        """
        Save the state to the DB. 
        Uses an 'upsert' so it creates a new row or updates the existing one.
        """
        # This is a 'PostgreSQL Upsert' - very efficient!
        stmt = insert(models.SessionState).values(
            session_id=session_id,
            data=state
        ).on_conflict_do_update(
            index_elements=['session_id'],
            set_=dict(data=state)
        )
        
        self.db.execute(stmt)
        self.db.commit()

    def clear(self, session_id: str) -> None:
        """Wipe the state for a specific session."""
        self.db.query(models.SessionState).filter(
            models.SessionState.session_id == session_id
        ).delete()
        self.db.commit()
