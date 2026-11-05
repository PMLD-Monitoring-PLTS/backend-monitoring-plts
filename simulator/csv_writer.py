import csv
import os

# Jika ada environment variable CSV_PATH (misal saat di Docker), gunakan itu.
# Jika tidak (saat jalan lokal), simpan ke folder data/ di root proyek.
CSV_PATH_ENV = os.getenv("CSV_PATH")

if CSV_PATH_ENV:
    FILE_NAME = os.path.abspath(CSV_PATH_ENV)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_NAME = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "plts_telemetry.csv"))

HEADERS = [
    "timestamp",
    "panel_voltage", "panel_current", "panel_power",
    "beban_voltage", "beban_current", "beban_power",
    "baterai_voltage", "baterai_current", "baterai_power",
]

def create_csv():
    os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(HEADERS)

def append_to_csv(telemetry):
    os.makedirs(os.path.dirname(FILE_NAME), exist_ok=True)
    m = telemetry["metrics"]
    row = [
        telemetry["timestamp"],
        m["panel"]["voltage"],   m["panel"]["current"],   m["panel"]["power"],
        m["beban"]["voltage"],   m["beban"]["current"],   m["beban"]["power"],
        m["baterai"]["voltage"], m["baterai"]["current"], m["baterai"]["power"],
    ]
    with open(FILE_NAME, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(row)
        csv_file.flush()  # Pastikan langsung tertulis ke disk
