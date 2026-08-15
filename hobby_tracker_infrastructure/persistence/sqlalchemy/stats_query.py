from datetime import datetime, timedelta
from uuid import UUID

from hobby_tracker.application.queries import (
    HobbiesStatsQuery,
    HobbiesStatsView,
    HobbyStats,
    Stats,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Activity, Hobby


class SqlalchemyHobbiesStatsHandler:
    def __init__(self, session: Session, user_id: UUID) -> None:
        self._session = session
        self._user_id = user_id

    def __call__(self, query: HobbiesStatsQuery) -> HobbiesStatsView:
        begin_dt = datetime.combine(query.date_from, datetime.min.time())
        end_dt = datetime.combine(
            query.date_to + timedelta(days=1),
            datetime.min.time(),
        )
        days = (query.date_to - query.date_from).days + 1

        stmt_hobbies = (
            select(
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
                begin_dt <= Activity.started_at,
                Activity.started_at < end_dt,
            )
            .group_by(Hobby.id)
        )
        stmt_common = (
            select(
                func.coalesce(
                    func.sum(Activity.duration_minutes) / 60.0,
                    0,
                ).label("total_hours"),
                func.coalesce(
                    func.count(Activity.id),
                    0,
                ).label("activities"),
            )
            .join(Hobby, Activity.hobby_id == Hobby.id)
            .where(
                Hobby.user_id == self._user_id,
                begin_dt <= Activity.started_at,
                Activity.started_at < end_dt,
            )
        )
        result_hobbies = self._session.execute(stmt_hobbies).mappings()
        result_common = self._session.execute(stmt_common).mappings().one()

        view = HobbiesStatsView(
            hobbies_stats=(
                HobbyStats(
                    hobby_name=row["hobby_name"],
                    stats=Stats(
                        total_hours=row["total_hours"],
                        activities=row["activities"],
                        hours_per_day=row["total_hours"] / days,
                    ),
                )
                for row in result_hobbies
            ),
            common_stats=Stats(
                total_hours=result_common["total_hours"],
                activities=result_common["activities"],
                hours_per_day=result_common["total_hours"] / days,
            ),
        )
        return view
