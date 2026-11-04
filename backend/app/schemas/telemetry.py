from datetime import datetime
from pydantic import BaseModel, Field


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
