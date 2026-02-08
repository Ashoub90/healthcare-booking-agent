from typing import Dict, Any


class SessionStateStore:
    def __init__(self):
        self._state: Dict[str, Dict[str, Any]] = {}

    def get(self, session_id: str) -> Dict[str, Any]:
        return self._state.get(session_id, {})

    def set(self, session_id: str, state: Dict[str, Any]) -> None:
        self._state[session_id] = state

    def clear(self, session_id: str) -> None:
        self._state.pop(session_id, None)


state_store_instance = SessionStateStore()
