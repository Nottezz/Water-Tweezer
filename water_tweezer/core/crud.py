from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models.intake import WaterIntake
from .models.reminder import Reminder
from .models.users import UserSettings
from .schemas import UserSettingsCreate, UserSettingsUpdate


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


async def create_reminder(
    session: AsyncSession, user_id: int, interval: int, tz: str
) -> Reminder:
    now = datetime.now(ZoneInfo(tz))

    next_run = now + timedelta(minutes=interval)

    reminder = Reminder(
        user_id=user_id,
        interval_minutes=interval,
        timezone=tz,
        next_run_at=next_run.astimezone(timezone.utc),
    )

    session.add(reminder)
    await session.commit()
    return reminder


async def get_due_reminders(session: AsyncSession) -> list[Reminder]:
    now = datetime.now(UTC)

    result = await session.execute(
        select(Reminder).where(  # type: ignore[call-arg]
            Reminder.is_active == True,
            Reminder.next_run_at <= now,
        )
    )
    return result.scalars().all()  # type: ignore


async def get_active_reminder(session: AsyncSession, user_id: int) -> Reminder | None:
    result = await session.scalars(
        select(Reminder).where(  # type: ignore
            Reminder.user_id == user_id,
            Reminder.is_active == True,
        )
    )
    return result.one_or_none()  # type: ignore


async def deactivate_user_reminders(session: AsyncSession, user_id: int) -> None:
    await session.execute(
        update(Reminder)  # type: ignore[arg-type]
        .where(Reminder.user_id == user_id, Reminder.is_active == True)  # type: ignore[call-arg]
        .values(is_active=False)
    )
    await session.commit()


async def create_intake(
    session: AsyncSession, user_id: int, amount_ml: int
) -> WaterIntake:
    intake = WaterIntake(
        user_id=user_id,
        amount_ml=amount_ml,
        recorded_at=datetime.now(UTC),
    )
    session.add(intake)
    await session.commit()
    return intake


async def get_daily_intake(session: AsyncSession, user_id: int) -> int:
    today = datetime.now(UTC).date()
    result = await session.execute(
        select(func.sum(WaterIntake.amount_ml)).where(
            WaterIntake.user_id == user_id,
            func.date(WaterIntake.recorded_at) == today,
        )
    )
    return result.scalar() or 0


async def get_weekly_intake(
    session: AsyncSession, user_id: int
) -> list[tuple[date, int]]:
    week_ago = datetime.now(UTC).date() - timedelta(days=7)
    result = await session.execute(
        select(
            func.date(WaterIntake.recorded_at).label("day"),
            func.sum(WaterIntake.amount_ml).label("total"),
        )
        .where(
            WaterIntake.user_id == user_id,
            func.date(WaterIntake.recorded_at) >= week_ago,
        )
        .group_by(func.date(WaterIntake.recorded_at))
        .order_by(func.date(WaterIntake.recorded_at))
    )
    return result.all()
