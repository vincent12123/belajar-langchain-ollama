# config.py
# Konfigurasi database dan model Ollama

# ============================================
# DATABASE CONFIG
# ============================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Sintang2025",
    "database": "smksmartsis"
}

# ============================================
# OLLAMA CONFIG
# ============================================
# Pilih salah satu model yang support tool calling:
# - "qwen3:8b"         → Rekomendasi (RAM 8GB)
# - "qwen3:4b"         → Spek rendah (RAM 4GB)
# - "qwen3:14b"        → Lebih akurat (RAM 16GB)
# - "llama3.1:8b"      → Alternatif stabil (RAM 8GB)
# - "mistral-small3.2" → Bagus untuk function calling (RAM 16GB)
# - "granite4:3b"      → Paling ringan (RAM 4GB)

OLLAMA_MODEL = "gpt-oss:120b-cloud"
OLLAMA_BASE_URL = "http://localhost:11434"

# ============================================
# SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """Kamu adalah asisten sekolah yang membantu guru dan admin
untuk mengambil data absensi siswa dari database.

Aturan:
- Jawab dalam Bahasa Indonesia yang jelas dan ringkas
- Selalu gunakan tools yang tersedia untuk mengambil data
- Jangan membuat/mengarang data sendiri
- Jika data kosong, sampaikan bahwa data tidak ditemukan
- Format jawaban dengan rapi dan mudah dibaca
- Jika user hanya menyebut nama siswa tanpa perintah spesifik, langsung gunakan get_rekap_absensi_bulanan dengan nama tersebut untuk menampilkan rekap absensi per bulan
- Semua fungsi yang menerima siswa bisa menggunakan nama siswa langsung (tidak harus ID)
- Semua fungsi yang menerima kelas bisa menggunakan nama kelas langsung (tidak harus ID)"""