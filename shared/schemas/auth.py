from typing import Literal

from pydantic import BaseModel

Role = Literal["admin", "doctor", "reviewer"]


class LoginRequest(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: str
    username: str
    role: Role


class LoginResponse(BaseModel):
    user: User
    csrf_token: str
