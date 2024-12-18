from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import HTMLResponse

from exception_handlers.auth_exc_handlers import TokenError
from exception_handlers.user_exc_handlers import UserAlreadyExists, UserDoesNotExist
from models import User
from schemas.auth_schemas import (
    Token,
    UserForgotPasswordSchema,
    UserResetPasswordSchema,
)
from schemas.user_schemas import UserCreateSchema
from usecases.auth_usecases import AuthUseCase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user(unit_test_user):
    user_data = UserCreateSchema(**unit_test_user)

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_username.return_value = None
    mock_user_repo.get_user_by_email.return_value = None
    mock_user_repo.create_user.return_value = User(id=1, **user_data.model_dump())

    auth_use_case = AuthUseCase(user_repository=mock_user_repo)

    result = await auth_use_case.create_user(user_data=user_data)

    assert result.id == 1
    assert result.username == unit_test_user["username"]

    mock_user_repo.get_user_by_username.assert_awaited_once()
    mock_user_repo.get_user_by_email.assert_awaited_once()
    mock_user_repo.create_user.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user_username_exists(unit_test_user):
    user_data = UserCreateSchema(**unit_test_user)

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_username.return_value = User(id=1, **user_data.model_dump())

    auth_use_case = AuthUseCase(user_repository=mock_user_repo)

    with pytest.raises(UserAlreadyExists):
        await auth_use_case.create_user(user_data=user_data)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_for_access_token(credentials, unit_test_user_in_db):
    with patch("usecases.auth_usecases.authenticate_user", new_callable=AsyncMock) as mock_authenticate_user:
        mock_authenticate_user.return_value = User(**unit_test_user_in_db)

        mock_user_repo = AsyncMock()

        auth_use_case = AuthUseCase(user_repository=mock_user_repo)

        result = await auth_use_case.login_for_access_token(db=AsyncMock(), credentials=credentials)

        assert isinstance(result, Token)
        assert hasattr(result, "access_token")
        assert hasattr(result, "refresh_token")
        assert result.token_type == "bearer"

        mock_authenticate_user.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_for_access_token_invalid_credentials(credentials):
    with patch("usecases.auth_usecases.authenticate_user", new_callable=AsyncMock) as mock_authenticate_user:
        mock_authenticate_user.return_value = False

        mock_user_repo = AsyncMock()

        auth_use_case = AuthUseCase(user_repository=mock_user_repo)

        with pytest.raises(HTTPException):
            await auth_use_case.login_for_access_token(db=AsyncMock(), credentials=credentials)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_access_token(refresh_token, unit_test_user_in_db):
    with (
        patch(
            "usecases.auth_usecases.is_refresh_token_blacklisted", new_callable=AsyncMock
        ) as mock_is_refresh_token_blacklisted,
        patch("usecases.auth_usecases.get_user", new_callable=AsyncMock) as mock_get_user,
        patch(
            "usecases.auth_usecases.add_refresh_token_to_blacklist", new_callable=AsyncMock
        ) as mock_add_refresh_token_to_blacklist,
    ):
        mock_is_refresh_token_blacklisted.return_value = 0
        mock_get_user.return_value = User(**unit_test_user_in_db)
        mock_add_refresh_token_to_blacklist.return_value = True

        mock_db = AsyncMock()
        mock_redis = AsyncMock()
        mock_user_repo = AsyncMock()

        auth_use_case = AuthUseCase(user_repository=mock_user_repo)

        result = await auth_use_case.refresh_access_token(
            refresh_token=refresh_token, db=mock_db, redis=mock_redis
        )

        assert isinstance(result, Token)
        assert hasattr(result, "access_token")
        assert hasattr(result, "refresh_token")
        assert result.token_type == "bearer"

        mock_is_refresh_token_blacklisted.assert_awaited_once()
        mock_get_user.assert_awaited_once()
        mock_add_refresh_token_to_blacklist.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_access_token_is_blacklisted(refresh_token, unit_test_user_in_db):
    with patch(
        "usecases.auth_usecases.is_refresh_token_blacklisted", new_callable=AsyncMock
    ) as mock_is_refresh_token_blacklisted:
        mock_is_refresh_token_blacklisted.return_value = 1

        mock_db = AsyncMock()
        mock_redis = AsyncMock()
        mock_user_repo = AsyncMock()

        auth_use_case = AuthUseCase(user_repository=mock_user_repo)

        with pytest.raises(TokenError):
            await auth_use_case.refresh_access_token(
                refresh_token=refresh_token, db=mock_db, redis=mock_redis
            )

        mock_is_refresh_token_blacklisted.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_forgot_password(unit_test_user_in_db):
    email = UserForgotPasswordSchema(email=unit_test_user_in_db["email"])

    with patch(
        "usecases.auth_usecases.send_message_to_rabbitmq", new_callable=AsyncMock
    ) as mock_send_message_to_rabbitmq:
        mock_send_message_to_rabbitmq.return_value = None

        mock_user_repo = AsyncMock()
        mock_user_repo.get_user_by_email.return_value = User(**unit_test_user_in_db)

        auth_use_case = AuthUseCase(user_repository=mock_user_repo)

        result = await auth_use_case.forgot_password(user_email=email)

        assert "reset_token" in result
        assert "message" in result

        mock_user_repo.get_user_by_email.assert_awaited_once()
        mock_send_message_to_rabbitmq.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_forgot_password_user_not_found(unit_test_user_in_db):
    email = UserForgotPasswordSchema(email=unit_test_user_in_db["email"])

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_email.return_value = None

    auth_use_case = AuthUseCase(user_repository=mock_user_repo)

    with pytest.raises(UserDoesNotExist):
        await auth_use_case.forgot_password(user_email=email)

    mock_user_repo.get_user_by_email.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_reset_password_template(reset_token):
    mock_user_repo = AsyncMock()

    auth_use_case = AuthUseCase(user_repository=mock_user_repo)

    result = await auth_use_case.get_reset_password_template(reset_token=reset_token)

    assert isinstance(result, HTMLResponse)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user_password(new_credentials):
    creds = UserResetPasswordSchema(**new_credentials)

    mock_user_repo = AsyncMock()
    mock_user_repo.update_user_password.return_value = {"message": "Your password was successfully changed"}

    auth_use_case = AuthUseCase(user_repository=mock_user_repo)

    result = await auth_use_case.update_user_password(new_credentials=creds)

    assert "message" in result
    mock_user_repo.update_user_password.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user_password_db_error(new_credentials):
    creds = UserResetPasswordSchema(**new_credentials)

    mock_user_repo = AsyncMock()
    mock_user_repo.update_user_password.side_effect = SQLAlchemyError("DB error")

    auth_use_case = AuthUseCase(user_repository=mock_user_repo)

    with pytest.raises(SQLAlchemyError):
        await auth_use_case.update_user_password(new_credentials=creds)

    mock_user_repo.update_user_password.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_logout(refresh_token):
    with patch(
        "usecases.auth_usecases.add_refresh_token_to_blacklist", new_callable=AsyncMock
    ) as mock_add_refresh_token_to_blacklist:
        mock_add_refresh_token_to_blacklist.return_value = True

        mock_redis = AsyncMock()
        mock_user_repo = AsyncMock()

        auth_use_case = AuthUseCase(user_repository=mock_user_repo)

        result = await auth_use_case.logout(refresh_token=refresh_token, redis=mock_redis)

        assert result.message == "Logout successful"

        mock_add_refresh_token_to_blacklist.assert_awaited_once()
