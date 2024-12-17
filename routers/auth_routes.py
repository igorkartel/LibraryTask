import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from dependencies.db_dependency import db_session
from dependencies.redis_dependency import get_redis_connection
from dependencies.usecase_dependencies import get_auth_usecase
from schemas.auth_schemas import UserForgotPasswordSchema, UserResetPasswordSchema
from schemas.user_schemas import UserCreateSchema, UserReadSchema
from usecases.auth_usecases import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserReadSchema)
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
    return await usecase.login_for_access_token(db=db, credentials=credentials)


@router.post("/refresh-token")
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(db_session),
    redis: aioredis.Redis = Depends(get_redis_connection),
    usecase: AuthUseCase = Depends(get_auth_usecase),
):
    """Refreshes access token"""
    return await usecase.refresh_access_token(refresh_token=refresh_token, db=db, redis=redis)


@router.post("/forgot-password")
async def forgot_password(
    user_email: UserForgotPasswordSchema,
    usecase: AuthUseCase = Depends(get_auth_usecase),
):
    """Accepts the user’s email address, creates reset password token
    and publishes a message to RabbitMQ “reset-password-stream” queue"""
    return await usecase.forgot_password(user_email=user_email)


@router.get("/reset-password", response_class=HTMLResponse)
async def get_reset_password_template(
    reset_token: str = Query(..., alias="reset_token"),
    usecase: AuthUseCase = Depends(get_auth_usecase),
):
    """Checks reset password token, when user follows the reset link"""
    return await usecase.get_reset_password_template(reset_token=reset_token)


@router.post("/reset-password")
async def reset_password(
    new_credentials: UserResetPasswordSchema,
    usecase: AuthUseCase = Depends(get_auth_usecase),
):
    """Resets user's password checking refresh password token. Accepts new password and new password confirmation"""
    return await usecase.update_user_password(new_credentials=new_credentials)


# @router.post("/logout")
# async def logout(
#     refresh_token: str = Depends(oauth2_scheme),
#     redis: aioredis.Redis = Depends(get_redis_connection),
#     auth_usecase: AuthUseCase = Depends(get_auth_usecase),
# ):
#     """Logout of user by adding a refresh token into blacklist"""
#     return await auth_usecase.logout(refresh_token=refresh_token, redis=redis)
