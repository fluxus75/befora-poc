from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from shared.schemas.session import SessionNote, SessionSlot


class ReportData(BaseModel):
    session_id: str
    patient_id: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    slots: list[SessionSlot] = Field(default_factory=list)
    notes: list[SessionNote] = Field(default_factory=list)
