from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    token: str
    type: str


class User(BaseModel):
    username: str
    password: str
    role: Optional[str] = None


USER_DATA=[User(**{"username": "admin", "password": "pass1", "role": "admin"}),
           User(**{"username": "user", "password": "pass2", "role": "user"})]