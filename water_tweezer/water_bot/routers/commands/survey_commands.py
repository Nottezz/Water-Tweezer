from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown

from water_tweezer.core import crud
from water_tweezer.core.database import AsyncSessionLocal
from water_tweezer.core.schemas import UserSettingsCreate, UserSettingsUpdate
from water_tweezer.water_bot.filters import IsPositiveInt, IsValidTimezone
from water_tweezer.water_bot.keyboards.reply import (
    build_yes_or_no_keyboard,
    daily_goal_keyboard,
    remainder_timer_keyboard,
    timezone_keyboard,
)
from water_tweezer.water_bot.survey_states import WaterSurvey

router = Router(name=__name__)


@router.message(F.text == "⚙️ Настроить напоминание")
async def start_setup(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Сколько воды вы хотите пить в день? (в мл)\nВы можете выбрать, кликнув на кнопку или ввести своё число",
        reply_markup=daily_goal_keyboard(),
    )
    await state.set_state(WaterSurvey.daily_goal)


@router.message(WaterSurvey.daily_goal, IsPositiveInt())
async def set_daily_goal(message: types.Message, state: FSMContext) -> None:
    text = message.text
    if text is None:
        return

    goal = int(text)
    await state.update_data(daily_goal=goal)
    await message.answer(
        "Как часто напоминать пить воду? (в минутах)\nВы можете выбрать, кликнув на кнопку или ввести своё число",
        reply_markup=remainder_timer_keyboard(),
    )
    await state.set_state(WaterSurvey.reminder_interval)


@router.message(WaterSurvey.reminder_interval, IsPositiveInt())
async def set_interval(message: types.Message, state: FSMContext) -> None:
    text = message.text
    if text is None:
        return

    interval = int(text)
    await state.update_data(interval=interval)
    await message.answer(
        "В какой временной зоне вы находитесь?",
        reply_markup=timezone_keyboard(),
    )
    await state.set_state(WaterSurvey.user_timezone)


@router.message(WaterSurvey.user_timezone, IsValidTimezone())
async def set_user_timezone_and_clean_state(
    message: types.Message, state: FSMContext
) -> None:
    user_timezone = message.text
    await state.update_data(user_timezone=user_timezone)
    data = await state.get_data()

    await message.answer(
        f"""
Ваши настройки:\n
- Дневная цель: {markdown.hbold(data["daily_goal"])} мл
- Интервал напоминаний: {markdown.hbold(data["interval"])} минут
- Тайм-зона: {markdown.hbold(data["user_timezone"])}

Сохранить?
    """,
        reply_markup=build_yes_or_no_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(WaterSurvey.confirm_settings)


@router.message(WaterSurvey.confirm_settings, F.text.casefold() == "да")
async def set_user_settings_if_yes(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()

    if message.from_user is None:
        return

    telegram_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        existing_user = await crud.get_user(session, telegram_id)
        if existing_user:
            await crud.update_user(
                session,
                telegram_id,
                UserSettingsUpdate(
                    daily_goal=data["daily_goal"],
                    interval=data["interval"],
                    timezone=data["user_timezone"],
                ),
            )
        else:
            await crud.create_user(
                session,
                UserSettingsCreate(
                    telegram_id=telegram_id,
                    daily_goal=data["daily_goal"],
                    interval=data["interval"],
                    timezone=data["user_timezone"],
                ),
            )
        await crud.deactivate_user_reminders(session, telegram_id)
        await crud.create_reminder(
            session=session,
            user_id=telegram_id,
            interval=data["interval"],
            tz=data["user_timezone"],
        )

    await message.answer(
        text="✅ Настройки сохранены!\n\nЯ буду регулярно напоминать пить воду 💧",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.clear()


@router.message(WaterSurvey.confirm_settings, F.text.casefold() == "нет")
async def set_user_settings_if_no(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        text="Процесс настройки был прерван, начните заново, используя команду /start",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.clear()


@router.message(WaterSurvey.daily_goal)
async def invalid_daily_goal_value(message: types.Message) -> None:
    await message.answer("⚠️ Пожалуйста, введи число в мл, например 2000.")


@router.message(WaterSurvey.reminder_interval)
async def invalid_reminder_interval_value(message: types.Message) -> None:
    await message.answer("⚠️ Пожалуйста, введи число в минутах, например 60.")


@router.message(WaterSurvey.user_timezone)
async def invalid_user_timezone_value(message: types.Message) -> None:
    await message.answer("⚠️ Пожалуйста, выберите вашу тайм-зону.")


@router.message(WaterSurvey.confirm_settings)
async def invalid_confirming_settings_value(message: types.Message) -> None:
    await message.answer("⚠️ Пожалуйста, ответьте на вопрос: ДА или НЕТ.")
