import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {
        "message": "Hi!",
        "username": credentials.username,
        "password": credentials.password,
    }

usernames_to_passwords = {
    "admin": "admin",
    "john": "password",
}

static_auth_token_username = {
    "djjqlkjlkfjsjriklgs": "admin",
    "sjfldsajfdlsjfekjfl": "john",
}


def get_username_by_static_auth_token():
    pass


def get_auth_user_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    correct_password = usernames_to_passwords.get(credentials.username)

    if correct_password is None:
        raise unauthed_exc

    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        correct_password.encode("utf-8"),
    ):
        raise unauthed_exc

    return credentials.username


@router.get("/basic-auth-username/")
def demo_basic_auth_username(
        auth_username: str = Depends(get_auth_user_username),
):
    return {
        "message": f"Hi!, {auth_username}",
        "username": auth_username,
    }


@router.get("/some-http-header-auth/")
def demo_basic_auth_username(
        username: str = Depends(),
):
    return {
        "message": f"Hi!, {username}",
        "username": username,
    }
