import datetime
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from water_tweezer.core.models import Base, Reminder


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def make_reminder():
    def _make(
        user_id: int = 12345,
        interval_minutes: int = 60,
        start_hour: int = 8,
        end_hour: int = 22,
        timezone: str = "Europe/Moscow",
        is_active: bool = True,
    ) -> Reminder:
        reminder = Reminder()
        reminder.user_id = user_id
        reminder.interval_minutes = interval_minutes
        reminder.start_hour = start_hour
        reminder.end_hour = end_hour
        reminder.timezone = timezone
        reminder.is_active = is_active
        reminder.next_run_at = datetime.datetime.now(datetime.UTC)
        return reminder

    return _make
