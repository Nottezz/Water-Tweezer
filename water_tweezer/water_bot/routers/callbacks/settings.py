from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown

from water_tweezer.core import crud
from water_tweezer.core.database import AsyncSessionLocal
from water_tweezer.water_bot.keyboards.inline import settings_keyboard
from water_tweezer.water_bot.keyboards.reply import daily_goal_keyboard
from water_tweezer.water_bot.survey_states import WaterSurvey

router = Router()


@router.callback_query(F.data == "reminder:create")
async def handle_create_reminder(callback: types.CallbackQuery) -> None:
    if callback.from_user is None:
        return

    async with AsyncSessionLocal() as session:
        user = await crud.get_user(session, callback.from_user.id)
        await crud.create_reminder(
            session, callback.from_user.id, user.interval, user.timezone
        )

    text = f"""
✅ Напоминание создано!

Текущие настройки:
- Дневная цель: {markdown.hbold(user.daily_goal)} мл
- Интервал напоминаний: {markdown.hbold(user.interval)} минут
- Тайм-зона: {markdown.hbold(user.timezone)}
    """
    await callback.message.edit_text(
        text=text,
        reply_markup=settings_keyboard(has_active_reminder=True),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@router.callback_query(F.data == "reminder:edit")
async def handle_edit_reminder(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    await callback.message.answer(
        "Сколько воды вы хотите пить в день? (в мл)\nВы можете выбрать, кликнув на кнопку или ввести своё число",
        reply_markup=daily_goal_keyboard(),
    )
    await state.set_state(WaterSurvey.daily_goal)
    await callback.answer()


@router.callback_query(F.data == "reminder:delete")
async def handle_delete_reminder(callback: types.CallbackQuery) -> None:
    if callback.from_user is None:
        return

    async with AsyncSessionLocal() as session:
        await crud.deactivate_user_reminders(session, callback.from_user.id)

    await callback.message.edit_text(
        "🗑 Напоминание удалено.",
        reply_markup=settings_keyboard(has_active_reminder=False),
    )
    await callback.answer()
