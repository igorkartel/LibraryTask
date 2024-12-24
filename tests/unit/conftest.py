from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.security import OAuth2PasswordRequestForm

from configs.settings import settings
from dependencies.auth_dependencies import get_password_hash
from models.user_role_enum import UserRoleEnum


@pytest.fixture
def unit_test_user():
    return dict(
        name="TestName",
        surname="TestSurname",
        username="test_user",
        password="test_password",
        email="test@example.com",
        role=UserRoleEnum.ADMIN.value,
    )


@pytest.fixture
def credentials():
    return OAuth2PasswordRequestForm(username="test_user", password="test_password")


@pytest.fixture
def unit_test_user_in_db():
    return dict(
        id=1,
        name="TestName",
        surname="TestSurname",
        username="test_user",
        password=get_password_hash("test_password"),
        email="test@example.com",
        role=UserRoleEnum.ADMIN.value,
        is_blocked=False,
    )


@pytest.fixture
def refresh_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJpZCI6IjEiLCJyb2xlIjoiVXNlclJvbGVFbnVtLkFETUlOIiwiZXhwIjo0MTAyNDQ0ODAwfQ.uRtDXTV1Cny_8QaDOCIRvBF18m7ZtcWCjVJDGuW7mHc"


@pytest.fixture
def reset_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjo0MTAyNDQ0ODAwfQ.fz32glwCguoWDdSFQc3UxRIHlPG_2FE2nrB9AuB0BDk"


@pytest.fixture
def new_credentials():
    return dict(
        reset_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjo0MTAyNDQ0ODAwfQ.fz32glwCguoWDdSFQc3UxRIHlPG_2FE2nrB9AuB0BDk",
        new_password="new_password",
        confirm_new_password="new_password",
    )


@pytest.fixture
def unit_test_user_2_in_db():
    return dict(
        id=2,
        name="TestName2",
        surname="TestSurname2",
        username="test_user2",
        password=get_password_hash("test_password2"),
        email="test2@example.com",
        role=UserRoleEnum.LIBRARIAN.value,
        is_blocked=False,
    )


@pytest.fixture
def unit_test_author():
    return dict(name="Стивен", surname="Кинг", nationality="США")


@pytest.fixture
def unit_test_author_in_db():
    return dict(
        id=1,
        name="Стивен",
        surname="Кинг",
        nationality="США",
        photo_s3_url=f"{settings.MINIO_URL_TO_OPEN_FILE}/minio-s3-bucket/test.jpg",
        created_at="2024-12-23 13:50:17.494935",
        updated_at="2024-12-23 14:00:50.788192",
        created_by="librarian",
        updated_by="admin",
    )


@pytest.fixture
def unit_mock_file():
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    return mock_file


@pytest.fixture
def unit_mock_minio_usecase():
    mock_minio_usecase = AsyncMock()
    mock_minio_usecase.ensure_bucket_exists.return_value = False
    mock_minio_usecase.create_bucket.return_value = True
    mock_minio_usecase.upload_file_and_get_presigned_url.return_value = (
        f"{settings.MINIO_URL_TO_OPEN_FILE}/minio-s3-bucket/test.jpg"
    )
    mock_minio_usecase.delete_file.return_value = None
    return mock_minio_usecase
