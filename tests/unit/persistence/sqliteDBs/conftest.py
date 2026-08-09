import sqlite3
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch
from uuid import UUID, uuid7

import pytest
from hobby_tracker.domain import Activity, Hobby
from hobby_tracker_infrastructure.persistence.sqliteDBs import (
    ActivitySQLiteDB,
    HobbySQLiteDB,
)


@pytest.fixture
def mock_connection() -> Mock:
    return Mock()


@pytest.fixture
def activity_id() -> UUID:
    return uuid7()


@pytest.fixture
def activity(activity_id: UUID) -> Activity:
    return Activity(
        id=activity_id,
        hobby_id=uuid7(),
        duration=timedelta(hours=1, minutes=30),
        started_at=datetime(2026, 8, 9),
        note="Writing tests",
    )


@pytest.fixture
def activity_row(activity: Activity) -> MagicMock:
    row = MagicMock(spec=sqlite3.Row)

    row.__getitem__.side_effect = {
        "id": str(activity.id),
        "hobby_id": str(activity.hobby_id),
        "duration": activity.duration.total_seconds() // 60,
        "started_at": activity.started_at.isoformat(),
        "note": activity.note,
    }.__getitem__
    return row


@pytest.fixture
def hobby_id() -> UUID:
    return uuid7()


@pytest.fixture
def hobby(hobby_id: UUID) -> Hobby:
    return Hobby(
        id=hobby_id,
        name="Drawing",
    )


@pytest.fixture
def hobby_row(hobby: Hobby) -> MagicMock:
    row = MagicMock(spec=sqlite3.Row)

    row.__getitem__.side_effect = {
        "id": str(hobby.id),
        "name": hobby.name,
    }.__getitem__

    return row


@pytest.fixture
def hobby_db(mock_connection: Mock) -> HobbySQLiteDB:
    with patch(
        "hobby_tracker_infrastructure.persistence.sqliteDBs.base.sqlite3.connect",
        return_value=mock_connection,
    ):
        yield HobbySQLiteDB("test.db")


@pytest.fixture
def activity_db(mock_connection: Mock) -> ActivitySQLiteDB:
    with patch(
        "hobby_tracker_infrastructure.persistence.sqliteDBs.base.sqlite3.connect",
        return_value=mock_connection,
    ):
        yield ActivitySQLiteDB("test.db")
