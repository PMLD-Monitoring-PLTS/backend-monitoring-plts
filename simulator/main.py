import json
import urllib.request
import urllib.error
from time import sleep
import generate
import csv_writer

# ========================================================
# KONFIGURASI SIMULATOR (ESP8266 IoT Device)
# ========================================================
SIMULATOR_INTERVAL = 10  # Interval pengiriman dalam detik
SCENARIO = "NORMAL"      # Pilihan: NORMAL, LOW_BATTERY, HIGH_LOAD, LOW_PANEL_OUTPUT

# Target Ingestion API (sesuai API_Contract.yaml)
API_URL = "http://localhost:3000/api/v1/telemetry/ingest"
DEVICE_API_KEY = "ESP8266_PLTS_SECRET_KEY"


def send_telemetry_http(url: str, api_key: str, payload: dict):
    """
    Mengirim telemetry data via HTTP POST ke Ingestion API
    menyerupai modul HTTPClient pada mikrokontroler ESP8266.
    Menggunakan urllib.request (bawaan Python standard library).
    """
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Device-API-Key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_code = response.getcode()
            res_body = response.read().decode("utf-8")
            return res_code, res_body
    except urllib.error.HTTPError as e:
        # Respon dari server saat request diterima tapi ditolak (misal 400, 401, 500)
        res_body = e.read().decode("utf-8") if e.fp else str(e)
        return e.code, res_body
    except urllib.error.URLError as e:
        # Gagal koneksi (misal server belum menyala atau timeout)
        return None, str(e.reason)
    except Exception as e:
        return None, str(e)


def main():
    print("=" * 65)
    print("🚀 SIMULATOR ESP8266 PLTS - HTTP INGESTION CLIENT")
    print(f"• Target Endpoint : {API_URL}")
    print(f"• Skenario        : {SCENARIO}")
    print(f"• Interval Kirim  : {SIMULATOR_INTERVAL} detik")
    print("=" * 65)

    csv_writer.create_csv()

    while True:
        # 1. Baca data sensor yang dihasilkan generator
        telemetry = generate.generate_telemetry(SCENARIO)
        timestamp = telemetry["timestamp"]
        device_id = telemetry["device_id"]

        # 2. Simpan ke CSV lokal sebagai backup / local storage
        csv_writer.append_to_csv(telemetry)

        # 3. Kirim data ke API via HTTP POST (seperti ESP nyata)
        status_code, response_text = send_telemetry_http(API_URL, DEVICE_API_KEY, telemetry)

        # 4. Tampilkan status ke console (seperti Serial Monitor pada ESP)
        if status_code == 200:
            print(f"[{timestamp}] [{device_id}] ✅ HTTP 200 OK -> Data berhasil dicatat server.")
        elif status_code in (400, 401, 403, 500):
            print(f"[{timestamp}] [{device_id}] ⚠️ HTTP {status_code} Error: {response_text}")
        else:
            print(f"[{timestamp}] [{device_id}] ❌ Koneksi Gagal: Server belum aktif ({response_text})")
            print("   ↳ Data tetap berhasil dicatat ke data/plts_telemetry.csv")

        sleep(SIMULATOR_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Simulator dihentikan oleh pengguna.")
