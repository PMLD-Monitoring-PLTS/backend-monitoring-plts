import random
from scenario import get_scenario
from datetime import datetime, timezone

DEVICE_ID = "ESP8266_PLTS_01"

def generate_value(value_range):
    minimum, maximum = value_range
    return random.uniform(minimum, maximum)

def generate_telemetry(scenario):

    config = get_scenario(scenario)

    # PANEL
    voltage_panel   = generate_value(config["panel"]["voltage"])
    current_panel   = generate_value(config["panel"]["current"])
    power_panel     = round(voltage_panel * current_panel / 1000, 2)

    # BEBAN
    voltage_beban   = generate_value(config["beban"]["voltage"])
    current_beban   = generate_value(config["beban"]["current"])
    power_beban     = round(voltage_beban * current_beban / 1000, 2)

    # BATERAI (current bisa negatif = discharge)
    voltage_baterai = generate_value(config["baterai"]["voltage"])
    current_baterai = generate_value(config["baterai"]["current"])
    power_baterai   = round(voltage_baterai * current_baterai / 1000, 2)
    # TIMESTAMP — ISO 8601 UTC
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Payload sesuai IngestRequest di API contract
    return {
        "device_id": DEVICE_ID,
        "timestamp": timestamp,
        "metrics": {
            "panel": {
                "voltage": round(voltage_panel, 2),
                "current": round(current_panel, 2),
                "power":   round(power_panel, 2),
            },
            "beban": {
                "voltage": round(voltage_beban, 2),
                "current": round(current_beban, 2),
                "power":   round(power_beban, 2),
            },
            "baterai": {
                "voltage": round(voltage_baterai, 2),
                "current": round(current_baterai, 2),
                "power":   round(power_baterai, 2),
            },
        },
    }
