from importlib.resources import files

_SQL = files(__name__)


def _load_query(name: str) -> str:
    return _SQL.joinpath(name).read_text(encoding="utf-8")


SAVE_HOBBY = _load_query("save_hobby.sql")

GET_HOBBY = _load_query("get_hobby.sql")

GET_ALL_HOBBIES = _load_query("get_all_hobbies.sql")


SAVE_ACTIVITY = _load_query("save_activity.sql")

GET_ACTIVITY = _load_query("get_activity.sql")

GET_ACTIVITIES = _load_query("get_activities.sql")

GET_ACTIVITY_STATISTICS = _load_query("get_activity_statistics.sql")
