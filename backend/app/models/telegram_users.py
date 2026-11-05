from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Identity,
    String,
    UniqueConstraint,
    func,
)

from app.core.database import Base


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id = Column(BigInteger, Identity(), primary_key=True)

    chat_id = Column(BigInteger, nullable=False)
    username = Column(String(100), nullable=True)

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            name="uq_telegram_users_chat_id",
        ),
    )
