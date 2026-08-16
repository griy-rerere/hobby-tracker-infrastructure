from datetime import datetime
from typing import Optional
from uuid import UUID

from hobby_tracker.domain.activity import Activity as DomainActivity
from hobby_tracker.domain.activity import ActivityDuration, ActivityNote, ActivityStart
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .hobby import Hobby


class Activity(Base):
    __tablename__ = "activity"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    hobby_id = mapped_column(ForeignKey("hobby.id"))

    started_at: Mapped[datetime]
    duration_minutes: Mapped[int]
    note: Mapped[Optional[str]] = mapped_column(String(500))

    hobby: Mapped[Hobby] = relationship()

    def as_domain(self) -> DomainActivity:
        start = object.__new__(ActivityStart)
        object.__setattr__(start, "value", self.started_at)

        duration = object.__new__(ActivityDuration)
        object.__setattr__(duration, "minutes", self.duration_minutes)

        if self.note is not None:
            note = object.__new__(ActivityNote)
            object.__setattr__(note, "text", self.note)

        else:
            note = None

        activity = object.__new__(DomainActivity)
        object.__setattr__(activity, "_id", self.id)
        object.__setattr__(activity, "_hobby_id", self.hobby_id)
        object.__setattr__(activity, "_started_at", start)
        object.__setattr__(activity, "_duration", duration)
        object.__setattr__(activity, "_note", note)

        return activity
