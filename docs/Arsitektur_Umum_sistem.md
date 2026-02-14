

Baik! Sebelum kita masuk ke Pydantic model, mari kita pelajari secara menyeluruh semua isi program yang ada. Saya akan mengambil konten dari semua file yang tersedia untuk memberikan gambaran lengkap.

Baik, mari kita pelajari semua isi program secara menyeluruh terlebih dahulu sebelum masuk ke Pydantic model. Saya akan mengekstrak semua konten kode dari file yang tersedia.

Baik! Sebelum kita masuk ke pembuatan Pydantic models, mari kita pelajari secara menyeluruh semua isi program dari sistem ini. Saya akan mengekstrak seluruh konten dari file yang sudah Anda berikan untuk memastikan kita memahami setiap detail.

Baik! Sebelum kita masuk ke pembuatan Pydantic model, mari kita pelajari secara menyeluruh semua isi program yang ada. Saya akan mengekstrak dan menganalisis setiap modul dari file yang tersedia.

Baik, mari kita pelajari keseluruhan isi program secara menyeluruh terlebih dahulu sebelum masuk ke Pydantic model. Berdasarkan semua file yang sudah kamu berikan (`kumpulan.txt`, `snippet.txt`, `smksmartsis.sql.txt`, dan `api.py`), berikut gambaran lengkap sistem **School Attendance AI System**:

---

## 1. Arsitektur Umum Sistem

Sistem ini adalah **aplikasi manajemen kehadiran sekolah berbasis AI** yang terdiri dari beberapa modul utama yang saling terhubung. Secara garis besar, arsitekturnya seperti ini:

```
[Frontend / Client]
       │
       ▼
   [api.py]  ←── FastAPI Server (REST + WebSocket)
       │
       ▼
   [agent.py]  ←── AI Agent (Ollama/LLM)
       │
       ├── [tools_definition.py]  ←── Definisi tool untuk function calling
       ├── [config.py]  ←── Konfigurasi database & sistem
       ├── [Database Functions]  ←── Query SQL ke MySQL
       └── [pdf_generator.py]  ←── Generator laporan PDF
              │
              ▼
       [MySQL Database]  ←── smksmartsis (schema dari .sql file)
```

---

## 2. File: `config.py` — Konfigurasi Sistem

File ini berisi pengaturan dasar untuk koneksi dan konfigurasi:

**Fungsinya:** menyimpan konstanta dan konfigurasi yang dipakai seluruh modul, termasuk koneksi database MySQL (host, user, password, database name), konfigurasi model AI (Ollama client, model name), dan path untuk file output seperti PDF.

Ini adalah "jantung" konfigurasi — semua modul lain mengimpor dari sini untuk mendapatkan parameter koneksi dan pengaturan.

---

## 3. File: `agent.py` — Otak AI Agent

Ini adalah **inti logika AI** dari sistem. File ini menangani:

**Fungsi Utama:**

- **`run_agent(query)`** — Menerima pertanyaan user, mengirimnya ke model LLM (via `OLLAMA_CLIENT`), memproses tool calls jika diperlukan, dan mengembalikan jawaban terstruktur.

- **`run_agent_with_history(query, history)`** — Sama seperti `run_agent` tapi menyertakan riwayat percakapan untuk konteks yang lebih baik (multi-turn conversation).

**Alur Kerjanya:**

1. User mengirim pertanyaan (misal: "Siapa siswa yang paling sering absen?")
2. Agent mengirim pertanyaan ke LLM
3. LLM memutuskan apakah perlu memanggil **tool/function** (misal: query database)
4. Jika ya, agent menjalankan function yang diminta dan mengirim hasilnya kembali ke LLM
5. LLM merangkum hasilnya menjadi jawaban natural language
6. Agent mengembalikan response dalam format `QueryResponse`

**Masalah yang sudah teridentifikasi:** Error handling masih di level tinggi (high-level), belum ada granular try-except di sekitar pemanggilan API dan tool calls, sehingga berisiko *silent failures*.

---

## 4. File: `tools_definition.py` — Definisi Tool untuk Function Calling

File ini mendefinisikan **semua tool/fungsi yang bisa dipanggil oleh AI agent**. Ini seperti "menu" yang diberikan ke LLM agar tahu fungsi apa saja yang tersedia.

**Tool-tool utama yang didefinisikan:**

| Tool | Fungsi |
|------|--------|
| `cari_siswa` | Mencari data siswa berdasarkan nama atau NIS |
| `get_absensi_by_siswa` | Mengambil data kehadiran per siswa |
| `get_rekap_absensi` | Rekap kehadiran (hadir, sakit, izin, alpha) |
| `compare_class_attendance` | Membandingkan kehadiran antar kelas |
| `get_attendance_trends` | Menganalisis tren kehadiran dalam periode tertentu |
| `get_geolocation_analysis` | Analisis lokasi GPS saat absen (deteksi kecurangan) |
| `get_anomaly_detection` | Mendeteksi anomali kehadiran (pola mencurigakan) |
| `get_laporan_kepsek_range` | Laporan untuk kepala sekolah dalam rentang tanggal |
| `get_top_students` | Siswa dengan kehadiran terbaik/terburuk |
| `get_time_statistics` | Statistik waktu kehadiran (rata-rata jam masuk, dll) |
| `get_attendance_method_analysis` | Analisis metode absensi (QR, GPS, manual) |

