import sqlite3
from datetime import date, timedelta
from unittest.mock import MagicMock, Mock
from uuid import UUID, uuid7

import pytest
from hobby_tracker.domain import Activity, DateRange
from hobby_tracker.exceptions import ActivityNotFound
from hobby_tracker.queries import ActivityQuery, ActivityStatisticsQuery
from hobby_tracker_infrastructure.persistence.sqliteDBs import ActivitySQLiteDB, queries


def test__row_to_activity(activity: Activity, activity_row: sqlite3.Row) -> None:
    assert activity == ActivitySQLiteDB._row_to_activity(activity_row)


def test_save(
    activity: Activity, mock_connection: Mock, activity_db: ActivitySQLiteDB
) -> None:
    activity_db.save(activity)

    mock_connection.execute.assert_called_once_with(
        queries.SAVE_ACTIVITY,
        (
            str(activity.id),
            str(activity.hobby_id),
            activity.started_at.isoformat(),
            activity.duration.total_seconds() // 60,
            activity.note,
        ),
    )
    mock_connection.commit.assert_called_once_with()


def test_get(
    activity_id: UUID,
    activity_row: MagicMock,
    activity: Activity,
    mock_connection: Mock,
    activity_db: ActivitySQLiteDB,
) -> None:
    execute_result = Mock()
    execute_result.fetchone.return_value = activity_row

    mock_connection.execute.return_value = execute_result

    assert activity_db.get(activity_id) == activity
    mock_connection.execute.assert_called_once_with(
        queries.GET_ACTIVITY, (str(activity_id),)
    )
    execute_result.fetchone.assert_called_once_with()


def test_get_none(
    activity_id: UUID, mock_connection: Mock, activity_db: ActivitySQLiteDB
) -> None:

    execute_result = Mock()
    execute_result.fetchone.return_value = None

    mock_connection.execute.return_value = execute_result

    with pytest.raises(ActivityNotFound, match=str(activity_id)):
        activity_db.get(activity_id)


def test_get_many_without_filters(
    activity: Activity,
    activity_row: MagicMock,
    mock_connection: Mock,
    activity_db: ActivitySQLiteDB,
) -> None:
    execute_result = Mock()
    execute_result.__iter__ = Mock(return_value=iter([activity_row]))
    mock_connection.execute.return_value = execute_result

    result = list(
        activity_db.get_many(
            ActivityQuery(
                hobby_ids=None,
                date_range=None,
            )
        )
    )

    assert result == [activity]

    mock_connection.execute.assert_called_once_with(
        queries.GET_ACTIVITIES,
        [],
    )


def test_get_many_by_hobby_ids(
    activity: Activity,
    activity_row: MagicMock,
    mock_connection: Mock,
    activity_db: ActivitySQLiteDB,
) -> None:
    execute_result = Mock()
    execute_result.__iter__ = Mock(return_value=iter([activity_row]))
    mock_connection.execute.return_value = execute_result

    hobby_ids = [activity.hobby_id, uuid7()]

    result = list(
        activity_db.get_many(
            ActivityQuery(
                hobby_ids=hobby_ids,
                date_range=None,
            )
        )
    )

    assert result == [activity]

    mock_connection.execute.assert_called_once_with(
        (queries.GET_ACTIVITIES + " WHERE hobby_id IN (?, ?)"),
        [str(hobby_ids[0]), str(hobby_ids[1])],
    )


def test_get_many_by_date_range(
    activity: Activity,
    activity_row: MagicMock,
    mock_connection: Mock,
    activity_db: ActivitySQLiteDB,
) -> None:
    execute_result = Mock()
    execute_result.__iter__ = Mock(return_value=iter([activity_row]))
    mock_connection.execute.return_value = execute_result

    date_range = DateRange(
        start=date(2026, 8, 1),
        end=date(2026, 8, 9),
    )

    result = list(
        activity_db.get_many(
            ActivityQuery(
                hobby_ids=None,
                date_range=date_range,
            )
        )
    )

    assert result == [activity]

    mock_connection.execute.assert_called_once_with(
        (queries.GET_ACTIVITIES + " WHERE started_at >= ? AND started_at < ?"),
        [
            "2026-08-01T00:00:00+00:00",
            "2026-08-10T00:00:00+00:00",
        ],
    )


def test_get_many_by_hobby_ids_and_date_range(
    activity: Activity,
    activity_row: MagicMock,
    mock_connection: Mock,
    activity_db: ActivitySQLiteDB,
) -> None:
    execute_result = Mock()
    execute_result.__iter__ = Mock(return_value=iter([activity_row]))
    mock_connection.execute.return_value = execute_result

    hobby_ids = [activity.hobby_id, uuid7()]
    date_range = DateRange(
        start=date(2026, 8, 1),
        end=date(2026, 8, 9),
    )

    result = list(
        activity_db.get_many(
            ActivityQuery(
                hobby_ids=hobby_ids,
                date_range=date_range,
            )
        )
    )

    assert result == [activity]

    mock_connection.execute.assert_called_once_with(
        (
            queries.GET_ACTIVITIES + " WHERE hobby_id IN (?, ?) "
            "AND started_at >= ? AND started_at < ?"
        ),
        [
            str(hobby_ids[0]),
            str(hobby_ids[1]),
            "2026-08-01T00:00:00+00:00",
            "2026-08-10T00:00:00+00:00",
        ],
    )


def test_calculate_statistics(
    mock_connection: Mock,
    activity_db: ActivitySQLiteDB,
) -> None:
    execute_result = Mock()

    execute_result.fetchone.return_value = {
        "activity_count": 5,
        "total_duration": 300,
        "avg_duration": 60,
    }

    mock_connection.execute.return_value = execute_result

    date_range = DateRange(
        start=date(2026, 8, 1),
        end=date(2026, 8, 9),
    )

    result = activity_db.calculate_statistics(
        ActivityStatisticsQuery(
            date_range=date_range,
            hobby_ids=None,
        )
    )

    assert result.activity_count == 5
    assert result.total_duration == timedelta(minutes=300)
    assert result.avg_duration == timedelta(minutes=60)

    mock_connection.execute.assert_called_once_with(
        queries.GET_ACTIVITY_STATISTICS,
        [
            "2026-08-01T00:00:00+00:00",
            "2026-08-10T00:00:00+00:00",
        ],
    )

    execute_result.fetchone.assert_called_once_with()


def test_calculate_statistics_by_hobby_ids(
    activity: Activity,
    mock_connection: Mock,
    activity_db: ActivitySQLiteDB,
) -> None:
    execute_result = Mock()

    execute_result.fetchone.return_value = {
        "activity_count": 3,
        "total_duration": 180,
        "avg_duration": 60,
    }

    mock_connection.execute.return_value = execute_result

    other_hobby_id = uuid7()

    result = activity_db.calculate_statistics(
        ActivityStatisticsQuery(
            date_range=DateRange(
                start=date(2026, 8, 1),
                end=date(2026, 8, 9),
            ),
            hobby_ids=[activity.hobby_id, other_hobby_id],
        )
    )

    assert result.activity_count == 3
    assert result.total_duration == timedelta(minutes=180)
    assert result.avg_duration == timedelta(minutes=60)

    mock_connection.execute.assert_called_once_with(
        (queries.GET_ACTIVITY_STATISTICS + " AND hobby_id IN (?, ?)"),
        [
            "2026-08-01T00:00:00+00:00",
            "2026-08-10T00:00:00+00:00",
            str(activity.hobby_id),
            str(other_hobby_id),
        ],
    )

    execute_result.fetchone.assert_called_once_with()
