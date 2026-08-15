from dataclasses import dataclass
from uuid import UUID

from hobby_tracker.domain import exceptions
from hobby_tracker.domain.hobby import Hobby, HobbyName
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from . import models


def hobby_mapper(hobby_model: models.Hobby) -> Hobby:
    name = object.__new__(HobbyName)
    object.__setattr__(name, "value", hobby_model.name)
    hobby = object.__new__(Hobby)
    object.__setattr__(hobby, "id", hobby_model.id)
    object.__setattr__(hobby, "name", name)
    return hobby


def rollback_hobby(hobby: Hobby, snapshot: Hobby) -> None:
    object.__setattr__(hobby, "id", snapshot.id)
    object.__setattr__(hobby, "name", snapshot.name)


class SqlalchemyHobbyRepository:
    @dataclass(frozen=True, slots=True)
    class Tracked:
        entity: Hobby
        model: models.Hobby

    def _create_model(self, hobby: Hobby) -> models.Hobby:
        return models.Hobby(id=hobby.id, name=hobby.name.value, user_id=self._user_id)

    def __init__(self, session: Session, user_id: UUID) -> None:
        self._session = session
        self._user_id = user_id
        self._tracked: dict[UUID, SqlalchemyHobbyRepository.Tracked] = {}
        self._dirty: dict[UUID, Hobby] = {}
        self._deleted: dict[UUID, SqlalchemyHobbyRepository.Tracked] = {}

    def add(self, hobby: Hobby) -> None:
        self._dirty[hobby.id] = hobby

    def get_by_id(self, id: UUID) -> Hobby:
        """
        Repository must track itself all the changes with loaded entities
        like Python list

        Raises:
            HobbyNotFound(id) if hobby not found
        """
        if id in self._deleted:
            raise exceptions.HobbyNotFound(id)
        if id in self._dirty:
            return self._dirty[id]
        if id in self._tracked:
            return self._tracked[id].entity

        stmt = select(models.Hobby).where(
            models.Hobby.id == id, models.Hobby.user_id == self._user_id
        )
        hobby_model = self._session.scalar(stmt)

        if hobby_model is None:
            raise exceptions.HobbyNotFound(id)

        hobby = hobby_mapper(hobby_model)
        self._tracked[id] = self.Tracked(entity=hobby, model=hobby_model)

        return hobby

    def exists(self, id: UUID) -> bool:
        if id in self._tracked or id in self._dirty:
            return True
        if id in self._deleted:
            return False

        stmt = select(
            exists().where(models.Hobby.id == id, models.Hobby.user_id == self._user_id)
        )
        return bool(self._session.scalar(stmt))

    def delete(self, hobby: Hobby) -> None:
        """
        Only tracking hobby is allowed to delete

        Raises:
            HobbyDeleteError if try to delete hobby not from Repository
        """
        if hobby.id in self._dirty:
            del self._dirty[hobby.id]
            return

        tracked_hobby = self._tracked.pop(hobby.id, None)
        if tracked_hobby is None:
            raise exceptions.HobbyDeleteError(f"{repr(hobby)} was not loaded from repo")

        self._deleted[hobby.id] = tracked_hobby

    def persist_changes(self) -> None:
        for tracked in self._tracked.values():
            tracked.model.id = tracked.entity.id
            tracked.model.name = tracked.entity.name.value

        for tracked in self._deleted.values():
            self._session.delete(tracked.model)
        self._deleted.clear()

        for hobby in self._dirty.values():
            model = self._create_model(hobby)
            self._session.add(model)
            self._tracked[hobby.id] = self.Tracked(entity=hobby, model=model)
        self._dirty.clear()

    def rollback_changes(self) -> None:
        self._tracked |= self._deleted

        for tracked in self._tracked.values():
            snapshot = hobby_mapper(tracked.model)
            rollback_hobby(tracked.entity, snapshot)

        self._deleted.clear()
        self._dirty.clear()

    def clear(self) -> None:
        self._tracked.clear()
        self._dirty.clear()
        self._deleted.clear()
