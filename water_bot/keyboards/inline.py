from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

INTAKE_AMOUNTS = [150, 250, 350, 500]


def water_intake_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for ml in INTAKE_AMOUNTS:
        builder.button(text=f"💧 {ml} мл", callback_data=f"intake:{ml}")

    builder.button(text="❌ Пропустить", callback_data="intake:0")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def settings_keyboard(has_active_reminder: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if has_active_reminder:
        builder.button(text="⚙️ Изменить настройки", callback_data="reminder:edit")
        builder.button(text="🗑 Удалить напоминание", callback_data="reminder:delete")
    else:
        builder.button(text="➕ Создать напоминание", callback_data="reminder:create")
    builder.adjust(1)
    return builder.as_markup()
