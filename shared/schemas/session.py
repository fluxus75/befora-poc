from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    patient_id: str | None = None


class SessionResponse(BaseModel):
    session_id: str
    status: str  # "active", "completed", "emergency_terminated"
    created_at: datetime


class SessionSlot(BaseModel):
    slot_key: str
    slot_value: str | None = None


class SessionLogEntry(BaseModel):
    turn_index: int
    user_input: str | None = None
    agent_response: str | None = None
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
    completed_at: datetime | None = None
    assigned_doctor_id: str | None = None
    reviewed_at: datetime | None = None
    confirmed_at: datetime | None = None


class SessionDetail(SessionListItem):
    patient_id: str | None = None
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
    slot_value: str | None = None


class SlotUpdateRequest(BaseModel):
    slots: list[SlotUpdateItem]


class SessionNoteCreate(BaseModel):
    note: str


class SessionStatusUpdateRequest(BaseModel):
    status: str | None = None
    assigned_doctor_id: str | None = None
