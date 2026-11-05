from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    Identity,
    String,
    func,
)

from app.core.database import Base


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(BigInteger, Identity(), primary_key=True)

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    level = Column(String(50), nullable=False)
    metric = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    message = Column(String(255), nullable=False)
