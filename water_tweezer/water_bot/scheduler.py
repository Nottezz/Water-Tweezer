from datetime import UTC, datetime, timedelta, timezone
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import select

from water_tweezer.core.crud import get_weekly_intake
from water_tweezer.core.models import UserSettings
from water_tweezer.core.models.reminder import Reminder
from water_tweezer.water_bot.keyboards.inline import water_intake_keyboard

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


async def send_weekly_reports(session_factory, bot) -> None:
    async with session_factory() as session:
        result = await session.scalars(select(UserSettings))
        users = result.all()

        for user in users:
            rows = await get_weekly_intake(session, user.id)

            if not rows:
                continue

            total = sum(r.total for r in rows)
            avg = total // 7
            best_day = max(rows, key=lambda r: r.total)
            goals_reached = sum(1 for r in rows if r.total >= user.daily_goal)

            text = f"""
📊 Недельный отчёт

💧 Всего выпито: {total} мл
📈 Среднее в день: {avg} мл
🏆 Лучший день: {best_day.day} — {best_day.total} мл
🎯 Дней с выполненной целью: {goals_reached} из 7
            """
            await bot.send_message(user.id, text)


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
