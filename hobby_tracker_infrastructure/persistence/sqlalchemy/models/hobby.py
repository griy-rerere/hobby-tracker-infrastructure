from uuid import UUID

from hobby_tracker.domain.hobby import Hobby as DomainHobby
from hobby_tracker.domain.hobby import HobbyName
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Hobby(Base):
    __tablename__ = "hobby"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(String(50))

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_hobby_user_name"),)

    def as_domain(self) -> DomainHobby:
        name = object.__new__(HobbyName)
        object.__setattr__(name, "value", self.name)

        entity = object.__new__(DomainHobby)
        object.__setattr__(entity, "_id", self.id)
        object.__setattr__(entity, "_name", name)

        return entity
