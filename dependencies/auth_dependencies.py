from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from configs.logger import logger
from configs.settings import settings
from dependencies.db_dependency import db_session
from exception_handlers.auth_exc_handlers import PermissionDeniedError
from exception_handlers.user_exc_handlers import UserDoesNotExist
from repositories.user_repository import UserRepository
from schemas.auth_schemas import TokenData
from schemas.user_schemas import UserReadSchema
from usecases.user_usecases import UserUseCase

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def get_user(username: str, db: AsyncSession = Depends(db_session)):
    try:
        usecase = UserUseCase(user_repository=UserRepository(db))
        user = await usecase.get_user_by_username(username=username)

        if not user:
            raise UserDoesNotExist(message=f"User with username '{username}' does not exist")

        return user

    except Exception as exc:
        logger.error(str(exc))
        raise


async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(db_session)):
    user = await get_user(username=username, db=db)

    if not user:
        return False

    if not verify_password(plain_password=password, hashed_password=user.password):
        return False

    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(db_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate User's credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            logger.error("Could not validate User's credentials")
            raise credentials_exception

        token_data = TokenData(username=username)

    except PyJWTError as exc:
        logger.error(f"PyJWTError occurred: {str(exc)}")
        raise credentials_exception

    user = await get_user(username=token_data.username, db=db)

    if user is None:
        logger.error("Could not validate User's credentials")
        raise credentials_exception

    return user


async def get_current_active_user(current_user: UserReadSchema = Depends(get_current_user)):
    try:
        if current_user.is_blocked:
            raise PermissionDeniedError(message="User is blocked")

        return current_user

    except Exception as exc:
        logger.error(str(exc))
        raise


def create_reset_password_token(email: EmailStr):
    to_encode = {"sub": email}
    expire = datetime.now() + timedelta(minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_reset_password_link(reset_token: str):
    reset_password_link = f"{settings.RESET_PASSWORD_LINK}?reset_token={reset_token}"
    return reset_password_link
