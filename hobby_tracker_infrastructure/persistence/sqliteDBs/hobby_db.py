import sqlite3
from typing import Iterable
from uuid import UUID

from hobby_tracker.domain import Hobby

from . import queries
from .base import SQLiteDatabase


class HobbySQLiteDB(SQLiteDatabase):
    @staticmethod
    def _row_to_hobby(row: sqlite3.Row) -> Hobby:
        return Hobby(
            id=UUID(row["id"]),
            name=row["name"],
        )

    def save(self, hobby: Hobby) -> None:
        self._connection.execute(
            queries.SAVE_HOBBY,
            (str(hobby.id), hobby.name),
        )
        self._connection.commit()

    def get(self, id: UUID) -> Hobby:
        row = self._connection.execute(
            queries.GET_HOBBY,
            (str(id),),
        ).fetchone()
        return self._row_to_hobby(row)

    def get_all(self) -> Iterable[Hobby]:
        return map(
            self._row_to_hobby,
            self._connection.execute(queries.GET_ALL_HOBBIES),
        )
