from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from water_bot.models.users import UserSettings
from water_bot.schemas import UserSettingsCreate, UserSettingsUpdate


async def get_user(session: AsyncSession, telegram_id: int) -> UserSettings | None:
    result = await session.execute(
        select(UserSettings).where(UserSettings.id == telegram_id)
    )
    user: UserSettings | None = result.scalar_one_or_none()
    return user


async def create_user(session: AsyncSession, user: UserSettingsCreate) -> UserSettings:
    db_user = UserSettings(
        id=user.telegram_id,
        daily_goal=user.daily_goal,
        interval=user.interval,
        timezone=user.timezone,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user(
    session: AsyncSession, telegram_id: int, user_update: UserSettingsUpdate
) -> UserSettings | None:
    user = await get_user(session, telegram_id)

    if not user:
        return None

    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user
