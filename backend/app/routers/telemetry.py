import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.models.telemetry import Telemetry
from app.schemas.telemetry import (
    ElectricalReading,
    IngestResponse,
    RealtimeData,
    RealtimeResponse,
    TelemetryIngestRequest,
)

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["Telemetry"],
)

# API Key yang valid (bisa diatur lewat .env atau default)
EXPECTED_DEVICE_KEY = os.getenv("DEVICE_API_KEY", "ESP8266_PLTS_SECRET_KEY")


def evaluate_system_status(voltage_baterai: float | None, current_baterai: float | None) -> str:
    """
    Evaluasi status sistem berdasarkan ambang batas baterai (sesuai API contract):
    - Critical : Tegangan <= 11.5 V atau Arus discharge <= -3000 mA
    - Warning  : Tegangan <= 12.0 V atau Arus discharge <= -1500 mA
    - Normal   : Selain kondisi di atas
    """
    if (voltage_baterai is not None and voltage_baterai <= 11.5) or (
        current_baterai is not None and current_baterai <= -3000
    ):
        return "critical"

    if (voltage_baterai is not None and voltage_baterai <= 12.0) or (
        current_baterai is not None and current_baterai <= -1500
    ):
        return "warning"

    return "normal"


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest data telemetry dari sensor/simulator",
)
def ingest_telemetry(
    payload: TelemetryIngestRequest,
    x_device_api_key: str = Header(..., alias="X-Device-API-Key"),
    db: Session = Depends(get_db),
):
    # 1. Validasi API Key perangkat
    if x_device_api_key != EXPECTED_DEVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akses ditolak. Kredensial tidak valid.",
        )

    # 2. Petakan payload JSON Pydantic ke SQLAlchemy Model
    telemetry_record = Telemetry(
        timestamp=payload.timestamp,
        device_id=payload.device_id,
        # Panel
        load_voltage_panel=payload.metrics.panel.voltage,
        current_panel=payload.metrics.panel.current,
        power_panel=payload.metrics.panel.power,
        # Beban
        load_voltage_beban=payload.metrics.beban.voltage,
        current_beban=payload.metrics.beban.current,
        power_beban=payload.metrics.beban.power,
        # Baterai
        load_voltage_baterai=payload.metrics.baterai.voltage,
        current_baterai=payload.metrics.baterai.current,
        power_baterai=payload.metrics.baterai.power,
    )

    # 3. Simpan record ke database
    try:
        db.add(telemetry_record)
        db.commit()
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan data ke database: {str(err)}",
        )

    # 4. Berikan respon sukses sesuai API Contract
    return IngestResponse(
        status="success",
        message="Telemetry data successfully recorded.",
    )


@router.get(
    "/latest",
    response_model=RealtimeResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch Data Realtime",
)
def get_latest_telemetry(db: Session = Depends(get_db)):
    """
    Mengambil data telemetri 9 metrik sensor terkini untuk Web Dashboard.
    """
    record = (
        db.query(Telemetry)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Belum ada data telemetri yang tersedia.",
        )

    system_status = evaluate_system_status(
        voltage_baterai=record.load_voltage_baterai,
        current_baterai=record.current_baterai,
    )

    return RealtimeResponse(
        status="success",
        data=RealtimeData(
            panel=ElectricalReading(
                voltage=record.load_voltage_panel,
                current=record.current_panel,
                power=record.power_panel,
            ),
            beban=ElectricalReading(
                voltage=record.load_voltage_beban,
                current=record.current_beban,
                power=record.power_beban,
            ),
            baterai=ElectricalReading(
                voltage=record.load_voltage_baterai,
                current=record.current_baterai,
                power=record.power_baterai,
            ),
            system_status=system_status,
            last_updated=record.timestamp,
        ),
    )
