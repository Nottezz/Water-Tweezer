from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import types
from aiogram.types import Message

from water_bot.keyboards.reply import get_on_start_kb
from water_bot.routers.commands import base_commands


@pytest.mark.asyncio
async def test_handle_start() -> None:
    message = AsyncMock()
    message.text = "/start"

    await base_commands.handle_start(message)

    message.answer.assert_called_once()

    kwargs = message.answer.call_args.kwargs
    text_sent = kwargs["text"]
    reply_markup = kwargs.get("reply_markup")

    assert "Привет" in text_sent
    assert "💧" in text_sent
    assert reply_markup == types.ReplyKeyboardRemove()


@pytest.mark.asyncio
async def test_handle_help() -> None:
    message = AsyncMock()
    message.text = "/help"

    await base_commands.handle_help(message)

    message.answer.assert_called_once()
    kwargs = message.answer.call_args.kwargs
    text_sent = kwargs["text"]

    assert "Доступные команды" in text_sent
    assert "/start" in text_sent
    assert "/help" in text_sent
    assert "/about" in text_sent


@pytest.mark.asyncio
async def test_handle_about() -> None:
    message = AsyncMock()
    message.text = "/about"

    await base_commands.handle_about(message)

    message.answer.assert_called_once()
    kwargs = message.answer.call_args.kwargs
    text_sent = kwargs["text"]

    assert "О боте" in text_sent
    assert "Автор: https://nottezz.ru" in text_sent
    assert "💧" in text_sent


@pytest.mark.asyncio
async def test_handle_settings_user_not_created() -> None:
    message = AsyncMock(spec=Message)
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    with patch("water_bot.crud.get_user", new=AsyncMock(return_value=None)):
        await base_commands.handle_settings(message)

    message.answer.assert_called_once()
    call_args = message.answer.call_args[1]
    assert "Вы ещё не выполнили первоначальную настройку" in call_args["text"]
    assert call_args["reply_markup"] == get_on_start_kb()


@pytest.mark.asyncio
async def test_handle_settings_user_exists() -> None:
    message = AsyncMock(spec=Message)
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    class FakeUser:
        daily_goal = 2000
        interval = 60
        timezone = "Europe/Moscow"

    with patch("water_bot.crud.get_user", new=AsyncMock(return_value=FakeUser())):
        with patch(
            "water_bot.crud.get_active_reminder",
            new=AsyncMock(return_value=MagicMock()),
        ):
            with patch(
                "water_bot.routers.commands.base_commands.markdown.hbold",
                side_effect=lambda x: f"**{x}**",
            ):
                await base_commands.handle_settings(message)

    message.answer.assert_called_once()
    text_sent = message.answer.call_args[1]["text"]
    assert "2000" in text_sent
    assert "60" in text_sent
    assert "Europe/Moscow" in text_sent
    assert message.answer.call_args[1]["parse_mode"] == "HTML"
