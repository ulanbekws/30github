from typing import Annotated, Callable
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from secrets import token_urlsafe
from passlib.context import CryptContext
from databases import Database

from src.auth.schemas import Role, UserSchema, Permission, UserReturn, UserCreate

router = APIRouter()

DATABASE_URL = "postgresql://user:password@localhost/dbname"
database = Database(DATABASE_URL)

SECRET_KEY = token_urlsafe(16)
ALGORITHM = 'HS256'
EXPIRATION_TIME = timedelta(minutes=3)
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
USERS_DATA = {
    'admin': {'username': 'admin', 'password': pwd_context.hash('adminpass'), 'role': 'admin'},
    'user': {'username': 'user', 'password': pwd_context.hash('userpass'), 'role': 'user'},
    'guest': {'username': 'guest', 'password': pwd_context.hash('guestpass'), 'role': 'guest'},
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# Функция назначения разрешений при авторизации
def set_permission(user: UserSchema):
    if user.role == Role.ADMIN:
        user.permission = Permission.ADMIN
    elif user.role == Role.USER:
        user.permission = Permission.USER
    else:
        user.permission = Permission.GUEST
    return user


# Функция для создания JWT токена
def create_jwt_token(data: dict):
    data.update({'exp': datetime.now(timezone.utc) + EXPIRATION_TIME})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# Функция получения User'а по токену
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[
            ALGORITHM])
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'},
        )


# Функция для получения пользовательских данных на основе имени пользователя
def get_user(username: str):
    if username in USERS_DATA:
        user_data = USERS_DATA[username]
        return UserSchema(**user_data)
    return None


# Декоратор для проверки роли пользователя
def role_required(role: Role):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user: str = kwargs.get('current_user')
            user_data = get_user(current_user)
            if user_data.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized'
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Роут для получения JWT-токена (так работает логин)
@router.post('/token/')
# тут логинимся через форму
def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_data_from_db = get_user(user_data.username)
    if user_data_from_db is None or pwd_context.verify(user_data.password, user_data_from_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    set_permission(user_data_from_db)
    access_token = create_jwt_token({'sub': user_data_from_db.username})
    return {'access_token': access_token}


# Защищенный роут для админов, когда токен уже получен
@router.get('/admin/')
@role_required(Role.ADMIN)
def get_admin_info(current_user: str = Depends(get_user_from_token)):
    return {'message': 'Welcome Admin!'}


# Защищенный роут для обычных пользователей, когда токен уже получен
@router.get('/user/')
@role_required(Role.USER)
def get_user_info(current_user: str = Depends(get_user_from_token)):
    return {'message': 'Hello User!'}
# Защищенный роут для гостей, когда токен уже получен

@router.get('/guest/')
@role_required(Role.GUEST)
def get_guest_info(current_user: str = Depends(get_user_from_token)):
    return {'message': 'Nice to meet you Guest!'}


@router.on_event("startup")
async def startup_database():
    await database.connect()


@router.on_event("shutdown")
async def shutdown_database():
    await database.disconnect()


@router.post("/users/", response_model=UserReturn)
async def create_user(user: UserCreate):
    query = "INSERT INTO users (username, email) VALUES (:username, :email) RETURNING id"
    values = {"username": user.username, "email": user.email}
    try:
        user_id = await database.execute(query=query, values=values)
        return {**user.dict(), "id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/user/{user_id}/", response_model=UserReturn)
async def get_user(user_id: int):
    query = "SELECT * FROM users WHERE id = :user_id"
    values = {"user_id": user_id}
    try:
        result = await database.fetch_one(query=query, values=values)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user")
    if result:
        return UserReturn(username=result["username"], email=result["email"])
    else:
        raise HTTPException(status_code=404, detail="User not found")