from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

# create_async_engine is lazy: no connection is opened until first use.
engine: AsyncEngine = create_async_engine(get_settings().database_url, pool_pre_ping=True)

# expire_on_commit=False keeps attributes loadable after commit, which an
# async session can't do (it can't lazily refresh outside an await).
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
