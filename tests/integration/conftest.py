import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock

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

from configs.settings import settings
from dependencies.db_dependency import db_session
from dependencies.redis_dependency import get_redis_connection
from main import app
from models import BaseModel
from models.user_role_enum import UserRoleEnum


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
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
async def async_client(override_db_session, mock_redis) -> AsyncGenerator[AsyncClient, None]:
    async def _override_db_session():
        yield override_db_session

    async def _override_redis():
        yield mock_redis

    app.dependency_overrides[db_session] = _override_db_session
    app.dependency_overrides[get_redis_connection] = _override_redis

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


# @pytest.fixture
# def test_user_2():
#     return dict(
#         id="11f24558-197c-4c9a-a63f-8e134ae48c4c",
#         name="TestName2",
#         surname="TestSurname2",
#         username="test_user2",
#         password="test_password2",
#         phone_number="+375292223311",
#         email="test2@example.com",
#         role=UserRoleEnum.LIBRARIAN.value,
#         group_id="34f24558-197c-4c9a-a63f-8e134ae48c4c",
#     )
#
#
# @pytest.fixture
# def test_user_3():
#     return dict(
#         name="TestName3",
#         surname="TestSurname3",
#         username="test_user3",
#         password="test_password3",
#         phone_number="+375292223311",
#         email="test3@example.com",
#         role=RoleEnum.MODERATOR.value,
#         group_id="34f24558-197c-4c9a-a63f-8e134ae48c4c",
#     )
#
#
# @pytest.fixture
# def test_user_for_update():
#     return dict(
#         name="TestName2",
#         surname="TestSurname2",
#         username="test_user2",
#         phone_number="+375299998877",
#         email="test2@example.com",
#         image_s3_path=None,
#     )
#
#
# @pytest.fixture
# def test_user_for_update_2():
#     return dict(
#         name="TestName2",
#         surname="TestSurname2",
#         username="test_user2",
#         phone_number="+375299998877",
#         email="test2@example.com",
#         image_s3_path=None,
#         role=RoleEnum.USER.value,
#         group_id="34f24558-197c-4c9a-a63f-8e134ae48c4c",
#         is_blocked=True,
#     )
#
#
# @pytest_asyncio.fixture
# async def create_test_user_2(override_db_session, test_user_2):
#     user_data = UserCreateSchema(**test_user_2)
#     hashed_password = get_password_hash(user_data.password)
#     user_data.password = hashed_password
#     created_user = User(**user_data.dict())
#     async with override_db_session as db:
#         db.add(created_user)
#         await db.commit()
#         await db.refresh(created_user)
#         return created_user
#
#
# @pytest_asyncio.fixture
# async def create_test_user_3(override_db_session, test_user_3):
#     user_data = UserCreateSchema(**test_user_3)
#     hashed_password = get_password_hash(user_data.password)
#     user_data.password = hashed_password
#     created_user = User(**user_data.dict())
#     async with override_db_session as db:
#         db.add(created_user)
#         await db.commit()
#         await db.refresh(created_user)
#         return created_user
#
#
# @pytest_asyncio.fixture
# async def test_group(override_db_session):
#     group_data = {
#         "id": "34f24558-197c-4c9a-a63f-8e134ae48c4c",
#         "created_at": datetime.now(),
#         "modified_at": datetime.now(),
#         "name": "TestGroup",
#     }
#     created_group = Group(**group_data)
#     async with override_db_session as db:
#         db.add(created_group)
#         await db.commit()
#         await db.refresh(created_group)
#         return created_group
#
#
# @pytest.fixture
# def test_user_list_query_params():
#     return dict(page=1, limit=30, filter_by_name=None, sort_by="username", order_by="desc")
