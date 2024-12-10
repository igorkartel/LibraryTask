from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.db_dependency import db_session
from dependencies.usecase_dependencies import get_auth_usecase
from schemas.user_schemas import UserCreateSchema, UserReadSchema
from usecases.auth_usecases import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/create-user", response_model=UserReadSchema)
async def create_new_user(user_data: UserCreateSchema, usecase: AuthUseCase = Depends(get_auth_usecase)):
    """Allows admin to create a new user profile for non-authenticated user"""
    return await usecase.create_user(user_data=user_data)


@router.post("/login")
async def login_for_access_token(
    db: AsyncSession = Depends(db_session),
    credentials: OAuth2PasswordRequestForm = Depends(),
    usecase: AuthUseCase = Depends(get_auth_usecase),
):
    """Authenticates a user using JWT"""
    return await usecase.login(db=db, credentials=credentials)
