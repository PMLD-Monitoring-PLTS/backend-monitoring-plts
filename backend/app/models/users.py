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


class User(Base):
    __tablename__ = "users"

    id = Column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    email = Column(
        String(100),
        nullable=False,
    )

    # Simpan password yang sudah di-hash, bukan password asli
    password = Column(String(255), nullable=False)

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
            "email",
            name="uq_users_email",
        ),
    )
