import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.abspath(
    os.path.join(BASE_DIR, "../data", "plts_telemetry.csv")
)

HEADERS = [
    "timestamp",
    "panel_voltage", "panel_current", "panel_power",
    "beban_voltage", "beban_current", "beban_power",
    "baterai_voltage", "baterai_current", "baterai_power",
]

def create_csv():
    if not os.path.exists(FILE_NAME):
        os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)
        with open(FILE_NAME, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(HEADERS)

def append_to_csv(telemetry):
    m = telemetry["metrics"]
    row = [
        telemetry["timestamp"],
        m["panel"]["voltage"],   m["panel"]["current"],   m["panel"]["power"],
        m["beban"]["voltage"],   m["beban"]["current"],   m["beban"]["power"],
        m["baterai"]["voltage"], m["baterai"]["current"], m["baterai"]["power"],
    ]
    with open(FILE_NAME, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(row)
