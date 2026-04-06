import asyncio
import logging
from typing import AsyncGenerator, Callable

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,  # type: ignore[import-not-found]
)
from sqlalchemy.ext.asyncio import AsyncSession

from water_bot.config import settings
from water_bot.database import AsyncSessionLocal
from water_bot.routers import router as main_router
from water_bot.scheduler import check_reminders


def setup_scheduler(
    bot: Bot,
    session_factory: Callable[[], AsyncGenerator[AsyncSession, None]],
) -> None:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_reminders,
        "interval",
        seconds=30,
        args=[session_factory, bot],
    )
    scheduler.start()


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.basicConfig(
        format=settings.logging.log_format,
        level=settings.logging.log_level,
        datefmt=settings.logging.log_date_format,
    )

    bot = Bot(token=settings.telegram_bot_token)

    setup_scheduler(bot, AsyncSessionLocal)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
