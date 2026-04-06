from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from water_bot.scheduler import check_reminders, process_reminder


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
