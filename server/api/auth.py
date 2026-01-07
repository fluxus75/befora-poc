from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from server.auth.session import (
    SESSION_COOKIE_NAME,
    CurrentUser,
    get_current_user,
    require_csrf_token,
)
from server.services.auth_store import (
    create_auth_session,
    delete_auth_session,
    get_user_by_username,
    verify_password,
)
from shared.schemas.auth import LoginRequest, LoginResponse, User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response) -> LoginResponse:
    user = get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login",
        )
    token, csrf_token = create_auth_session(user["id"])
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return LoginResponse(
        user=User(id=user["id"], username=user["username"], role=user["role"]),
        csrf_token=csrf_token,
    )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    current_user: CurrentUser = Depends(require_csrf_token),
) -> dict:
    _ = current_user
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        delete_auth_session(token)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=User)
def me(current_user: CurrentUser = Depends(get_current_user)) -> User:
    return User(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
    )
