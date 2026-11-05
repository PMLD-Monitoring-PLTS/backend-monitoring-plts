from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    String,
    func,
)

from app.core.database import Base


class AlertDeliveries(Base):
    __tablename__ = "alert_deliveries"

    id = Column(BigInteger, Identity(), primary_key=True)

    alert_log_id = Column(
        BigInteger,
        ForeignKey("alert_logs.id"),
        nullable=False,
    )

    telegram_user_id = Column(
        BigInteger,
        ForeignKey("telegram_users.id"),
        nullable=False,
    )

    status = Column(String(50), nullable=False)
    error_message = Column(String(255), nullable=True)

    attempted_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    delivered_at = Column(DateTime(timezone=True), nullable=True)
