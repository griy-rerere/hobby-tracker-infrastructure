from typing import Any, Protocol, Self

from sqlalchemy.orm import Session


class Persistable(Protocol):
    def persist_changes(self) -> None: ...

    def rollback_changes(self) -> None: ...

    def clear_tracking(self) -> None: ...


class SqlalchemyUOW:
    def __init__(self, session: Session, *persistables: Persistable) -> None:
        self._session = session
        self._persistables = persistables
        self._active = False

    def begin(self) -> None:
        self._active = True
        self._session.begin()

    def __enter__(self) -> Self:
        self.begin()
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_val: Any,
        exc_tb: Any,
    ) -> bool:
        if self._active:
            self.rollback()

        return not exc_type

    def commit(self) -> None:
        for one in self._persistables:
            one.persist_changes()

        self._session.commit()

        for one in self._persistables:
            one.clear_tracking()

        self._active = False

    def rollback(self) -> None:
        self._session.rollback()

        for one in self._persistables:
            one.rollback_changes()
            one.clear_tracking()

        self._active = False
