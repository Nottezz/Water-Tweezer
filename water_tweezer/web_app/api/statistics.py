from typing import Annotated

from core.database import get_async_session
from core.models.auth import CurrentUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from web_app.security import get_current_user

from water_tweezer.core import crud

router = APIRouter(prefix="/stats", tags=["User statistics"])


@router.get("/today")
async def get_today_user_stats(
    user_id: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> int:
    return await crud.get_daily_intake(session=db, user_id=user_id.id)


@router.get("/week")
async def get_week_user_stats(
    user_id: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> list:
    return await crud.get_weekly_intake(session=db, user_id=user_id.id)


@router.get("/month", deprecated=True)
async def get_month_user_stats(
    user_id: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    pass


@router.get("/history", deprecated=True)
async def get_history_user_stats(
    user_id: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    pass
