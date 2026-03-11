from types import SimpleNamespace

import pytest

from water_bot.filters import IsPositiveInt


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
