from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TIMEZONE_OPTIONS = [
    ["Europe/Moscow", "Europe/Tallinn", "Europe/London"],
    ["Asia/Tokyo", "Asia/Shanghai", "Asia/Dubai"],
    ["America/New_York", "America/Los_Angeles", "America/Sao_Paulo"],
]
DAILY_GOAL_OPTIONS = [1500, 2000, 2500, 3000]
REMAINDER_TIMER = [30, 60, 80, 120]


def get_on_start_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="⚙️ Настроить напоминание")
    builder.adjust(1)
    return builder.as_markup(
        resize_keyboard=True,
    )


def build_yes_or_no_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Да")
    builder.button(text="Нет")
    return builder.as_markup(resize_keyboard=True)


def timezone_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for row in TIMEZONE_OPTIONS:
        builder.row(*[KeyboardButton(text=tz) for tz in row])

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def daily_goal_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for num in DAILY_GOAL_OPTIONS:
        builder.add(KeyboardButton(text=str(num)))
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def remainder_timer_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for num in REMAINDER_TIMER:
        builder.add(KeyboardButton(text=str(num)))
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
