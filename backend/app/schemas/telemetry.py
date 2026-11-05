from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class SystemStatusEnum(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class ElectricalReading(BaseModel):
    voltage: float = Field(..., description="Tegangan dalam Volt (V)")
    current: float = Field(..., description="Arus dalam mA (boleh negatif untuk baterai)")
    power: float = Field(..., description="Daya dalam W atau mW")


class TelemetryMetrics(BaseModel):
    panel: ElectricalReading
    beban: ElectricalReading
    baterai: ElectricalReading


class TelemetryIngestRequest(BaseModel):
    device_id: str = Field(..., description="ID perangkat ESP8266")
    timestamp: datetime = Field(..., description="Waktu pembacaan ISO 8601")
    metrics: TelemetryMetrics


class IngestResponse(BaseModel):
    status: str = "success"
    message: str = "Telemetry data successfully recorded."



# Latest endpoint
class RealtimeData(BaseModel):
    panel: ElectricalReading
    beban: ElectricalReading
    baterai: ElectricalReading
    system_status: SystemStatusEnum
    last_updated: datetime


class RealtimeResponse(BaseModel):
    status: str = "success"
    data: RealtimeData


class HistoryPoint(BaseModel):
    timestamp: datetime
    panel: ElectricalReading
    beban: ElectricalReading
    baterai: ElectricalReading


class HistoryData(BaseModel):
    interval: str
    from_: datetime = Field(..., alias="from")
    to: datetime
    points: list[HistoryPoint]

    model_config = {"populate_by_name": True}


class HistoryResponse(BaseModel):
    status: str = "success"
    data: HistoryData
