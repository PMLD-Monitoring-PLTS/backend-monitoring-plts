import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.telemetry import Telemetry
from app.models.users import User
from app.schemas.telemetry import (
    ElectricalReading,
    HistoryData,
    HistoryPoint,
    HistoryResponse,
    IngestResponse,
    RealtimeData,
    RealtimeResponse,
    TelemetryIngestRequest,
)

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["Telemetry"],
)

EXPECTED_DEVICE_KEY = os.getenv("DEVICE_API_KEY", "ESP8266_PLTS_SECRET_KEY")

# Pemetaan nilai interval dari query param ke interval SQL
INTERVAL_MAP = {
    "5m":  "5 minutes",
    "10m": "10 minutes",
    "1h":  "1 hour",
    "1d":  "1 day",
}


def evaluate_system_status(voltage_baterai: float | None, current_baterai: float | None) -> str:
    """
    Evaluasi status sistem berdasarkan ambang batas baterai (sesuai API contract):
    - critical : tegangan <= 11.5 V atau arus discharge <= -3000 mA
    - warning  : tegangan <= 12.0 V atau arus discharge <= -1500 mA
    - normal   : selain kondisi di atas
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
    if x_device_api_key != EXPECTED_DEVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akses ditolak. Kredensial tidak valid.",
        )

    telemetry_record = Telemetry(
        timestamp=payload.timestamp,
        device_id=payload.device_id,
        load_voltage_panel=payload.metrics.panel.voltage,
        current_panel=payload.metrics.panel.current,
        power_panel=payload.metrics.panel.power,
        load_voltage_beban=payload.metrics.beban.voltage,
        current_beban=payload.metrics.beban.current,
        power_beban=payload.metrics.beban.power,
        load_voltage_baterai=payload.metrics.baterai.voltage,
        current_baterai=payload.metrics.baterai.current,
        power_baterai=payload.metrics.baterai.power,
    )

    try:
        db.add(telemetry_record)
        db.commit()
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan data ke database: {str(err)}",
        )

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
def get_latest_telemetry(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Mengambil 9 metrik sensor terkini untuk Web Dashboard.
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


@router.get(
    "/history",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch Riwayat Data (Grafik Tren)",
)
def get_telemetry_history(
    from_: datetime | None = Query(
        default=None,
        alias="from",
        description="Batas awal rentang waktu. Default 24 jam sebelum `to`.",
    ),
    to: datetime | None = Query(
        default=None,
        description="Batas akhir rentang waktu. Default sekarang.",
    ),
    interval: str = Query(
        default="10m",
        pattern="^(raw|5m|10m|1h|1d)$",
        description="Interval agregasi rata-rata. Pilihan: raw, 5m, 10m, 1h, 1d.",
    ),
    limit: int = Query(
        default=200,
        ge=1,
        le=1000,
        description="Batas maksimum jumlah titik data yang dikembalikan.",
    ),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Mengambil data historis untuk grafik tren panel/beban/baterai.
    - interval=raw        : Data mentah per row.
    - interval=5m/10m/1h/1d : Rata-rata (AVG) per bucket waktu.
    """
    # Resolve default nilai to dan from
    now = datetime.now(timezone.utc)

    resolved_to: datetime = to if isinstance(to, datetime) else now
    if resolved_to.tzinfo is None:
        resolved_to = resolved_to.replace(tzinfo=timezone.utc)

    resolved_from: datetime = (
        from_ if isinstance(from_, datetime) else resolved_to - timedelta(hours=24)
    )
    if resolved_from.tzinfo is None:
        resolved_from = resolved_from.replace(tzinfo=timezone.utc)

    # Resolve default interval dan limit saat dipanggil di luar HTTP context
    resolved_interval: str = interval if isinstance(interval, str) else "10m"
    resolved_limit: int = limit if isinstance(limit, int) else 200

    if resolved_from >= resolved_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parameter `from` harus lebih awal dari `to`.",
        )

    if resolved_interval == "raw":
        rows = (
            db.query(Telemetry)
            .filter(Telemetry.timestamp >= resolved_from, Telemetry.timestamp <= resolved_to)
            .order_by(Telemetry.timestamp.asc())
            .limit(resolved_limit)
            .all()
        )
        points = [
            HistoryPoint(
                timestamp=row.timestamp,
                panel=ElectricalReading(
                    voltage=row.load_voltage_panel,
                    current=row.current_panel,
                    power=row.power_panel,
                ),
                beban=ElectricalReading(
                    voltage=row.load_voltage_beban,
                    current=row.current_beban,
                    power=row.power_beban,
                ),
                baterai=ElectricalReading(
                    voltage=row.load_voltage_baterai,
                    current=row.current_baterai,
                    power=row.power_baterai,
                ),
            )
            for row in rows
        ]
    else:
        # Hitung rata-rata per bucket waktu menggunakan date_bin (PostgreSQL 14+)
        sql_interval = INTERVAL_MAP[resolved_interval]
        rows = db.execute(
            text("""
                SELECT
                    date_bin(
                        CAST(:interval AS INTERVAL),
                        timestamp,
                        TIMESTAMPTZ '2000-01-01'
                    ) AS bucket,
                    AVG(load_voltage_panel)   AS voltage_panel,
                    AVG(current_panel)        AS current_panel,
                    AVG(power_panel)          AS power_panel,
                    AVG(load_voltage_beban)   AS voltage_beban,
                    AVG(current_beban)        AS current_beban,
                    AVG(power_beban)          AS power_beban,
                    AVG(load_voltage_baterai) AS voltage_baterai,
                    AVG(current_baterai)      AS current_baterai,
                    AVG(power_baterai)        AS power_baterai
                FROM telemetry
                WHERE timestamp >= :from_ts AND timestamp <= :to_ts
                GROUP BY bucket
                ORDER BY bucket ASC
                LIMIT :limit
            """),
            {
                "interval": sql_interval,
                "from_ts": resolved_from,
                "to_ts": resolved_to,
                "limit": resolved_limit,
            },
        ).fetchall()

        points = [
            HistoryPoint(
                timestamp=row.bucket,
                panel=ElectricalReading(
                    voltage=round(row.voltage_panel, 2),
                    current=round(row.current_panel, 2),
                    power=round(row.power_panel, 2),
                ),
                beban=ElectricalReading(
                    voltage=round(row.voltage_beban, 2),
                    current=round(row.current_beban, 2),
                    power=round(row.power_beban, 2),
                ),
                baterai=ElectricalReading(
                    voltage=round(row.voltage_baterai, 2),
                    current=round(row.current_baterai, 2),
                    power=round(row.power_baterai, 2),
                ),
            )
            for row in rows
        ]

    return HistoryResponse(
        status="success",
        data=HistoryData(**{
            "from": resolved_from,
            "to": resolved_to,
            "interval": resolved_interval,
            "points": points,
        }),
    )
