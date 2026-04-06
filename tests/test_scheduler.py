from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from water_bot.scheduler import check_reminders, process_reminder, send_weekly_reports


@pytest.mark.asyncio
async def test_process_reminder_sends_message_within_hours(
    async_session, make_reminder
) -> None:
    bot = AsyncMock()
    reminder = make_reminder(start_hour=0, end_hour=23)

    await process_reminder(reminder, async_session, bot)

    bot.send_message.assert_called_once()
    assert bot.send_message.call_args[0][0] == 12345
    assert reminder.next_run_at is not None


@pytest.mark.asyncio
async def test_process_reminder_skips_outside_hours(
    async_session, make_reminder
) -> None:
    bot = AsyncMock()
    reminder = make_reminder(start_hour=0, end_hour=0)

    await process_reminder(reminder, async_session, bot)

    bot.send_message.assert_not_called()
    assert reminder.next_run_at > datetime.now(UTC)


@pytest.mark.asyncio
async def test_process_reminder_reschedules_next_day_if_interval_exceeds_end(
    async_session, make_reminder
) -> None:
    bot = AsyncMock()
    reminder = make_reminder(start_hour=0, end_hour=23, interval_minutes=600)

    await process_reminder(reminder, async_session, bot)

    bot.send_message.assert_called_once()
    next_run = reminder.next_run_at
    assert next_run > datetime.now(UTC) + timedelta(hours=1)


@pytest.mark.asyncio
async def test_check_reminders_calls_process_for_due(
    async_session, make_reminder
) -> None:
    bot = AsyncMock()

    reminder = make_reminder(start_hour=0, end_hour=23)
    reminder.next_run_at = datetime.now(UTC) - timedelta(minutes=1)
    async_session.add(reminder)
    await async_session.commit()

    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=async_session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    await check_reminders(session_factory, bot)

    bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_check_reminders_ignores_future(async_session, make_reminder) -> None:
    bot = AsyncMock()

    reminder = make_reminder(start_hour=0, end_hour=23)
    reminder.next_run_at = datetime.now(UTC) + timedelta(hours=1)
    async_session.add(reminder)
    await async_session.commit()

    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=async_session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    await check_reminders(session_factory, bot)

    bot.send_message.assert_not_called()


def make_user(user_id: int = 12345, daily_goal: int = 2000) -> SimpleNamespace:
    return SimpleNamespace(id=user_id, daily_goal=daily_goal)


def make_row(day: str, total: int) -> SimpleNamespace:
    return SimpleNamespace(day=day, total=total)


@pytest.mark.asyncio
async def test_send_weekly_reports_sends_message() -> None:
    bot = AsyncMock()
    user = make_user()
    rows = [
        make_row("2026-03-31", 1500),
        make_row("2026-04-01", 2200),
        make_row("2026-04-02", 1800),
    ]

    session = AsyncMock()
    session.scalars = AsyncMock(
        return_value=MagicMock(all=MagicMock(return_value=[user]))
    )

    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(
            "water_bot.scheduler.get_weekly_intake", AsyncMock(return_value=rows)
        )
        await send_weekly_reports(session_factory, bot)

    bot.send_message.assert_called_once()
    text = bot.send_message.call_args[0][1]
    assert "Недельный отчёт" in text
    assert "5500" in text
    assert "785" in text
    assert "2026-04-01" in text
    assert "1 из 7" in text


@pytest.mark.asyncio
async def test_send_weekly_reports_skips_user_without_intakes() -> None:
    bot = AsyncMock()
    user = make_user()

    session = AsyncMock()
    session.scalars = AsyncMock(
        return_value=MagicMock(all=MagicMock(return_value=[user]))
    )

    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("water_bot.scheduler.get_weekly_intake", AsyncMock(return_value=[]))
        await send_weekly_reports(session_factory, bot)

    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_weekly_reports_no_users() -> None:
    bot = AsyncMock()

    session = AsyncMock()
    session.scalars = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[])))

    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    await send_weekly_reports(session_factory, bot)

    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_weekly_reports_goals_reached_count() -> None:
    bot = AsyncMock()
    user = make_user(daily_goal=2000)
    rows = [
        make_row("2026-04-01", 2000),
        make_row("2026-04-02", 2500),
        make_row("2026-04-03", 1999),
    ]

    session = AsyncMock()
    session.scalars = AsyncMock(
        return_value=MagicMock(all=MagicMock(return_value=[user]))
    )

    session_factory = MagicMock()
    session_factory.return_value.__aenter__ = AsyncMock(return_value=session)
    session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(
            "water_bot.scheduler.get_weekly_intake", AsyncMock(return_value=rows)
        )
        await send_weekly_reports(session_factory, bot)

    text = bot.send_message.call_args[0][1]
    assert "2 из 7" in text
