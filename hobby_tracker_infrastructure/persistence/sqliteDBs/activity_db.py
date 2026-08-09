import sqlite3
from datetime import datetime, time, timedelta, timezone
from typing import Iterable
from uuid import UUID

from hobby_tracker.domain import Activity, ActivityStatistics
from hobby_tracker.exceptions import ActivityNotFound
from hobby_tracker.queries import ActivityQuery, ActivityStatisticsQuery

from . import queries
from .base import SQLiteDatabase


class ActivitySQLiteDB(SQLiteDatabase):
    @staticmethod
    def _row_to_activity(row: sqlite3.Row) -> Activity:
        return Activity(
            id=UUID(row["id"]),
            hobby_id=UUID(row["hobby_id"]),
            duration=timedelta(minutes=row["duration"]),
            started_at=datetime.fromisoformat(row["started_at"]),
            note=row["note"],
        )

    def save(self, activity: Activity) -> None:
        self._connection.execute(
            queries.SAVE_ACTIVITY,
            (
                str(activity.id),
                str(activity.hobby_id),
                activity.started_at.isoformat(),
                activity.duration.total_seconds() // 60,
                activity.note,
            ),
        )
        self._connection.commit()

    def get(self, id: UUID) -> Activity:
        row = self._connection.execute(
            queries.GET_ACTIVITY,
            (str(id),),
        ).fetchone()
        if row is None:
            raise ActivityNotFound(str(id))

        return self._row_to_activity(row)

    def get_many(self, query: ActivityQuery) -> Iterable[Activity]:
        conditions: list[str] = []
        parameters: list[object] = []

        if query.hobby_ids is not None:
            hobby_ids = list(query.hobby_ids)

            if hobby_ids:
                placeholders = ", ".join("?" for _ in hobby_ids)
                conditions.append(f"hobby_id IN ({placeholders})")
                parameters.extend(str(hobby_id) for hobby_id in hobby_ids)

        if query.date_range is not None:
            start = datetime.combine(
                query.date_range.start,
                time.min,
                tzinfo=timezone.utc,
            )
            end = datetime.combine(
                query.date_range.end + timedelta(days=1),
                time.min,
                tzinfo=timezone.utc,
            )

            conditions.append("started_at >= ?")
            parameters.append(start.isoformat())

            conditions.append("started_at < ?")
            parameters.append(end.isoformat())

        sql_query = queries.GET_ACTIVITIES

        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)

        return map(
            self._row_to_activity,
            self._connection.execute(sql_query, parameters),
        )

    def calculate_statistics(
        self, query: ActivityStatisticsQuery
    ) -> ActivityStatistics:
        start = datetime.combine(
            query.date_range.start,
            time.min,
            tzinfo=timezone.utc,
        )
        end = datetime.combine(
            query.date_range.end + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )
        parameters = [start.isoformat(), end.isoformat()]
        sql_query = queries.GET_ACTIVITY_STATISTICS

        if (query.hobby_ids is not None) and (hobby_ids := list(query.hobby_ids)):
            sql_query += f" AND hobby_id IN ({', '.join('?' for _ in hobby_ids)})"
            parameters.extend(str(hobby_id) for hobby_id in hobby_ids)

        row = self._connection.execute(sql_query, parameters).fetchone()

        return ActivityStatistics(
            activity_count=row["activity_count"],
            total_duration=timedelta(minutes=row["total_duration"]),
            avg_duration=timedelta(minutes=row["avg_duration"]),
        )
