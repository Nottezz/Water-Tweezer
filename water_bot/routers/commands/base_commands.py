from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.utils import markdown

from water_bot import crud
from water_bot.database import AsyncSessionLocal
from water_bot.keyboards.reply import get_on_start_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message) -> None:
    text = """
👋 Привет! Я бот, который помогает не забывать пить воду.

Я могу:
💧 Напоминать пить воду в течение дня
📊 Собирать статистику потребления
🎯 Помогать достигать дневной цели

Чтобы начать, введите команду /settings, затем нажмите появившуюся кнопку ниже:
— сколько воды ты хочешь пить в день
— как часто присылать напоминания
- твоя тайм-зона

Напиши /help чтобы узнать доступные команды.
"""
    await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())


@router.message(Command("help"))
async def handle_help(message: types.Message) -> None:
    text = """
📌 Доступные команды:

/start — начать работу с ботом и настроить напоминания
/settings - посмотреть настройки
/help — показать список команд
/about — информация о боте

Как это работает:
1️⃣ Ты задаёшь дневную норму воды
2️⃣ Выбираешь интервал напоминаний
3️⃣ Бот присылает уведомления 💧
4️⃣ Ты отмечаешь, сколько воды выпил

Каждую неделю я покажу тебе статистику 📊
"""
    await message.answer(text=text)


@router.message(Command("about"))
async def handle_about(message: types.Message) -> None:
    text = """
ℹ️ О боте

Этот бот помогает формировать привычку регулярно пить воду.

Функции:
💧 Напоминания о воде
📊 Статистика потребления
🎯 Контроль дневной нормы

Автор: https://nottezz.ru
"""
    await message.answer(text=text)


@router.message(Command("settings"))
async def handle_settings(message: types.Message) -> None:

    if message.from_user is None:
        return

    telegram_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        user = await crud.get_user(session, telegram_id)
        if not user:
            await message.answer(
                text="Вы ещё не выполнили первоначальную настройку. Нажмите кнопку ниже для выполнения.",
                reply_markup=get_on_start_kb(),
            )
            return

    text = f"""
    Текущие настройки
- Дневная цель: {markdown.hbold(user.daily_goal)} мл
- Интервал напоминаний: {markdown.hbold(user.interval)} минут
- Тайм-зона: {markdown.hbold(user.timezone)}

Если вы хотите изменить настройки - кликните на кнопку ниже
    """
    await message.answer(
        text=text, reply_markup=get_on_start_kb(), parse_mode=ParseMode.HTML
    )
