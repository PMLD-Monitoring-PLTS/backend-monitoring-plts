# Back-End Sistem Monitoring PLTS Berbasis Web Dashboard dan Telegram Bot

Sistem Monitoring PLTS (Pembangkit Listrik Tenaga Surya) berbasis Web Dashboard dan Telegram Bot yang dirancang untuk membantu monitoring kondisi kelistrikan PLTS secara berkala dan memberikan informasi kondisi sistem kepada pengguna.

Proyek ini dikembangkan sebagai bagian dari **Proyek Mandiri Lintas Disiplin Ilmu (PMLD)**.

---

## 📌 Tentang Proyek

Sistem ini dibuat untuk membantu pengelola/teknisi kampus dalam melakukan pengawasan operasional PLTS. Cara kerjanya, sistem akan menerima data telemetry PLTS dan mengolahnya agar dapat digunakan oleh Web Dashboard dan Telegram Bot.

Karena perangkat PLTS yang digunakan saat ini belum dapat digunakan secara langsung, proyek menyediakan **Dummy Data Generator / Simulator** sebagai sumber data telemetry selama tahap pengembangan.

Arsitektur data yang digunakan:

```text
PLTS / Simulator
       │
       ▼
      CSV
       │
       ▼
 Backend & Ingestion API
       │
       ▼
   Time-Series DB
       │
       ├──────────────► Web Dashboard
       │
       └──────────────► Telegram Bot
```

Pada tahap pengembangan saat ini, simulator digunakan untuk menghasilkan data telemetry dan menyimpannya ke dalam file CSV.

---

## 🎯 Tujuan

Tujuan utama proyek:

* Menyediakan monitoring kondisi kelistrikan PLTS.
* Menghasilkan data telemetry secara berkala selama perangkat PLTS belum dapat digunakan.
* Menyediakan data historis yang dapat digunakan untuk monitoring dan analisis.
* Mendukung pemberian peringatan ketika terjadi kondisi tertentu pada sistem.
* Menyiapkan arsitektur agar sumber data dapat diganti dari simulator ke sensor PLTS sebenarnya.

---

## ⚙️ Data Telemetry

Satu data telemetry merepresentasikan satu pembacaan kondisi PLTS pada satu waktu.

Sistem menggunakan **9 metrik kelistrikan**:

| Komponen | Voltage | Current | Power |
| --- | --- | --- | --- |
| Panel | `load_voltage_panel` | `current_panel` | `power_panel` |
| Beban | `load_voltage_beban` | `current_beban` | `power_beban` |
| Baterai | `load_voltage_baterai` | `current_baterai` | `power_baterai` |

Selain 9 metrik tersebut, setiap data memiliki:

* `timestamp`

Sehingga satu baris data CSV memiliki **10 kolom**.

### Satuan

| Data | Satuan |
| --- | --- |
| Voltage | V |
| Current | mA |
| Power | W |
| Timestamp | ISO 8601 |

Power dihitung berdasarkan voltage dan current:

```text
Power (W) = Voltage (V) × Current (mA) / 1000
```

Power tidak dibuat secara random secara terpisah dari voltage dan current.

---

## 🤖 Dummy Data Simulator

Simulator digunakan untuk menghasilkan data telemetry PLTS selama hardware belum dapat digunakan.

Simulator memiliki beberapa skenario kondisi:

### `NORMAL`
Menggambarkan kondisi operasi normal pada:
* Panel
* Beban
* Baterai

### `LOW_BATTERY`
Menggambarkan kondisi ketika tegangan baterai berada pada rentang rendah.

### `HIGH_LOAD`
Menggambarkan kondisi ketika konsumsi arus pada beban lebih tinggi dari kondisi normal.

### `LOW_PANEL_OUTPUT`
Menggambarkan kondisi ketika output panel lebih rendah dari kondisi normal.

Skenario digunakan untuk menentukan karakteristik data voltage dan current yang dihasilkan simulator.

> ℹ️ **Catatan:** Rentang nilai simulator saat ini merupakan asumsi untuk kebutuhan pengujian dan pengembangan, bukan spesifikasi final dari hardware PLTS.

---

## 📁 Struktur Proyek

