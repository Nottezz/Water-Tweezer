from unittest.mock import ANY, AsyncMock

import pytest

from water_bot.keyboards.reply import get_on_start_kb
from water_bot.routers.commands.base_commands import (
    handle_about,
    handle_help,
    handle_start,
)


@pytest.mark.asyncio
async def test_handle_start() -> None:
    message = AsyncMock()
    message.text = "/start"

    await handle_start(message)

    message.answer.assert_called_once()

    kwargs = message.answer.call_args.kwargs
    text_sent = kwargs["text"]
    reply_markup = kwargs.get("reply_markup")

    assert "Привет" in text_sent
    assert "💧" in text_sent
    assert reply_markup == get_on_start_kb()


@pytest.mark.asyncio
async def test_handle_help() -> None:
    message = AsyncMock()
    message.text = "/help"

    await handle_help(message)

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

    await handle_about(message)

    message.answer.assert_called_once()
    kwargs = message.answer.call_args.kwargs
    text_sent = kwargs["text"]

    assert "О боте" in text_sent
    assert "Автор: https://nottezz.ru" in text_sent
    assert "💧" in text_sent
