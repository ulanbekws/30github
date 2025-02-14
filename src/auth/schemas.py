from typing import Optional
from pydantic import BaseModel
from enum import Enum


class User(BaseModel):
    username: str
    password: str
    role: str


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Permission(Enum):
    ADMIN = "create, read, update, delete"
    USER = "read, update"
    GUEST = "read"


class UserSchema(BaseModel):
    username: str
    password: str
    role: Role | None = None
    permission: Permission | None = None


class UserCreate(BaseModel):
    username: str
    email: str


class UserReturn(BaseModel):
    username: str
    email: str
    id: Optional[int] = None


USER_DATA=[User(**{"username": "admin", "password": "pass1", "role": "admin"}),
           User(**{"username": "user", "password": "pass2", "role": "user"})]