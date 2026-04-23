from pydantic import BaseModel, ConfigDict


class UserSettingsBase(BaseModel):
    daily_goal: int
    interval: int
    timezone: str

    model_config = ConfigDict(from_attributes=True)


class UserSettingsCreate(UserSettingsBase):
    telegram_id: int


class UserSettingsRead(UserSettingsBase):
    id: int


class UserSettingsUpdate(BaseModel):
    daily_goal: int | None = None
    interval: int | None = None
    timezone: str | None = None
