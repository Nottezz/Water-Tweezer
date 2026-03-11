from itertools import chain
from typing import Callable

import pytest
from aiogram.types import ReplyKeyboardMarkup

from water_bot.keyboards.reply import (
    DAILY_GOAL_OPTIONS,
    REMAINDER_TIMER,
    TIMEZONE_OPTIONS,
    build_yes_or_no_keyboard,
    daily_goal_keyboard,
    get_on_start_kb,
    remainder_timer_keyboard,
    timezone_keyboard,
)


def extract_buttons(keyboard: ReplyKeyboardMarkup) -> list[str]:
    return [button.text for row in keyboard.keyboard for button in row]


def test_get_on_start_kb() -> None:
    kb = get_on_start_kb()

    assert isinstance(kb, ReplyKeyboardMarkup)
    assert kb.resize_keyboard is True

    buttons = extract_buttons(kb)

    assert buttons == ["⚙️ Настроить напоминание"]


def test_yes_or_no_keyboard() -> None:
    kb = build_yes_or_no_keyboard()

    assert isinstance(kb, ReplyKeyboardMarkup)
    assert kb.resize_keyboard is True

    buttons = extract_buttons(kb)

    assert "Да" in buttons
    assert "Нет" in buttons
    assert len(buttons) == 2


@pytest.mark.parametrize(
    "keyboard_func,expected",
    [
        (daily_goal_keyboard, DAILY_GOAL_OPTIONS),
        (remainder_timer_keyboard, REMAINDER_TIMER),
        (timezone_keyboard, list(chain.from_iterable(TIMEZONE_OPTIONS))),
    ],
)
def test_numeric_keyboards(keyboard_func, expected: list[str]) -> None:  # type: ignore
    kb = keyboard_func()

    buttons = [button.text for row in kb.keyboard for button in row]

    assert buttons == [str(x) for x in expected]
