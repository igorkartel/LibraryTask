from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.db_dependency import db_session
from repositories.user_repository import UserRepository
from usecases.auth_usecases import AuthUseCase
from usecases.user_usecases import UserUseCase


async def get_auth_usecase(db: AsyncSession = Depends(db_session)) -> AuthUseCase:
    user_repository = UserRepository(db)
    return AuthUseCase(user_repository)


async def get_user_usecase(db: AsyncSession = Depends(db_session)) -> UserUseCase:
    user_repository = UserRepository(db)
    return UserUseCase(user_repository)