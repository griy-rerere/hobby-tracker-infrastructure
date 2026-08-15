from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Activity(Base):
    __tablename__ = "activity"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    hobby_id = mapped_column(ForeignKey("hobby.id"))

    started_at: Mapped[datetime]
    duration_minutes: Mapped[int]
    note: Mapped[Optional[str]] = mapped_column(String(500))
