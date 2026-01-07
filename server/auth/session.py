from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status

from server.services.auth_store import AuthSession, get_auth_session, get_user_by_id

SESSION_COOKIE_NAME = "dashboard_session"


@dataclass
class CurrentUser:
    id: str
    username: str
    role: str


def _get_session_token(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE_NAME)


def get_current_auth_session(
    request: Request,
) -> tuple[CurrentUser, AuthSession]:
    token = _get_session_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )
    session = get_auth_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )
    user = get_user_by_id(session.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    current_user = CurrentUser(
        id=user["id"],
        username=user["username"],
        role=user["role"],
    )
    return current_user, session


def get_current_user(
    auth: tuple[CurrentUser, AuthSession] = Depends(get_current_auth_session),
) -> CurrentUser:
    return auth[0]


def require_csrf_token(
    request: Request,
    auth: tuple[CurrentUser, AuthSession] = Depends(get_current_auth_session),
) -> CurrentUser:
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token or csrf_token != auth[1].csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )
    return auth[0]
