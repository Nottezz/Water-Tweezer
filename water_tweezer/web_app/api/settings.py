from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from water_tweezer.core import crud
from water_tweezer.core.database import get_async_session
from water_tweezer.core.models.auth import CurrentUser
from water_tweezer.core.schemas import UserSettingsRead, UserSettingsUpdate
from water_tweezer.web_app.security import get_current_user

router = APIRouter(prefix="/settings", tags=["User settings"])


@router.get("/", response_model=UserSettingsRead)
async def get_user_settings(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserSettingsRead:
    settings = await crud.get_user(session=db, telegram_id=user.id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserSettingsRead.model_validate(settings)


@router.put("/", response_model=UserSettingsRead)
async def update_user_settings(
    payload: UserSettingsUpdate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserSettingsRead:
    updated = await crud.update_user(
        session=db, telegram_id=user.id, user_update=payload
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserSettingsRead.model_validate(updated)
