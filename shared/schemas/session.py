from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    patient_id: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    status: str  # "active", "completed", "emergency_terminated"
    created_at: datetime


class SessionSlot(BaseModel):
    slot_key: str
    slot_value: Optional[str] = None


class SessionLogEntry(BaseModel):
    turn_index: int
    user_input: Optional[str] = None
    agent_response: Optional[str] = None
    timestamp: datetime


class SessionNote(BaseModel):
    id: int
    doctor_id: str
    note: str
    created_at: datetime


class SessionListItem(BaseModel):
    session_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    assigned_doctor_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None


class SessionDetail(SessionListItem):
    patient_id: Optional[str] = None
    slots: list[SessionSlot] = Field(default_factory=list)
    logs: list[SessionLogEntry] = Field(default_factory=list)
    notes: list[SessionNote] = Field(default_factory=list)


class SessionListResponse(BaseModel):
    items: list[SessionListItem]
    total: int
    page: int
    page_size: int


class SlotUpdateItem(BaseModel):
    slot_key: str
    slot_value: Optional[str] = None


class SlotUpdateRequest(BaseModel):
    slots: list[SlotUpdateItem]


class SessionNoteCreate(BaseModel):
    note: str


class SessionStatusUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_doctor_id: Optional[str] = None
