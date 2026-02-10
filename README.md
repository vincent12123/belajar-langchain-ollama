# Sistem Absensi Sekolah - AI Agent

Aplikasi AI Agent berbasis **Ollama** yang memungkinkan guru dan admin sekolah mengakses data absensi siswa melalui pertanyaan bahasa natural (bahasa Indonesia). Agent otomatis memilih query database yang tepat berdasarkan pertanyaan pengguna.

## Cara Kerja

```
User bertanya (bahasa natural)
    ↓
LLM menganalisis & memilih tool (function calling)
    ↓
Tool dieksekusi → query ke MySQL
    ↓
Hasil dikirim balik ke LLM
    ↓
LLM merangkum jawaban dalam bahasa natural
```

## Fitur

- **Cari siswa** berdasarkan nama (pencarian parsial)
- **Daftar siswa per kelas** berdasarkan nama kelas
- **Data absensi** per siswa atau per kelas pada tanggal tertentu
- **Daftar siswa tidak hadir** (alfa/sakit/izin) pada hari tertentu
- **Rekap absensi** total per siswa (hadir, sakit, izin, alfa)
- **Rekap absensi bulanan** - breakdown per bulan dengan persentase kehadiran
- **Persentase kehadiran** per siswa atau per kelas

Semua fungsi mendukung pencarian menggunakan **nama** (tidak harus ID).

## Contoh Penggunaan

```
👤 Anda: giovinco
→ Menampilkan rekap absensi bulanan siswa bernama Giovinco

👤 Anda: siapa saja yang tidak hadir hari ini?
→ Menampilkan daftar siswa yang alfa/sakit/izin hari ini

👤 Anda: tampilkan siswa kelas X RPL 1
→ Menampilkan daftar siswa di kelas tersebut

👤 Anda: persentase kehadiran kelas XI TKJ 2 bulan Februari
→ Menampilkan persentase kehadiran kelas tersebut
```

## Struktur File

```
├── main.py              # Entry point - interactive chat
├── agent.py             # Agent router (Ollama + function calling)
├── db_functions.py      # Fungsi-fungsi query ke MySQL
├── tools_definition.py  # Definisi tools untuk function calling
├── config.py            # Konfigurasi database & model (tidak di-commit)
├── config.example.py    # Contoh konfigurasi
├── requirements.txt     # Dependencies Python
└── struktursmksmartsis.sql  # Struktur database
```

## Prasyarat

- **Python 3.10+**
- **MySQL 8.0+** dengan database `smksmartsis`
- **Ollama** terinstall dan berjalan, atau API kompatibel lainnya

## Instalasi

1. Clone repository
   ```bash
   git clone <url-repo>
   cd belajar-langchain-ollama
   ```

2. Buat virtual environment dan install dependencies
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Import struktur database
   ```bash
   mysql -u root -p smksmartsis < struktursmksmartsis.sql
   ```

4. Salin dan sesuaikan konfigurasi
   ```bash
   copy config.example.py config.py
   ```
   Edit `config.py` dan isi kredensial database serta model yang digunakan.

5. Jalankan aplikasi
   ```bash
   python main.py
   ```

## Konfigurasi

Buat file `config.py` berdasarkan `config.example.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password_anda",
    "database": "smksmartsis"
}

OLLAMA_MODEL = "qwen3:8b"  # sesuaikan dengan model yang tersedia
```

### Model yang Didukung

| Model               | RAM    | Keterangan                  |
|----------------------|--------|-----------------------------|
| `qwen3:4b`           | 4 GB   | Spek rendah                 |
| `qwen3:8b`           | 8 GB   | Rekomendasi                 |
| `qwen3:14b`          | 16 GB  | Lebih akurat                |
| `llama3.1:8b`        | 8 GB   | Alternatif stabil           |
| `mistral-small3.2`   | 16 GB  | Bagus untuk function calling|
| `granite4:3b`        | 4 GB   | Paling ringan               |

## Teknologi

- **Ollama** - menjalankan LLM secara lokal dengan function calling
- **MySQL** - database absensi sekolah
- **Python** - bahasa pemrograman utama
