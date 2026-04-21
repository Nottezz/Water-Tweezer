from unittest.mock import AsyncMock

import pytest

from water_tweezer.water_bot.keyboards.inline import settings_keyboard
from water_tweezer.water_bot.routers.callbacks.settings import (
    handle_create_reminder,
    handle_delete_reminder,
    handle_edit_reminder,
)
from water_tweezer.water_bot.survey_states import WaterSurvey


@pytest.mark.asyncio
async def test_handle_create_reminder(async_session, monkeypatch) -> None:
    callback = AsyncMock()
    callback.from_user.id = 12345

    class FakeUser:
        daily_goal = 2000
        interval = 60
        timezone = "Europe/Moscow"

    monkeypatch.setattr(
        "water_tweezer.water_bot.routers.callbacks.settings.AsyncSessionLocal",
        lambda: async_session,
    )
    monkeypatch.setattr(
        "water_tweezer.water_bot.routers.callbacks.settings.crud.get_user",
        AsyncMock(return_value=FakeUser()),
    )
    monkeypatch.setattr(
        "water_tweezer.water_bot.routers.callbacks.settings.crud.create_reminder",
        AsyncMock(),
    )

    await handle_create_reminder(callback)

    call_kwargs = callback.message.edit_text.call_args[1]
    assert "Напоминание создано" in call_kwargs["text"]
    assert "2000" in call_kwargs["text"]
    assert "60" in call_kwargs["text"]
    assert "Europe/Moscow" in call_kwargs["text"]
    assert call_kwargs["reply_markup"] == settings_keyboard(has_active_reminder=True)
    assert call_kwargs["parse_mode"] == "HTML"
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_create_reminder_no_user() -> None:
    callback = AsyncMock()
    callback.from_user = None

    await handle_create_reminder(callback)

    callback.message.edit_text.assert_not_called()
    callback.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_edit_reminder() -> None:
    callback = AsyncMock()
    state = AsyncMock()

    await handle_edit_reminder(callback, state)

    callback.message.answer.assert_called_once()
    sent_text = callback.message.answer.call_args[0][0]
    assert "Сколько воды вы хотите пить в день?" in sent_text
    state.set_state.assert_called_once_with(WaterSurvey.daily_goal)
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_delete_reminder(async_session, monkeypatch) -> None:
    callback = AsyncMock()
    callback.from_user.id = 12345

    monkeypatch.setattr(
        "water_tweezer.water_bot.routers.callbacks.settings.AsyncSessionLocal",
        lambda: async_session,
    )
    monkeypatch.setattr(
        "water_tweezer.water_bot.routers.callbacks.settings.crud.deactivate_user_reminders",
        AsyncMock(),
    )

    await handle_delete_reminder(callback)

    call_args = callback.message.edit_text.call_args
    assert "Напоминание удалено" in call_args[0][0]
    assert call_args[1]["reply_markup"] == settings_keyboard(has_active_reminder=False)
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_delete_reminder_no_user() -> None:
    callback = AsyncMock()
    callback.from_user = None

    await handle_delete_reminder(callback)

    callback.message.edit_text.assert_not_called()
    callback.answer.assert_not_called()
