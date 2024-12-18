import json
from datetime import datetime, timedelta

import jwt
import redis.asyncio as aioredis
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import HTMLResponse

from brokers.rabbitmq import send_message_to_rabbitmq
from brokers.redis import add_refresh_token_to_blacklist, is_refresh_token_blacklisted
from configs.logger import logger
from configs.settings import settings
from dependencies.auth_dependencies import (
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_reset_password_link,
    create_reset_password_token,
    get_password_hash,
    get_user,
)
from exception_handlers.auth_exc_handlers import TokenError
from exception_handlers.user_exc_handlers import UserAlreadyExists, UserDoesNotExist
from models import User
from repositories.user_repository import UserRepository
from schemas.auth_schemas import (
    LogoutSchema,
    Token,
    UserForgotPasswordSchema,
    UserResetPasswordSchema,
)
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
            }
        )
        refresh_token = create_refresh_token(
            data={
                "sub": user.username,
                "id": str(user.id),
                "role": str(user.role),
            }
        )

        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    async def refresh_access_token(
        self, refresh_token: str, db: AsyncSession, redis: aioredis.Redis
    ) -> Token:
        try:
            if await is_refresh_token_blacklisted(redis=redis, token=refresh_token):
                raise TokenError(message="Token is blacklisted")

            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            username: str = payload.get("sub")

            if username is None:
                raise TokenError(message="Invalid token")

            user = await get_user(username=username, db=db)

            access_token = create_access_token(
                data={"sub": user.username, "id": str(user.id), "role": str(user.role)}
            )
            new_refresh_token = create_refresh_token(
                data={"sub": user.username, "id": str(user.id), "role": str(user.role)}
            )
            refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

            await add_refresh_token_to_blacklist(
                redis=redis, token=refresh_token, expiration=int(refresh_token_expires.total_seconds())
            )

            return Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")

        except ExpiredSignatureError as exc:
            logger.error(str(exc))
            raise TokenError(message="Token expired")
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def forgot_password(self, user_email: UserForgotPasswordSchema):
        try:
            email = user_email.email
            user = await self.user_repository.get_user_by_email(email=email)

            if not user:
                raise UserDoesNotExist(
                    message=f"User with email '{email}' does not exist. Please check the correctness of email."
                )

            reset_token = create_reset_password_token(email=email)
            reset_password_link = create_reset_password_link(reset_token=reset_token)

            message_payload = {
                "user_id": str(user.id),
                "email": email,
                "subject": "Password Reset Link",
                "body": f"To reset your password, click on the following link: {reset_password_link}",
                "date_published": datetime.now().isoformat(),
                "date_sent": datetime.now().isoformat(),
            }

            message = json.dumps(message_payload)
            await send_message_to_rabbitmq(
                message=message, queue_name=settings.RABBITMQ_RESET_PASSWORD_QUEUE
            )

            return {"reset_token": reset_token, "message": "Request for password reset link has been sent"}

        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_reset_password_template(self, reset_token: str):
        try:
            payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")

            if email is None:
                raise TokenError(message="Invalid token")

            reset_password_form = f"""
                <html>
                    <head>
                        <title>Reset Password</title>
                    </head>
                    <body>
                        <h1>Reset Password</h1>
                        <form action="/auth/reset-password" method="post">
                            <input type="hidden" name="reset_token" value="{reset_token}" />
                            <label for="new_password">New Password:</label>
                            <input type="password" id="new_password" name="new_password" required minlength="8"/>
                            <br/>
                            <label for="confirm_new_password">Confirm New Password:</label>
                            <input type="password" id="confirm_new_password" name="confirm_new_password" required minlength="8"/>
                            <br/>
                            <button type="submit">Reset Password</button>
                        </form>
                    </body>
                </html>
                """

            return HTMLResponse(content=reset_password_form)

        except ExpiredSignatureError as exc:
            logger.error(str(exc))
            raise TokenError(message="Token expired")
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def update_user_password(self, new_credentials: UserResetPasswordSchema):
        try:
            payload = jwt.decode(new_credentials.reset_token, SECRET_KEY, algorithms=[ALGORITHM])
            email: EmailStr = payload.get("sub")

            if email is None:
                raise TokenError(message="Invalid token")

            new_password = new_credentials.new_password
            new_hashed_password = get_password_hash(new_password)

            return await self.user_repository.update_user_password(
                email=email, new_hashed_password=new_hashed_password
            )

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update password: {str(exc)}")
            raise SQLAlchemyError
        except ExpiredSignatureError as exc:
            logger.error(str(exc))
            raise TokenError(message="Token expired")
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def logout(self, refresh_token: str, redis: aioredis.Redis):
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")

            if not exp:
                raise TokenError(message="Invalid token")

            expiration = exp - int(datetime.now().timestamp())
            await add_refresh_token_to_blacklist(redis=redis, token=refresh_token, expiration=expiration)

            return LogoutSchema(message="Logout successful")

        except ExpiredSignatureError as exc:
            logger.error(str(exc))
            raise TokenError(message="Token expired")
        except Exception as exc:
            logger.error(str(exc))
            raise
