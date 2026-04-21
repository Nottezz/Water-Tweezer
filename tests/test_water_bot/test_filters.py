from types import SimpleNamespace

import pytest

from water_tweezer.water_bot.filters import IsPositiveInt, IsValidTimezone


@pytest.mark.parametrize(
    "text,result",
    [
        ("2000", True),
        ("0", False),
        ("-10", False),
        ("abc", False),
        ("", False),
    ],
)
@pytest.mark.asyncio
async def test_positive_int_filter(text: str, result: bool) -> None:
    message = SimpleNamespace(text=text)

    res = await IsPositiveInt()(message)  # type: ignore

    assert res == result


@pytest.mark.parametrize(
    "text,result",
    [
        ("Europe/Moscow", True),
        ("America/New_York", True),
        ("Asia/Tokyo", True),
        ("Invalid/Zone", False),
        ("abc", False),
        ("", False),
    ],
)
@pytest.mark.asyncio
async def test_valid_timezone_filter(text: str, result: bool) -> None:
    message = SimpleNamespace(text=text)

    res = await IsValidTimezone()(message)

    assert res == result
