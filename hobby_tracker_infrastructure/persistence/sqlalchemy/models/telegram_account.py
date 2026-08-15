from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User


class TelegramAccount(Base):
    __tablename__ = "telegram_account"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), unique=True)

    user: Mapped[User] = relationship()
