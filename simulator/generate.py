import random
from scenario import get_scenario
from datetime import datetime

def generate_value(value_range):
    minimum, maximum = value_range
    return random.uniform(minimum, maximum)

def calculate_power(voltage, current):
    return voltage * current / 1000

def generate_telemetry(scenario):

    config = get_scenario(scenario)

    # PANEL
    voltage_panel = generate_value(
        config["panel"]["voltage"]
    )

    current_panel = generate_value(
        config["panel"]["current"]
    )

    power_panel = calculate_power(
        voltage_panel,
        current_panel
    )

    # BEBAN
    voltage_beban = generate_value(
        config["beban"]["voltage"]
    )

    current_beban = generate_value(
        config["beban"]["current"]
    )

    power_beban = calculate_power(
        voltage_beban,
        current_beban
    )

    # BATTERY
    voltage_baterai = generate_value(
        config["baterai"]["voltage"]
    )

    current_baterai = generate_value(
        config["baterai"]["current"]
    )

    power_baterai = calculate_power(
        voltage_baterai,
        current_baterai
    )

    # TIMESTAMP
    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    return {
        "timestamp": timestamp,

        "load_voltage_panel": round(voltage_panel, 2),
        "current_panel": round(current_panel, 2),
        "power_panel": round(power_panel, 2),

        "load_voltage_beban": round(voltage_beban, 2),
        "current_beban": round(current_beban, 2),
        "power_beban": round(power_beban, 2),

        "load_voltage_baterai": round(voltage_baterai, 2),
        "current_baterai": round(current_baterai, 2),
        "power_baterai": round(power_baterai, 2)
    }