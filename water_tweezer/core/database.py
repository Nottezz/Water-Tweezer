from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine = create_async_engine(
    url=settings.database.database_url_asyncpg,
    echo=settings.database.echo,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
