from datetime import UTC, datetime, timedelta, timezone
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import select

from water_bot.keyboards.inline import water_intake_keyboard
from water_bot.models.reminder import Reminder

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def process_reminder(reminder: Reminder, session: AsyncSession, bot) -> None:
    user_tz = ZoneInfo(reminder.timezone)
    now_user = datetime.now(user_tz)

    if not (reminder.start_hour <= now_user.hour < reminder.end_hour):
        next_time = now_user.replace(
            hour=reminder.start_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

        reminder.next_run_at = next_time.astimezone(timezone.utc)
        await session.commit()
        return

    await bot.send_message(
        reminder.user_id, "💧 Пора попить воды", reply_markup=water_intake_keyboard()
    )

    next_time = now_user + timedelta(minutes=reminder.interval_minutes)

    if next_time.hour >= reminder.end_hour:
        next_time = next_time.replace(
            hour=reminder.start_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

    reminder.next_run_at = next_time.astimezone(timezone.utc)
    await session.commit()


async def check_reminders(session_factory, bot) -> None:
    async with session_factory() as session:
        now = datetime.now(UTC)

        result = await session.scalars(
            select(Reminder).where(
                Reminder.is_active == True,
                Reminder.next_run_at <= now,
            )
        )

        reminders = result.all()

        for reminder in reminders:
            await process_reminder(reminder, session, bot)
