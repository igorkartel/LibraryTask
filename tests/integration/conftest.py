import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from configs.minio_s3 import minio_config
from configs.settings import settings
from dependencies.db_dependency import db_session
from dependencies.minio_s3_dependency import get_minio_s3_client, minio_aioboto3_session
from dependencies.redis_dependency import get_redis_connection
from main import app
from models import BaseModel
from models.user_role_enum import UserRoleEnum
from usecases.minio_s3_usecases import MinioS3UseCase


@pytest.fixture(scope="session")
def event_loop():
    # loop = asyncio.new_event_loop()
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Collecting this url: "postgresql+asyncpg://test_user:test_pass@test-db-postgresql:5432/test_db"
@pytest_asyncio.fixture(scope="session")
async def test_async_engine() -> AsyncEngine:
    engine = create_async_engine(
        settings.test_db_url, pool_pre_ping=True, future=True, echo=True, poolclass=NullPool
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database(test_async_engine):
    BaseModel.metadata.bind = test_async_engine
    async with test_async_engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.drop_all)
        await connection.run_sync(BaseModel.metadata.create_all)
        await connection.commit()
    yield


@pytest_asyncio.fixture(scope="session")
async def override_db_session(test_async_engine, prepare_database) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(bind=test_async_engine, autoflush=False, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.set.return_value = True
    redis_mock.exists.return_value = 0
    yield redis_mock


@pytest_asyncio.fixture(scope="session")
async def override_minio_s3_client():
    async with minio_aioboto3_session.client(
        service_name="s3",
        endpoint_url=settings.MINIO_URL,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        config=minio_config,
    ) as minio_s3_client:
        yield minio_s3_client


@pytest.fixture
def mock_minio_s3_usecase(override_minio_s3_client):
    mock_minio_usecase = AsyncMock(spec=MinioS3UseCase)
    mock_minio_usecase.ensure_bucket_exists = AsyncMock(return_value=False)
    mock_minio_usecase.create_bucket = AsyncMock(return_value=True)
    mock_minio_usecase.upload_file_and_get_presigned_url = AsyncMock(
        return_value=f"{settings.MINIO_URL_TO_OPEN_FILE}/minio-s3-bucket/test.jpg"
    )
    mock_minio_usecase.delete_file = AsyncMock(return_value=True)
    return mock_minio_usecase


@pytest_asyncio.fixture(scope="session")
async def async_client(
    override_db_session, mock_redis, override_minio_s3_client
) -> AsyncGenerator[AsyncClient, None]:
    async def _override_db_session():
        yield override_db_session

    async def _override_redis():
        yield mock_redis

    async def _override_minio_s3_client():
        yield override_minio_s3_client

    app.dependency_overrides[db_session] = _override_db_session
    app.dependency_overrides[get_redis_connection] = _override_redis
    app.dependency_overrides[get_minio_s3_client] = _override_minio_s3_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8004") as ac:
        yield ac


@pytest.fixture
def test_user():
    return dict(
        name="TestName",
        surname="TestSurname",
        username="test_user",
        password="test_password",
        email="test@example.com",
        role=UserRoleEnum.ADMIN.value,
    )


@pytest.fixture
def test_user_2():
    return dict(
        id=2,
        name="TestName2",
        surname="TestSurname2",
        username="test_user2",
        password="test_password2",
        email="test2@example.com",
        role=UserRoleEnum.LIBRARIAN.value,
    )


@pytest.fixture
def test_user_2_for_update():
    return dict(
        name="TestName2",
        surname="TestSurname2",
        username="test_user2",
        email="user2@example.com",
    )


@pytest.fixture
def test_user_3():
    return dict(
        id=3,
        name="TestName3",
        surname="TestSurname3",
        username="test_user3",
        password="test_password3",
        email="test3@example.com",
        role=UserRoleEnum.LIBRARIAN.value,
    )


@pytest.fixture
def test_user_3_for_update():
    return dict(
        name="TestName3",
        surname="TestSurname3",
        username="test_user3",
        email="test3@example.com",
        is_blocked=True,
    )


@pytest.fixture
def test_user_list_query_params():
    return dict(page=1, limit=30, sort_by="username", order_by="asc")


@pytest.fixture
def test_genre_list_query_params():
    return dict(page=1, limit=30, sort_by="name", order_by="asc")


@pytest.fixture
def test_author_list_query_params():
    return dict(page=1, limit=30, sort_by="surname", order_by="asc")


@pytest.fixture
def test_book_list_query_params():
    return dict(page=1, limit=30, sort_by="title_rus", order_by="asc")


@pytest.fixture
def mock_file():
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    return mock_file


@pytest.fixture
def test_author():
    return dict(id=1, name="Стивен", surname="Кинг", nationality="США")


@pytest.fixture
def test_book():
    return dict(
        id=1,
        title_rus="Книга",
        title_origin="Book",
        quantity=0,
        available_for_loan=0,
        created_by=None,
        updated_by=None,
    )


@pytest.fixture
def test_book_with_author_and_genre():
    return dict(
        id=2,
        title_rus="Война и мир",
        title_origin="Война и мир",
        quantity=0,
        available_for_loan=0,
        created_by=None,
        updated_by=None,
        authors_name="Лев",
        authors_surname="Толстой",
        authors_nationality="Россия",
        genre_name="Роман",
    )
