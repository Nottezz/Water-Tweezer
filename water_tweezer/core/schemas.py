from pydantic import BaseModel, ConfigDict, conint


class UserSettingsBase(BaseModel):
    telegram_id: int
    daily_goal: int
    interval: int
    timezone: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserSettingsCreate(UserSettingsBase):
    """
    UserSettingsCreate schema
    """


class UserSettingsRead(UserSettingsBase):
    """
    UserSettingsRead schema
    """


class UserSettingsUpdate(BaseModel):
    daily_goal: int | None = None
    interval: int | None = None
    timezone: str | None = None
