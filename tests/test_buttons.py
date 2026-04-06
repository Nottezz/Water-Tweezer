from itertools import chain
from typing import Callable

import pytest
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from water_bot.keyboards.inline import (
    INTAKE_AMOUNTS,
    settings_keyboard,
    water_intake_keyboard,
)
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


def extract_inline_buttons(keyboard: InlineKeyboardMarkup) -> list[tuple[str, str]]:
    return [
        (button.text, button.callback_data)
        for row in keyboard.inline_keyboard
        for button in row
    ]


def test_water_intake_keyboard() -> None:
    kb = water_intake_keyboard()

    assert isinstance(kb, InlineKeyboardMarkup)

    buttons = extract_inline_buttons(kb)

    for ml in INTAKE_AMOUNTS:
        assert (f"💧 {ml} мл", f"intake:{ml}") in buttons

    assert ("❌ Пропустить", "intake:0") in buttons
    assert len(buttons) == len(INTAKE_AMOUNTS) + 1


def test_settings_keyboard_with_active_reminder() -> None:
    kb = settings_keyboard(has_active_reminder=True)

    assert isinstance(kb, InlineKeyboardMarkup)

    buttons = extract_inline_buttons(kb)

    assert ("⚙️ Изменить настройки", "reminder:edit") in buttons
    assert ("🗑 Удалить напоминание", "reminder:delete") in buttons
    assert len(buttons) == 2


def test_settings_keyboard_without_active_reminder() -> None:
    kb = settings_keyboard(has_active_reminder=False)

    assert isinstance(kb, InlineKeyboardMarkup)

    buttons = extract_inline_buttons(kb)

    assert ("➕ Создать напоминание", "reminder:create") in buttons
    assert len(buttons) == 1
