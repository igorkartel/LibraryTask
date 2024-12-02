from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from configs.settings import settings

async_engine = create_async_engine(settings.db_url)

async_session_factory = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)