```text
monitoring-plts-backend/
├── simulator/
│   ├── main.py
│   ├── generate.py
│   ├── scenario.py
│   └── csv_writer.py
│
├── backend/
│   └── ...
│
├── data/
│   └── plts_telemetry.csv
│
├── .gitignore
└── README.md
```

### Detail Modul `simulator/`

Berisi komponen Dummy Data Generator.

#### `main.py`
Bertanggung jawab sebagai orchestrator simulator.

Tugas utamanya:
1. Membuat file CSV jika belum tersedia.
2. Menjalankan generator telemetry.
3. Menulis telemetry ke CSV.
4. Menjalankan proses secara berkala.

#### `generate.py`
Bertanggung jawab untuk menghasilkan satu data telemetry.

Tugasnya:
* Mengambil konfigurasi scenario.
* Menghasilkan nilai voltage.
* Menghasilkan nilai current.
* Menghitung power.
* Menghasilkan timestamp.
* Mengembalikan data telemetry dalam bentuk dictionary.

#### `scenario.py`
Berisi konfigurasi berbagai skenario simulator beserta rentang nilai yang digunakan untuk menghasilkan telemetry.

#### `csv_writer.py`
Bertanggung jawab terhadap penulisan telemetry ke file CSV.

CSV bersifat **append-only**, sehingga data baru ditambahkan ke baris berikutnya tanpa menghapus data sebelumnya.

---

## 📄 Format CSV

File telemetry disimulasikan pada:

```text
data/plts_telemetry.csv
```

Format header:

```csv
timestamp,load_voltage_panel,current_panel,power_panel,load_voltage_beban,current_beban,power_beban,load_voltage_baterai,current_baterai,power_baterai
```

Contoh baris data:

```csv
timestamp,load_voltage_panel,current_panel,power_panel,load_voltage_beban,current_beban,power_beban,load_voltage_baterai,current_baterai,power_baterai
2026-09-17T11:00:00+07:00,13.52,1024.35,13.85,5.21,320.15,1.67,13.21,754.20,9.96
```

Satu baris CSV = satu pembacaan telemetry PLTS pada satu timestamp.
CSV digunakan sebagai **source of truth** pada tahap simulator saat ini.

---

## ⏱️ Interval Data

Simulator saat ini menghasilkan satu data telemetry setiap:

```text
30 detik
```

Interval tersebut digunakan untuk kebutuhan pengembangan dan pengujian. Dalam kondisi produksi, interval pembacaan dapat berbeda sesuai kebutuhan sistem dan perangkat sensor.

> ℹ️ **Catatan:** Interval simulator dan interval polling backend merupakan dua hal yang berbeda. Simulator menghasilkan data setiap 30 detik, sedangkan backend direncanakan melakukan polling CSV setiap 10 detik.

---

## 🔄 Alur Simulator

Proses simulator:

```text
main.py
   │
   ▼
generate_telemetry()
   │
   ▼
scenario.py
   │
   ▼
Generate Voltage & Current
   │
   ▼
Calculate Power
   │
   ▼
Generate Timestamp
   │
   ▼
Telemetry Dictionary
   │
   ▼
append_to_csv()
   │
   ▼
plts_telemetry.csv
```

---

## 🗄️ Rencana Integrasi Backend

Pada arsitektur keseluruhan sistem, CSV akan menjadi sumber data yang dibaca oleh backend.

Alur yang direncanakan:

```text
CSV
 │
 ▼
Backend FastAPI
 │
 ▼
Database
 │
 ├──► Telemetry Latest API
 │
 └──► Telemetry History API
```

Backend akan memeriksa data baru berdasarkan `timestamp`.

Konsep ingestion:
1. Backend membaca timestamp terakhir dari database.
2. Backend membaca data dari CSV.
3. Backend mengambil data dengan timestamp > timestamp terakhir di database.
4. Data baru dimasukkan ke database.

Timestamp diharapkan selalu meningkat secara kronologis. Kondisi timestamp yang duplicate atau menurun perlu dianggap sebagai data yang tidak valid dan ditangani oleh proses ingestion.

---

## 🔌 Kesiapan Integrasi Hardware

Simulator dibuat agar sumber data dapat diganti ketika sensor PLTS sebenarnya sudah dapat digunakan.

Target arsitektur:

