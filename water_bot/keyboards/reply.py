from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_on_start_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="⚙️ Настроить напоминания")
    builder.adjust(1)
    return builder.as_markup(
        resize_keyboard=True,
    )
