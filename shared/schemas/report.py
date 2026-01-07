from datetime import datetime

from pydantic import BaseModel, Field

from shared.schemas.session import SessionNote, SessionSlot


class ReportData(BaseModel):
    session_id: str
    patient_id: str | None = None
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    reviewed_at: datetime | None = None
    confirmed_at: datetime | None = None
    slots: list[SessionSlot] = Field(default_factory=list)
    notes: list[SessionNote] = Field(default_factory=list)
