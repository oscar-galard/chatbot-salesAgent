from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class UserMessage(BaseModel):
    session_id: str = Field(..., description="ID único para la sesión de usuario.")
    message: str = Field(..., description="Mensaje del usuario.")

class BotResponse(BaseModel):
    session_id: str
    response: str
    phase: str
    data: Optional[Dict[str, Any]] = {}
