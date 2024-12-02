from configs.database import async_session_factory


async def db_session():
    async with async_session_factory() as session:
        yield session
