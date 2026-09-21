import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.abspath(
    os.path.join(BASE_DIR, "../data", "plts_telemetry.csv")
)

HEADERS = [
    "timestamp",
    "load_voltage_panel",
    "current_panel",
    "power_panel",
    "load_voltage_beban",
    "current_beban",
    "power_beban",
    "load_voltage_baterai",
    "current_baterai",
    "power_baterai"
]

def create_csv():
    if not os.path.exists(FILE_NAME):
        os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)
        with open(FILE_NAME, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(HEADERS)

def append_to_csv(telemetry):
    with open(FILE_NAME, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([telemetry[header] for header in HEADERS])
