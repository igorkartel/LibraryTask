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


@pytest.fixture(scope="session")
def event_loop():
    # loop = asyncio.get_event_loop_policy().new_event_loop()
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
