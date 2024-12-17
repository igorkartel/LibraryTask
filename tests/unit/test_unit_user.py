from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from exception_handlers.auth_exc_handlers import PermissionDeniedError
from models import User
from schemas.user_schemas import (
    UserAdminUpdateSchema,
    UserDeleteSchema,
    UserListQueryParams,
    UserReadSchema,
    UsersListSchema,
    UserUpdateSchema,
)
from usecases.user_usecases import UserUseCase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_by_id(unit_test_user_in_db):
    user_id = unit_test_user_in_db["id"]
    current_user = AsyncMock()
    current_user.role = "admin"

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_id.return_value = User(**unit_test_user_in_db)

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    result = await user_use_case.get_user_by_id(user_id=user_id, current_user=current_user)

    assert result.id == 1
    assert result.username == "test_user"

    mock_user_repo.get_user_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_by_id_no_permission(unit_test_user_in_db):
    user_id = unit_test_user_in_db["id"]
    current_user = AsyncMock()
    current_user.role = "librarian"

    mock_user_repo = AsyncMock()

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    with pytest.raises(PermissionDeniedError):
        await user_use_case.get_user_by_id(user_id=user_id, current_user=current_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_by_username(unit_test_user_in_db):
    username = unit_test_user_in_db["username"]

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_username.return_value = User(**unit_test_user_in_db)

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    result = await user_use_case.get_user_by_username(username=username)

    assert result.id == 1
    assert result.username == "test_user"

    mock_user_repo.get_user_by_username.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_by_username_db_error(unit_test_user_in_db):
    username = unit_test_user_in_db["username"]

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_username.side_effect = SQLAlchemyError("DB error")

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    with pytest.raises(SQLAlchemyError):
        await user_use_case.get_user_by_username(username=username)

    mock_user_repo.get_user_by_username.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_by_email(unit_test_user_in_db):
    email = unit_test_user_in_db["email"]

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_email.return_value = User(**unit_test_user_in_db)

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    result = await user_use_case.get_user_by_email(email=email)

    assert result.id == 1
    assert result.email == "test@example.com"

    mock_user_repo.get_user_by_email.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_by_email_db_error(unit_test_user_in_db):
    email = unit_test_user_in_db["email"]

    mock_user_repo = AsyncMock()
    mock_user_repo.get_user_by_email.side_effect = SQLAlchemyError("DB error")

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    with pytest.raises(SQLAlchemyError):
        await user_use_case.get_user_by_email(email=email)

    mock_user_repo.get_user_by_email.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_users(unit_test_user_in_db, unit_test_user_2_in_db):
    request_payload = UserListQueryParams()
    current_user = AsyncMock()
    current_user.role = "admin"

    mock_user_repo = AsyncMock()
    mock_user_repo.get_all_users.return_value = UsersListSchema(
        users=[UserReadSchema(**unit_test_user_in_db), UserReadSchema(**unit_test_user_2_in_db)]
    )

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    result = await user_use_case.get_all_users(request_payload=request_payload, current_user=current_user)

    assert len(result.users) == 2

    mock_user_repo.get_all_users.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_users_no_permission():
    request_payload = UserListQueryParams()
    current_user = AsyncMock()
    current_user.role = "librarian"

    mock_user_repo = AsyncMock()

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    with pytest.raises(PermissionDeniedError):
        await user_use_case.get_all_users(request_payload=request_payload, current_user=current_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user(unit_test_user_in_db):
    updated_data = UserUpdateSchema(email="new-test-email@example.com")
    current_user = AsyncMock()
    current_user.id = 1

    user_to_update = unit_test_user_in_db
    user_to_update["email"] = updated_data.email
    user_to_update["updated_at"] = datetime.now()

    mock_user_repo = AsyncMock()
    mock_user_repo.update_user.return_value = UserReadSchema(**user_to_update)

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    result = await user_use_case.update_user(updated_data=updated_data, current_user=current_user)

    assert result.email == updated_data.email

    mock_user_repo.update_user.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user_db_error(unit_test_user_in_db):
    updated_data = UserUpdateSchema(email="new-test-email@example.com")
    current_user = AsyncMock()
    current_user.id = 1

    user_to_update = unit_test_user_in_db
    user_to_update["email"] = updated_data.email
    user_to_update["updated_at"] = datetime.now()

    mock_user_repo = AsyncMock()
    mock_user_repo.update_user.side_effect = SQLAlchemyError("DB error")

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    with pytest.raises(SQLAlchemyError):
        await user_use_case.update_user(updated_data=updated_data, current_user=current_user)

    mock_user_repo.update_user.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user_by_admin(unit_test_user_2_in_db):
    updated_data = UserAdminUpdateSchema(email="new-test-email@example.com", is_blocked=True)
    current_user = AsyncMock()
    current_user.role = "admin"

    user_to_update = unit_test_user_2_in_db
    user_to_update["email"] = updated_data.email
    user_to_update["is_blocked"] = updated_data.is_blocked
    user_to_update["updated_at"] = datetime.now()

    mock_user_repo = AsyncMock()
    mock_user_repo.update_user_by_admin.return_value = UserReadSchema(**user_to_update)

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    result = await user_use_case.update_user_by_admin(
        user_id=unit_test_user_2_in_db["id"], updated_data=updated_data, current_user=current_user
    )

    assert result.email == updated_data.email
    assert result.is_blocked == updated_data.is_blocked

    mock_user_repo.update_user_by_admin.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user_by_admin_no_permission(unit_test_user_in_db):
    updated_data = UserAdminUpdateSchema(email="new-test-email@example.com", is_blocked=True)
    current_user = AsyncMock()
    current_user.role = "librarian"

    mock_user_repo = AsyncMock()

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    with pytest.raises(PermissionDeniedError):
        await user_use_case.update_user_by_admin(
            user_id=unit_test_user_in_db["id"], updated_data=updated_data, current_user=current_user
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_user(unit_test_user_2_in_db):
    user_id = unit_test_user_2_in_db["id"]
    current_user = AsyncMock()
    current_user.role = "admin"

    mock_user_repo = AsyncMock()
    mock_user_repo.delete_user.return_value = UserDeleteSchema(
        message=f"User with id {user_id} deleted successfully"
    )

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    result = await user_use_case.delete_user(user_id=user_id, current_user=current_user)

    assert result.message == f"User with id {user_id} deleted successfully"

    mock_user_repo.delete_user.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_user_no_permission(unit_test_user_in_db):
    user_id = unit_test_user_in_db["id"]
    current_user = AsyncMock()
    current_user.role = "librarian"

    mock_user_repo = AsyncMock()

    user_use_case = UserUseCase(user_repository=mock_user_repo)

    with pytest.raises(PermissionDeniedError):
        await user_use_case.delete_user(user_id=user_id, current_user=current_user)
