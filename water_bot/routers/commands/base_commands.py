from aiogram import Router, types
from aiogram.filters import Command, CommandStart

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

Чтобы начать, мне нужно выполнить настройку. Нажми кнопку ниже, я задам несколько вопросов:
— сколько воды ты хочешь пить в день
— как часто присылать напоминания
- твоя тайм-зона

Напиши /help чтобы узнать доступные команды.
"""
    await message.answer(text=text, reply_markup=get_on_start_kb())


@router.message(Command("help"))
async def handle_help(message: types.Message) -> None:
    text = """
📌 Доступные команды:

/start — начать работу с ботом и настроить напоминания
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
