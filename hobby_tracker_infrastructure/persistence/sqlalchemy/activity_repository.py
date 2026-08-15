from dataclasses import dataclass
from uuid import UUID

from hobby_tracker.domain import exceptions
from hobby_tracker.domain.activity import (
    Activity,
)
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from . import models


class SqlalchemyActivityRepository:
    @dataclass(frozen=True, slots=True)
    class _Tracked:
        entity: Activity
        model: models.Activity

        def persist(self) -> None:
            self.model.started_at = self.entity.started_at.value
            self.model.duration_minutes = self.entity.duration.minutes
            self.model.note = (
                None if self.entity.note is None else self.entity.note.text
            )

        def rollback(self) -> None:
            snapshot = self.model.as_domain()
            object.__setattr__(self.entity, "_started_at", snapshot._started_at)
            object.__setattr__(self.entity, "_duration", snapshot._duration)
            object.__setattr__(self.entity, "_note", snapshot._note)

    @staticmethod
    def _create_model(activity: Activity) -> models.Activity:
        return models.Activity(
            id=activity.id,
            hobby_id=activity.hobby_id,
            started_at=activity.started_at.value,
            duration_minutes=activity.duration.minutes,
            note=None if activity.note is None else activity.note.text,
        )

    def __init__(self, session: Session, user_id: UUID) -> None:
        self._session = session
        self._user_id = user_id
        self._tracked: dict[UUID, SqlalchemyActivityRepository._Tracked] = {}
        self._dirty: dict[UUID, Activity] = {}
        self._deleted: dict[UUID, SqlalchemyActivityRepository._Tracked] = {}

    def add(self, activity: Activity) -> None:
        self._dirty[activity.id] = activity

    def get_by_id(self, id: UUID) -> Activity:
        """
        Repository must track itself all the changes with loaded entities
        like Python list

        Raises:
            ActivityNotFound(id) if activity not found
        """
        if id in self._deleted:
            raise exceptions.ActivityNotFound(id)
        if id in self._dirty:
            return self._dirty[id]
        if id in self._tracked:
            return self._tracked[id].entity

        stmt = select(models.Activity).where(
            models.Activity.id == id, models.Activity.hobby.user_id == self._user_id
        )
        activity_model = self._session.scalar(stmt)
        if activity_model is None:
            raise exceptions.ActivityNotFound(id)

        activity = activity_model.as_domain()
        self._tracked[id] = self._Tracked(entity=activity, model=activity_model)

        return activity

    def exists(self, id: UUID) -> bool:
        if id in self._tracked or id in self._dirty:
            return True
        if id in self._deleted:
            return False

        stmt = select(
            exists().where(
                models.Activity.id == id, models.Activity.hobby.user_id == self._user_id
            )
        )
        return bool(self._session.scalar(stmt))

    def delete(self, activity: Activity) -> None:
        """
        Only tracking activity is allowed to delete

        Raises:
            ActivityDeleteError if try to delete activity not from Repository
        """
        if activity.id in self._dirty:
            del self._dirty[activity.id]
            return

        tracked_activity = self._tracked.pop(activity.id, None)
        if tracked_activity is None:
            raise exceptions.ActivityDeleteError(
                f"{repr(activity)} was not loaded from repo"
            )

        self._deleted[activity.id] = tracked_activity

    def persist_changes(self) -> None:
        for tracked in self._tracked.values():
            tracked.persist()

        for tracked in self._deleted.values():
            self._session.delete(tracked.model)

        self._deleted.clear()

        for entity in self._dirty.values():
            model = self._create_model(entity)
            self._session.add(model)
            self._tracked[entity.id] = self._Tracked(entity=entity, model=model)

        self._dirty.clear()

    def rollback_changes(self) -> None:
        self._tracked |= self._deleted

        for tracked in self._tracked.values():
            tracked.rollback()

        self._deleted.clear()
        self._dirty.clear()

    def clear(self) -> None:
        self._tracked.clear()
        self._dirty.clear()
        self._deleted.clear()
