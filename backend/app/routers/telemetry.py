import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryIngestRequest, IngestResponse

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["Telemetry"],
)

# API Key yang valid (bisa diatur lewat .env atau default)
EXPECTED_DEVICE_KEY = os.getenv("DEVICE_API_KEY", "ESP8266_PLTS_SECRET_KEY")


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
