from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from server.auth.rbac import require_role
from server.auth.session import CurrentUser, require_csrf_token
from server.services.session_store import (
    add_session_note,
    get_session_detail,
    list_sessions,
    set_session_status,
    update_session_assignment,
    upsert_session_slots,
)
from shared.schemas.session import (
    SessionDetail,
    SessionListResponse,
    SessionNote,
    SessionNoteCreate,
    SessionStatusUpdateRequest,
    SlotUpdateRequest,
)


router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _ensure_access(detail: SessionDetail, current_user: CurrentUser) -> None:
    if current_user.role == "doctor":
        if not detail.assigned_doctor_id or detail.assigned_doctor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not assigned",
            )


@router.get("", response_model=SessionListResponse)
def get_sessions(
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: CurrentUser = Depends(require_role(["admin", "doctor", "reviewer"])),
) -> SessionListResponse:
    assigned_doctor_id = current_user.id if current_user.role == "doctor" else None
    return list_sessions(
        page=page,
        page_size=page_size,
        status=status_filter,
        assigned_doctor_id=assigned_doctor_id,
    )


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: str,
    current_user: CurrentUser = Depends(require_role(["admin", "doctor", "reviewer"])),
) -> SessionDetail:
    detail = get_session_detail(session_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    _ensure_access(detail, current_user)
    return detail


@router.patch("/{session_id}/slots", response_model=SessionDetail)
def update_slots(
    session_id: str,
    payload: SlotUpdateRequest,
    current_user: CurrentUser = Depends(require_csrf_token),
) -> SessionDetail:
    if current_user.role not in {"admin", "doctor"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not allowed",
        )
    detail = get_session_detail(session_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    _ensure_access(detail, current_user)
    slot_map = {item.slot_key: item.slot_value for item in payload.slots}
    upsert_session_slots(session_id, slot_map)
    updated = get_session_detail(session_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return updated


@router.post("/{session_id}/notes", response_model=SessionNote)
def create_note(
    session_id: str,
    payload: SessionNoteCreate,
    current_user: CurrentUser = Depends(require_csrf_token),
) -> SessionNote:
    if current_user.role not in {"admin", "doctor"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not allowed",
        )
    detail = get_session_detail(session_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    _ensure_access(detail, current_user)
    return add_session_note(session_id, current_user.id, payload.note)


@router.patch("/{session_id}/status", response_model=SessionDetail)
def update_status(
    session_id: str,
    payload: SessionStatusUpdateRequest,
    current_user: CurrentUser = Depends(require_csrf_token),
) -> SessionDetail:
    detail = get_session_detail(session_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    _ensure_access(detail, current_user)
    if current_user.role == "doctor":
        if payload.status not in {"reviewed", "confirmed"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status",
            )
        if payload.status == "confirmed" and detail.status != "reviewed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session must be reviewed first",
            )
        set_session_status(session_id, payload.status)
    elif current_user.role == "admin":
        if payload.assigned_doctor_id:
            update_session_assignment(session_id, payload.assigned_doctor_id)
        if payload.status:
            set_session_status(session_id, payload.status)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not allowed",
        )
    updated = get_session_detail(session_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return updated
