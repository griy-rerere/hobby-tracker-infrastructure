import sqlite3
from unittest.mock import Mock, patch

from hobby_tracker_infrastructure.persistence.sqliteDBs import SQLiteDatabase


@patch("hobby_tracker_infrastructure.persistence.sqliteDBs.base.sqlite3.connect")
def test_init_connects_to_database(mock_connect: Mock) -> None:
    connection = Mock()
    mock_connect.return_value = connection

    path = "test.db"

    SQLiteDatabase(path)

    mock_connect.assert_called_once_with(path)
    assert connection.row_factory is sqlite3.Row


@patch("hobby_tracker_infrastructure.persistence.sqliteDBs.base.sqlite3.connect")
def test_close_closes_connection(mock_connect: Mock) -> None:
    connection = Mock()
    mock_connect.return_value = connection

    database = SQLiteDatabase("test.db")

    database.close()

    connection.close.assert_called_once_with()
