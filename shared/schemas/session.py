from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    patient_id: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    status: str  # "active", "completed", "emergency_terminated"
    created_at: datetime
