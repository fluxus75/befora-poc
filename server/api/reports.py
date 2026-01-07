from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse

from server.auth.rbac import require_role
from server.auth.session import CurrentUser
from server.services.report_generator import build_report_data, build_report_html
from server.services.session_store import get_session_detail
from shared.schemas.report import ReportData
from shared.schemas.session import SessionDetail


router = APIRouter(prefix="/api/sessions", tags=["reports"])


def _ensure_access(detail: SessionDetail, current_user: CurrentUser) -> None:
    if current_user.role == "doctor":
        if not detail.assigned_doctor_id or detail.assigned_doctor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not assigned",
            )


@router.get("/{session_id}/report", response_model=ReportData)
def get_report(
    session_id: str,
    current_user: CurrentUser = Depends(require_role(["admin", "doctor", "reviewer"])),
) -> ReportData:
    detail = get_session_detail(session_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    _ensure_access(detail, current_user)
    return build_report_data(detail)


@router.get("/{session_id}/report/html")
def get_report_html(
    session_id: str,
    current_user: CurrentUser = Depends(require_role(["admin", "doctor", "reviewer"])),
) -> HTMLResponse:
    detail = get_session_detail(session_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    _ensure_access(detail, current_user)
    html = build_report_html(detail)
    return HTMLResponse(content=html)
