from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import types
from aiogram.filters import BaseFilter


class IsPositiveInt(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        if message.text is None:
            return False

        try:
            return int(message.text) > 0  # type[ignore]
        except ValueError, TypeError:
            return False


class IsValidTimezone(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        try:
            ZoneInfo(message.text)
            return True
        except ZoneInfoNotFoundError, KeyError, ValueError:
            return False
