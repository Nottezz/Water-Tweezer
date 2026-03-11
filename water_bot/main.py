import asyncio
import logging

from aiogram import Bot, Dispatcher

from water_bot.config import settings
from water_bot.routers import router as main_router


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.basicConfig(
        format=settings.logging.log_format,
        level=settings.logging.log_level,
        datefmt=settings.logging.log_date_format,
    )

    bot = Bot(token=settings.telegram_bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
