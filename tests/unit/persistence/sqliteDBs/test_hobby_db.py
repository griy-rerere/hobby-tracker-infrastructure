from unittest.mock import MagicMock, Mock

from hobby_tracker.domain import Hobby
from hobby_tracker_infrastructure.persistence.sqliteDBs import HobbySQLiteDB, queries


def test__row_to_hobby(
    hobby: Hobby,
    hobby_row: MagicMock,
) -> None:
    assert hobby == HobbySQLiteDB._row_to_hobby(hobby_row)


def test_save(
    hobby: Hobby,
    mock_connection: Mock,
    hobby_db: HobbySQLiteDB,
) -> None:
    hobby_db.save(hobby)

    mock_connection.execute.assert_called_once_with(
        queries.SAVE_HOBBY,
        (
            str(hobby.id),
            hobby.name,
        ),
    )
    mock_connection.commit.assert_called_once_with()


def test_get(
    hobby_id,
    hobby: Hobby,
    hobby_row: MagicMock,
    mock_connection: Mock,
    hobby_db: HobbySQLiteDB,
) -> None:
    execute_result = Mock()
    execute_result.fetchone.return_value = hobby_row

    mock_connection.execute.return_value = execute_result

    assert hobby_db.get(hobby_id) == hobby

    mock_connection.execute.assert_called_once_with(
        queries.GET_HOBBY,
        (str(hobby_id),),
    )
    execute_result.fetchone.assert_called_once_with()


def test_get_all(
    hobby: Hobby,
    hobby_row: MagicMock,
    mock_connection: Mock,
    hobby_db: HobbySQLiteDB,
) -> None:
    execute_result = MagicMock()
    execute_result.__iter__.return_value = iter([hobby_row])

    mock_connection.execute.return_value = execute_result

    result = list(hobby_db.get_all())

    assert result == [hobby]

    mock_connection.execute.assert_called_once_with(
        queries.GET_ALL_HOBBIES,
    )
