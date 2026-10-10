from datetime import datetime, timedelta
from uuid import UUID

from hobby_tracker.application.common import HobbyStats, Stats
from hobby_tracker.application.queries import (
    HobbyStatsQuery,
    HobbyStatsView,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Activity, Hobby


class SqlalchemyHobbyStatsHandler:
    def __init__(self, session: Session, user_id: UUID) -> None:
        self._session = session
        self._user_id = user_id

    def __call__(self, query: HobbyStatsQuery) -> HobbyStatsView:
        begin_dt = datetime.combine(query.date_from, datetime.min.time())
        end_dt = datetime.combine(
            query.date_to + timedelta(days=1),
            datetime.min.time(),
        )
        days = (query.date_to - query.date_from).days + 1

        stmt_hobby = (
            select(
                Hobby.id.label("hobby_id"),
                Hobby.name.label("hobby_name"),
                func.coalesce(
                    func.sum(Activity.duration_minutes) / 60.0,
                    0,
                ).label("total_hours"),
                func.coalesce(
                    func.count(Activity.id),
                    0,
                ).label("activities"),
            )
            .join(Activity, Activity.hobby_id == Hobby.id)
            .where(
                Hobby.user_id == self._user_id,
                Hobby.id == query.hobby_id,
                begin_dt <= Activity.started_at,
                Activity.started_at < end_dt,
            )
            .group_by(Hobby.id)
        )
        result = self._session.execute(stmt_hobby).mappings().one()
        view = HobbyStatsView(
            stats_chart=bytes(),
            stats=HobbyStats(
                hobby_id=result["hobby_id"],
                hobby_name=result["hobby_name"],
                stats=Stats(
                    total_hours=result["total_hours"],
                    activities=result["activities"],
                    hours_per_day=result["total_hours"] / days,
                ),
            ),
        )
        return view
