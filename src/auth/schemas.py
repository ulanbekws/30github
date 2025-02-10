from pydantic import BaseModel


class Token(BaseModel):
    token: str
    type: str


class User(BaseModel):
    username: str
    password: str

USER_DATA=[User(**{"username": "John", "password": "pass1"}),
           User(**{"username": "Katy", "password": "pass2"})]