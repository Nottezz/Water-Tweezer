from unittest.mock import AsyncMock

import pytest

from water_bot.crud import get_user
from water_bot.keyboards.reply import TIMEZONE_OPTIONS
from water_bot.routers.commands.survey_commands import (
    set_daily_goal,
    set_interval,
    set_user_settings_if_yes,
    set_user_timezone_and_clean_state,
    start_setup,
)
from water_bot.survey_states import WaterSurvey


@pytest.mark.asyncio
async def test_start_setup_handler() -> None:
    message = AsyncMock()
    message.text = "⚙️ Настроить напоминание"
    state = AsyncMock()

    await start_setup(message, state)

    state.set_state.assert_called_once_with(WaterSurvey.daily_goal)

    message.answer.assert_called_once()
    sent_text = message.answer.call_args[0][0]
    assert "Сколько воды вы хотите пить в день?" in sent_text


@pytest.mark.asyncio
async def test_daily_goal_handler() -> None:
    message = AsyncMock()
    message.text = "1200"

    state = AsyncMock()

    await set_daily_goal(message, state)

    state.update_data.assert_called_once_with(daily_goal=1200)
    state.set_state.assert_called_once_with(WaterSurvey.reminder_interval)

    message.answer.assert_called_once()
    args, kwargs = message.answer.call_args
    assert "Как часто напоминать пить воду" in args[0]
    assert kwargs.get("reply_markup") is not None


@pytest.mark.asyncio
async def test_set_interval_handler() -> None:
    message = AsyncMock()
    message.text = "60"

    state = AsyncMock()

    await set_interval(message, state)

    state.update_data.assert_called_once_with(interval=60)
    state.set_state.assert_called_once()


@pytest.mark.asyncio
async def test_full_fsm_survey_flow(async_session, monkeypatch) -> None:
    state = AsyncMock()
    state.get_data = AsyncMock(
        return_value={
            "daily_goal": 2000,
            "interval": 60,
            "user_timezone": "Europe/Moscow",
        }
    )
    message = AsyncMock()
    message.from_user.id = 12345

    monkeypatch.setattr(
        "water_bot.routers.commands.survey_commands.AsyncSessionLocal",
        lambda: async_session,
    )

    message.text = "⚙️ Настроить напоминание"
    await start_setup(message, state)
    state.set_state.assert_called_with(WaterSurvey.daily_goal)

    message.text = "2000"
    await set_daily_goal(message, state)
    state.update_data.assert_called_with(daily_goal=2000)
    state.set_state.assert_called_with(WaterSurvey.reminder_interval)

    message.text = "60"
    await set_interval(message, state)
    state.update_data.assert_called_with(interval=60)
    state.set_state.assert_called_with(WaterSurvey.user_timezone)

    message.text = TIMEZONE_OPTIONS[0][0]  # "Europe/Moscow"
    await set_user_timezone_and_clean_state(message, state)
    state.update_data.assert_called_with(user_timezone="Europe/Moscow")
    state.set_state.assert_called_with(WaterSurvey.confirm_settings)

    message.text = "Да"
    await set_user_settings_if_yes(message, state)
    state.clear.assert_called_once()

    user = await get_user(async_session, 12345)
    assert user is not None
    assert user.daily_goal == 2000
    assert user.interval == 60
    assert user.timezone == "Europe/Moscow"
