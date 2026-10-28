from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    Identity,
    String,
    UniqueConstraint,
    func,
)

from app.core.database import Base


class Thresholds(Base):
    __tablename__ = "thresholds"

    id = Column(BigInteger, Identity(), primary_key=True)

    metric = Column(String(100), nullable=False)
    level = Column(String(50), nullable=False)
    threshold_value = Column(Float, nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "metric",
            "level",
            name="uq_thresholds_metric_level",
        ),
    )