```text
                 ┌──► Simulator ──► CSV ──► Backend
Data Source ────┤
                 └──► Sensor/ESP32 ───────► Backend
```

Dengan pendekatan tersebut, komponen yang menggunakan data telemetry tidak perlu bergantung langsung pada simulator.

---

## 🚀 Menjalankan Simulator

Pastikan Python sudah terinstall.

Dari folder proyek:

```bash
python simulator/main.py
```

Simulator akan menampilkan informasi seperti:

```text
Simulator PLTS dimulai | Scenario: NORMAL | Interval: 30s
```

Kemudian simulator akan menghasilkan telemetry secara berkala dan menambahkannya ke `data/plts_telemetry.csv`.

Untuk menghentikan simulator: Tekan `Ctrl + C` pada terminal.

---

## 🧪 Skenario Pengujian

Simulator dapat dijalankan menggunakan scenario yang berbeda untuk menguji perilaku sistem (dapat diubah pada `simulator/main.py`).

Contoh skenario:
* `SCENARIO = "NORMAL"`
* `SCENARIO = "LOW_BATTERY"`
* `SCENARIO = "HIGH_LOAD"`
* `SCENARIO = "LOW_PANEL_OUTPUT"`

Skenario ini nantinya dapat digunakan untuk menguji:
* Monitoring telemetry.
* Grafik histori.
* Kondisi beban tinggi.
* Kondisi output panel rendah.
* Kondisi baterai rendah.
* Sistem notifikasi Telegram.

---

## 🤝 Panduan Kontribusi

Proyek ini menggunakan Git untuk mengelola perubahan kode.

### Gaya Pesan Commit

Gunakan format berikut:

```text
feat:     fitur baru
fix:      perbaikan bug
test:     menambah atau memperbaiki pengujian
ci:       perubahan pada pipeline CI
docs:     dokumentasi
chore:    pekerjaan rumah tangga (konfigurasi, dependensi)
refactor: ubah struktur kode tanpa ubah perilaku
```

#### Contoh Commit

* Menambahkan simulator scenario baru:
  ```bash
  git commit -m "feat: tambah scenario low panel output"
  ```
* Memperbaiki bug CSV:
  ```bash
  git commit -m "fix: perbaiki penulisan telemetry ke csv"
  ```
* Menambahkan dokumentasi:
  ```bash
  git commit -m "docs: tambah dokumentasi simulator"
  ```
* Melakukan refactor:
  ```bash
  git commit -m "refactor: pisahkan konfigurasi scenario"
  ```

---

## 🌿 Branching Strategy

| Branch | Peran | Boleh push langsung? |
| --- | --- | --- |
| `feature/<sesuatu>` | satu perubahan, umurnya pendek | ya |
| `dev` | tempat semua fitur bertemu dan diuji bareng | tidak — lewat PR dari `feature/*` |
| `main` | kondisi yang dianggap layak rilis | tidak — lewat PR dari `dev` saja |

### Alur Pengembangan

```text
                 ┌──► feature/<sesuatu>
                 │
Developer ───────┤
                 │
                 └──► feature/<sesuatu>
                          │
                          ▼
                     Pull Request
                          │
                          ▼
                         dev
                          │
                          ▼
                    Integration Test
                          │
                          ▼
                     Pull Request
                          │
                          ▼
                        main
```

### Membuat Feature Branch

```bash
git checkout dev
git pull origin dev

git checkout -b feature/nama-fitur
```

Setelah pekerjaan selesai:

```bash
git add .
git commit -m "feat: deskripsi perubahan"
git push origin feature/nama-fitur
```

Kemudian buat **Pull Request** menuju:
`feature/nama-fitur` → `dev`

Setelah fitur di `dev` selesai diintegrasikan dan dianggap layak dirilis, buat **Pull Request**:
`dev` → `main`

---

## 🛠️ Catatan Pengembangan

Beberapa nilai dan konfigurasi pada simulator saat ini dibuat untuk kebutuhan development dan testing. Nilai tersebut belum dianggap sebagai spesifikasi final dari perangkat PLTS.

Ketika hardware sebenarnya sudah tersedia, range telemetry, satuan, threshold, interval pembacaan, dan karakteristik data perlu disesuaikan dengan spesifikasi serta hasil pengukuran perangkat sebenarnya.
