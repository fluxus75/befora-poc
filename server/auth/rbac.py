from __future__ import annotations

from fastapi import Depends, HTTPException, status

from server.auth.session import CurrentUser, get_current_user


def require_role(allowed_roles: list[str]):
    def dependency(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not allowed",
            )
        return current_user

    return dependency
