from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Hobby(Base):
    __tablename__ = "hobby"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(String(50))

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_hobby_user_name"),)
