from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, Form, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt

from src.auth.schemas import USER_DATA, User, Token

router = APIRouter()

SECRET_KEY = "dba749b064fa8502475b7bd8b31b81d2cb20a34fbfee762ba4ba9c09093c799a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def authenticate_user(username: str = Form(), password: str = Form()) -> User:
    for user in USER_DATA:
        if user.username == username and user.password == password:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)


async def create_jwt_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=1)
    }
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)


async def get_username_from_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Expired signature')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')


@router.post("/login")
async def login(user: Annotated[User | None, Depends(authenticate_user)]) -> Token:
    return Token(token=await create_jwt_token(user.username), type="bearer")


@router.get("/protected_resource")
async def protected_resource(username: User = Depends(get_username_from_token)):
    for user in USER_DATA:
        if username == user.username:
            return {"message": "Access granted"}
