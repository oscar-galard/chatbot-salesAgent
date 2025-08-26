from typing import Dict, Any, Optional
from ..domain.models import SessionData

class SessionStorage:
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def get_session(self, session_id: str) -> Optional[SessionData]:
        return self._sessions.get(session_id)

    def save_session(self, session: SessionData):
        self._sessions[session.session_id] = session

    def delete_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

# Singleton instance for in-memory storage
session_storage = SessionStorage()
