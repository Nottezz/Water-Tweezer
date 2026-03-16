from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore

from .base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    daily_goal: Mapped[int] = mapped_column(Integer, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, nullable=False)
    timezone: Mapped[str] = mapped_column(String(255), nullable=False)
