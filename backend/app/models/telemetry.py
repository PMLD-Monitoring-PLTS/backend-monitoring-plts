from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    Identity,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)

from app.core.database import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    # TimescaleDB: primary key menyertakan kolom waktu
    id = Column(BigInteger, Identity(), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    device_id = Column(String(100), nullable=False)

    load_voltage_panel = Column(Float)
    current_panel = Column(Float)
    power_panel = Column(Float)

    load_voltage_beban = Column(Float)
    current_beban = Column(Float)
    power_beban = Column(Float)

    load_voltage_baterai = Column(Float)
    current_baterai = Column(Float)
    power_baterai = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("id", "timestamp"),
        UniqueConstraint(
            "device_id",
            "timestamp",
            name="uq_telemetry_device_timestamp",
        ),
    )
