from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from configs.logger import logger
from dependencies.auth_dependencies import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from exception_handlers.user_exc_handlers import UserAlreadyExists
from models import User
from repositories.user_repository import UserRepository
from schemas.auth_schemas import Token
from schemas.user_schemas import UserCreateSchema


class AuthUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_data: UserCreateSchema):
        try:
            existing_username = await self.user_repository.get_user_by_username(username=user_data.username)
            if existing_username:
                raise UserAlreadyExists(message=f"User with username '{user_data.username}' already exists")

            existing_email = await self.user_repository.get_user_by_email(email=user_data.email)
            if existing_email:
                raise UserAlreadyExists(message=f"User with email '{user_data.email}' already exists")

            hashed_password = get_password_hash(password=user_data.password)
            user_data.password = hashed_password

            new_user = User(**user_data.model_dump())

            return await self.user_repository.create_user(new_user=new_user)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to create user: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    @staticmethod
    async def login_for_access_token(
        self, db: AsyncSession, credentials: OAuth2PasswordRequestForm
    ) -> Token:
        user = await authenticate_user(username=credentials.username, password=credentials.password, db=db)
        if not user:
            logger.error("Incorrect username or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(
            data={
                "sub": user.username,
                "id": str(user.id),
                "role": str(user.role),
                "group_id": str(user.group.id),
            }
        )
        refresh_token = create_refresh_token(
            data={
                "sub": user.username,
                "id": str(user.id),
                "role": str(user.role),
                "group_id": str(user.group.id),
            }
        )
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
