from datetime import date, datetime

from pydantic import BaseModel


class TodayStatsResponse(BaseModel):
    consumed_ml: int
    goal_ml: int
    entries: list[dict]


class DayStatsResponse(BaseModel):
    date: date
    consumed_ml: int
    goal_ml: int


class IntakeRequest(BaseModel):
    amount_ml: int


class IntakeResponse(BaseModel):
    id: int
    amount_ml: int
    recorded_at: datetime
