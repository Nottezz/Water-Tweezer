from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from water_tweezer.core import crud
from water_tweezer.core.database import get_async_session
from water_tweezer.core.models.auth import CurrentUser
from water_tweezer.core.models.statistics import (
    DayStatsResponse,
    IntakeRequest,
    IntakeResponse,
    TodayStatsResponse,
)
from water_tweezer.web_app.security import get_current_user

router = APIRouter(prefix="/stats", tags=["User statistics"])


@router.get("/today", response_model=TodayStatsResponse)
async def get_today_user_stats(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> TodayStatsResponse:
    user_settings = await crud.get_user(session=db, telegram_id=user.id)
    if not user_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    consumed = await crud.get_daily_intake(session=db, user_id=user.id)
    entries = await crud.get_today_entries(session=db, user_id=user.id)

    return TodayStatsResponse(
        consumed_ml=consumed,
        goal_ml=user_settings.daily_goal,
        entries=[
            {
                "id": e.id,
                "amount_ml": e.amount_ml,
                "recorded_at": e.recorded_at.isoformat(),
            }
            for e in entries
        ],
    )


@router.get("/week", response_model=list[DayStatsResponse])
async def get_week_user_stats(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> list[DayStatsResponse]:
    user_settings = await crud.get_user(session=db, telegram_id=user.id)
    if not user_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    rows = await crud.get_weekly_intake(session=db, user_id=user.id)
    return [
        DayStatsResponse(
            date=row[0], consumed_ml=row[1], goal_ml=user_settings.daily_goal
        )
        for row in rows
    ]


@router.get("/month", response_model=list[DayStatsResponse])
async def get_month_user_stats(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> list[DayStatsResponse]:
    user_settings = await crud.get_user(session=db, telegram_id=user.id)
    if not user_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    rows = await crud.get_monthly_intake(session=db, user_id=user.id)
    return [
        DayStatsResponse(
            date=row[0], consumed_ml=row[1], goal_ml=user_settings.daily_goal
        )
        for row in rows
    ]


@router.post("/intake", response_model=IntakeResponse)
async def add_intake(
    payload: IntakeRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> IntakeResponse:
    entry = await crud.create_intake(
        session=db, user_id=user.id, amount_ml=payload.amount_ml
    )
    return IntakeResponse(
        id=entry.id,
        amount_ml=entry.amount_ml,
        recorded_at=entry.recorded_at,
    )