Setiap tool memiliki deskripsi, parameter yang diharapkan (nama, tipe, required/optional), dan format output yang dikembalikan.

---

## 5. File: `api.py` — FastAPI Server

Ini adalah **pintu masuk (gateway)** antara frontend/client dan backend. Semua request masuk melalui sini.

**Endpoint-endpoint utama:**

| Endpoint | Method | Fungsi |
|----------|--------|--------|
| `/` | GET | Status server |
| `/api/chat` | POST | Endpoint utama chat AI — menerima query user, diteruskan ke agent |
| `/chat` | POST | Chat AI kompatibel Vercel AI SDK (streaming) |
| `/api/attendance/trends` | POST | Tren kehadiran per siswa/kelas |
| `/api/geolocation/analysis` | POST | Analisis validasi GPS kehadiran |
| `/api/class/comparison` | POST | Perbandingan kehadiran antar kelas |
| `/api/attendance/anomaly` | POST | Deteksi anomali kehadiran |
| `/api/attendance/method-analysis` | POST | Analisis metode absensi |
| `/api/top-students` | POST | Leaderboard siswa berdasarkan kehadiran |
| `/api/time-statistics` | POST | Statistik waktu kehadiran |
| `/api/report/principal` | POST | Laporan kepala sekolah |
| `/api/report/daily-teacher` | POST | Laporan harian guru |
| `/ws/{client_id}` | WebSocket | Chat AI real-time via WebSocket |
| `/api/classes` | GET | Daftar kelas aktif |
| `/api/files` | GET | List file PDF yang tersedia |
| `/download/{filename}` | GET | Download file PDF |

**Fitur penting:**
- CORS middleware untuk integrasi frontend
- Async processing (`run_in_executor`) untuk operasi berat
- WebSocket untuk komunikasi real-time
- Response dalam format JSON terstruktur (`QueryResponse`)

---

## 6. Database Functions — Query SQL

Ini adalah kumpulan fungsi Python yang **langsung berinteraksi dengan database MySQL**. Setiap fungsi menjalankan query SQL spesifik dan mengembalikan hasilnya.

**Kategori fungsi:**

**Data Retrieval (Pengambilan Data):**
- Cari siswa, ambil data kehadiran, ambil rekap per kelas/siswa

**Analisis & Reporting:**
- Tren kehadiran, perbandingan kelas, statistik waktu
- Deteksi anomali dan aktivitas mencurigakan

**Geolocation & GPS:**
- Validasi lokasi absensi, deteksi lokasi palsu/spoofing
- Analisis jarak dari koordinat sekolah

**Laporan Khusus:**
- Laporan kepala sekolah, laporan harian guru
- Data untuk surat peringatan

---

## 7. File: `pdf_generator.py` — Generator Laporan PDF

Modul ini menghasilkan **dokumen PDF** untuk berbagai keperluan:

- **Surat Peringatan** — untuk siswa dengan kehadiran buruk
- **Laporan Rekap** — ringkasan kehadiran per kelas/periode
- **Laporan Kepala Sekolah** — laporan komprehensif untuk manajemen

File PDF yang dihasilkan disimpan di server dan bisa didownload melalui endpoint `/download/{filename}`.

---

## 8. Database Schema (`smksmartsis.sql.txt`)

Database MySQL bernama **smksmartsis** dengan tabel-tabel utama:

| Tabel | Fungsi | Relasi |
|-------|--------|--------|
| `siswa` | Data siswa (NIS, nama, email, QR code) | — |
| `kelas` | Data kelas (nama, tingkat, tahun ajaran) | FK → `tahun_ajaran` |
| `tahun_ajaran` | Data tahun ajaran | — |
| `penempatan_kelas` | Mapping siswa ke kelas | FK → `siswa`, `kelas` |
| `absensi` | Record kehadiran harian | FK → `siswa`, `kelas` |
| `tagihan_spps` | Tagihan SPP siswa | FK → `siswa` |
| `tagihan_lains` | Tagihan lain-lain | FK → `siswa` |
| `pembayaran_spps` | Pembayaran SPP | FK → `tagihan_spps` |
| `settings` | Konfigurasi sistem | — |
| `migrations` | Versioning schema | — |

**Tabel `absensi`** adalah tabel paling krusial, berisi kolom: `id`, `siswa_id`, `kelas_id`, `tanggal`, `status` (Hadir/Sakit/Izin/Alpha), `metode` (QR/GPS/Manual), `waktu_masuk`, `waktu_keluar`, `latitude`, `longitude`, dan timestamps.

---

## Ringkasan Alur Sistem End-to-End

```
1. User mengirim pertanyaan → [Frontend]
2. Request masuk ke → [api.py] endpoint /api/chat
3. api.py meneruskan ke → [agent.py] run_agent()
4. Agent mengirim ke → [LLM/Ollama] dengan daftar tools dari tools_definition.py
5. LLM memutuskan tool mana yang dipanggil
6. Agent menjalankan → [Database Functions] query SQL ke MySQL
7. Hasil query dikembalikan ke LLM untuk dirangkum
8. Response dikembalikan dalam format → QueryResponse (Pydantic)
9. api.py mengirim response JSON ke → [Frontend]
10. (Opsional) pdf_generator.py membuat laporan PDF
```

---

