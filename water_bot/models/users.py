from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore

from .base import Base

if TYPE_CHECKING:
    from .reminder import Reminder


class UserSettings(Base):
    __tablename__ = "user_settings"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    daily_goal: Mapped[int] = mapped_column(Integer, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, nullable=False)
    timezone: Mapped[str] = mapped_column(String(255), nullable=False)

    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder",
        back_populates="user",
        cascade="all, delete-orphan",
    )
