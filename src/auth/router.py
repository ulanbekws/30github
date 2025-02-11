from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from typing import Optional, Annotated

from sqlalchemy.sql.operators import all_op

from src.auth.schemas import User, USER_DATA

router = APIRouter()

SECRET_KEY = "dba749b064fa8502475b7bd8b31b81d2cb20a34fbfee762ba4ba9c09093c799a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_jwt_token(data: dict) -> str:
    return jwt.encode(payload=data, key=SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user(username: str) -> Optional[User]:
    if username in USER_DATA:
        user_data = USER_DATA[username]
        return User(**user_data)
    return None


@router.post("/token/")  # Login
def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_data_from_db = get_user(username=user_data.username)
    if user_data_from_db is None or user_data.password != user_data_from_db.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_jwt_token({"sub": user_data_from_db.username})}


@router.get("/admin/")
def get_admin_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(username=current_user)
    if user_data.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return {"message": "Welcome Admin!"}


@router.get("/user/")
def get_user_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(username=current_user)
    if user_data.role != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return {"message": "Welcome User!"}
