from unittest.mock import AsyncMock, patch

import pytest

from water_bot.routers.callbacks.intake import handle_intake


@pytest.mark.asyncio
async def test_handle_intake_with_amount(async_session, monkeypatch) -> None:
    callback = AsyncMock()
    callback.data = "intake:250"
    callback.from_user.id = 12345
    callback.message.edit_text = AsyncMock()

    monkeypatch.setattr(
        "water_bot.routers.callbacks.intake.AsyncSessionLocal",
        lambda: async_session,
    )

    await handle_intake(callback)

    callback.message.edit_text.assert_called_once_with("Отлично, записал 250 мл! 💧")
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_intake_skip(async_session, monkeypatch) -> None:
    callback = AsyncMock()
    callback.data = "intake:0"
    callback.from_user.id = 12345
    callback.message.edit_text = AsyncMock()

    monkeypatch.setattr(
        "water_bot.routers.callbacks.intake.AsyncSessionLocal",
        lambda: async_session,
    )

    await handle_intake(callback)

    callback.message.edit_text.assert_called_once_with("Хорошо, напомню позже 👌")
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_handle_intake_no_user(async_session) -> None:
    callback = AsyncMock()
    callback.data = "intake:250"
    callback.from_user = None

    await handle_intake(callback)

    callback.message.edit_text.assert_not_called()
    callback.answer.assert_not_called()
