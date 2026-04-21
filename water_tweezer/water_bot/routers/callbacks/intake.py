from aiogram import F, Router, types

from water_tweezer.core import crud
from water_tweezer.core.database import AsyncSessionLocal

router = Router()


@router.callback_query(F.data.startswith("intake:"))
async def handle_intake(callback: types.CallbackQuery) -> None:
    amount = int(callback.data.split(":")[1])

    if callback.from_user is None:
        return
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        await crud.create_intake(session, user_id, amount)

    if amount == 0:
        text = "Хорошо, напомню позже 👌"
    else:
        text = f"Отлично, записал {amount} мл! 💧"

    await callback.message.edit_text(text)
    await callback.answer()
