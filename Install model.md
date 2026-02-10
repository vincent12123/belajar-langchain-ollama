

Baik, saya buatkan **kode lengkap per file** beserta rekomendasi model Ollama terbaik untuk tool calling.

---

## Rekomendasi Model Ollama untuk Tool Calling

Berdasarkan data terbaru, berikut model terbaik yang support **tool calling** di Ollama [citation:2][citation:7][citation:11]:

| Model | Ukuran | RAM Minimal | Keterangan |
|-------|--------|-------------|------------|
| **`qwen3:8b`** | 8B | 8 GB | **Paling direkomendasikan** — ringan, akurat, support tools + thinking |
| `qwen3:4b` | 4B | 4 GB | Untuk PC/laptop spek rendah |
| `qwen3:14b` | 14B | 16 GB | Lebih akurat, butuh RAM lebih |
| `llama3.1:8b` | 8B | 8 GB | Stabil, banyak dipakai |
| `mistral-small3.2` | 24B | 16 GB | Bagus untuk function calling |
| `granite4:3b` | 3B | 4 GB | Paling ringan, enterprise-ready |
| `qwen2.5:32b` | 32B | 32 GB | Paling reliable menurut komunitas |

**Rekomendasi saya:** Gunakan **`qwen3:8b`** — keseimbangan terbaik antara performa dan kebutuhan resource.

```bash
# Install model
ollama pull qwen3:8b
```

---

Sekarang kode lengkap per file:

---

## File 1: `config.py`

```python
# config.py
# Konfigurasi database dan model Ollama

# ============================================
# DATABASE CONFIG
# ============================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "school_db"
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

OLLAMA_MODEL = "qwen3:8b"
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
- Format jawaban dengan rapi dan mudah dibaca"""
```

---

## File 2: `tools_definition.py`

```python
# tools_definition.py
# Definisi tools untuk function calling (OpenAI format)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_absensi_by_siswa",
            "description": "Mengambil data absensi/kehadiran berdasarkan ID siswa dan rentang tanggal",
            "parameters": {
                "type": "object",
                "properties": {
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID unik siswa di database"
                    },
                    "tanggal_mulai": {
                        "type": "string",
                        "description": "Tanggal mulai dalam format YYYY-MM-DD (opsional)"
                    },
                    "tanggal_akhir": {
                        "type": "string",
                        "description": "Tanggal akhir dalam format YYYY-MM-DD (opsional)"
                    }
                },
                "required": ["siswa_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_absensi_by_kelas",
            "description": "Mengambil data absensi seluruh siswa dalam satu kelas pada tanggal tertentu",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {
                        "type": "integer",
                        "description": "ID kelas"
                    },
                    "tanggal": {
                        "type": "string",
                        "description": "Tanggal absensi dalam format YYYY-MM-DD"
                    }
                },
                "required": ["kelas_id", "tanggal"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_siswa_tidak_hadir",
            "description": "Mengambil daftar siswa yang tidak hadir (alfa/sakit/izin) pada hari tertentu",
            "parameters": {
                "type": "object",
                "properties": {
                    "tanggal": {
                        "type": "string",
                        "description": "Tanggal dalam format YYYY-MM-DD. Default: hari ini"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["alfa", "sakit", "izin"],
                        "description": "Filter berdasarkan status ketidakhadiran (opsional)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_rekap_absensi",
            "description": "Menghitung rekap/ringkasan absensi siswa (total hadir, sakit, izin, alfa)",
            "parameters": {
                "type": "object",
                "properties": {
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID unik siswa"
                    },
                    "bulan": {
                        "type": "integer",
                        "description": "Bulan (1-12), opsional"
                    },
                    "tahun": {
                        "type": "integer",
                        "description": "Tahun (contoh: 2026), opsional"
                    }
                },
                "required": ["siswa_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_persentase_kehadiran",
            "description": "Menghitung persentase kehadiran siswa atau seluruh kelas dalam periode tertentu",
            "parameters": {
                "type": "object",
                "properties": {
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID siswa (opsional, isi salah satu: siswa_id atau kelas_id)"
                    },
                    "kelas_id": {
                        "type": "integer",
                        "description": "ID kelas (opsional, isi salah satu: siswa_id atau kelas_id)"
                    },
                    "bulan": {
                        "type": "integer",
                        "description": "Bulan (1-12)"
                    },
                    "tahun": {
                        "type": "integer",
                        "description": "Tahun (contoh: 2026)"
                    }
                }
            }
        }
    }
]
```

---

## File 3: `db_functions.py`

```python
# db_functions.py
# Fungsi-fungsi SQL query untuk mengambil data absensi

import mysql.connector
from datetime import date
from typing import Optional, List, Dict, Any
from config import DB_CONFIG


def get_db_connection():
    """Buat koneksi baru ke database"""
    return mysql.connector.connect(**DB_CONFIG)


def get_absensi_by_siswa(
    siswa_id: int,
    tanggal_mulai: Optional[str] = None,
    tanggal_akhir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Ambil data absensi berdasarkan siswa"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            k.nama AS kelas,
            a.tanggal,
            a.status,
            a.keterangan
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.siswa_id = %s
    """
    params = [siswa_id]

    if tanggal_mulai and tanggal_akhir:
        query += " AND a.tanggal BETWEEN %s AND %s"
        params.extend([tanggal_mulai, tanggal_akhir])

    query += " ORDER BY a.tanggal DESC LIMIT 50"
    cursor.execute(query, params)
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_absensi_by_kelas(
    kelas_id: int,
    tanggal: str
) -> List[Dict[str, Any]]:
    """Ambil data absensi seluruh siswa dalam satu kelas"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            a.status,
            a.keterangan
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s AND a.tanggal = %s
        ORDER BY s.nama
    """
    cursor.execute(query, [kelas_id, tanggal])
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_siswa_tidak_hadir(
    tanggal: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Ambil daftar siswa yang tidak hadir"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not tanggal:
        tanggal = date.today().isoformat()

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            k.nama AS kelas,
            a.status,
            a.keterangan
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.tanggal = %s AND a.status != 'hadir'
    """
    params = [tanggal]

    if status:
        query += " AND a.status = %s"
        params.append(status)

    query += " ORDER BY k.nama, s.nama"
    cursor.execute(query, params)
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_rekap_absensi(
    siswa_id: int,
    bulan: Optional[int] = None,
    tahun: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Hitung rekap absensi siswa"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            COUNT(CASE WHEN a.status = 'hadir' THEN 1 END) AS total_hadir,
            COUNT(CASE WHEN a.status = 'sakit' THEN 1 END) AS total_sakit,
            COUNT(CASE WHEN a.status = 'izin' THEN 1 END)  AS total_izin,
            COUNT(CASE WHEN a.status = 'alfa' THEN 1 END)  AS total_alfa,
            COUNT(*) AS total_hari
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.siswa_id = %s
    """
    params = [siswa_id]

    if bulan:
        query += " AND MONTH(a.tanggal) = %s"
        params.append(bulan)
    if tahun:
        query += " AND YEAR(a.tanggal) = %s"
        params.append(tahun)

    query += " GROUP BY s.id, s.nama, s.nis"
    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    db.close()
    return result


def get_persentase_kehadiran(
    siswa_id: Optional[int] = None,
    kelas_id: Optional[int] = None,
    bulan: Optional[int] = None,
    tahun: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Hitung persentase kehadiran siswa atau kelas"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if siswa_id:
        query = """
            SELECT 
                s.nama AS nama_siswa,
                ROUND(
                    COUNT(CASE WHEN a.status = 'hadir' THEN 1 END) * 100.0 / COUNT(*), 2
                ) AS persentase_kehadiran
            FROM absensi a
            JOIN siswa s ON a.siswa_id = s.id
            WHERE a.siswa_id = %s
        """
        params = [siswa_id]
    elif kelas_id:
        query = """
            SELECT 
                k.nama AS kelas,
                ROUND(
                    COUNT(CASE WHEN a.status = 'hadir' THEN 1 END) * 100.0 / COUNT(*), 2
                ) AS persentase_kehadiran
            FROM absensi a
            JOIN kelas k ON a.kelas_id = k.id
            WHERE a.kelas_id = %s
        """
        params = [kelas_id]
    else:
        return {"error": "Harus menyertakan siswa_id atau kelas_id"}

    if bulan:
        query += " AND MONTH(a.tanggal) = %s"
        params.append(bulan)
    if tahun:
        query += " AND YEAR(a.tanggal) = %s"
        params.append(tahun)

    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    db.close()
    return result
```

---

## File 4: `agent.py`

```python
# agent.py
# Agent Router menggunakan Ollama

import ollama
import json
from config import OLLAMA_MODEL, SYSTEM_PROMPT
from tools_definition import tools
from db_functions import (
    get_absensi_by_siswa,
    get_absensi_by_kelas,
    get_siswa_tidak_hadir,
    get_rekap_absensi,
    get_persentase_kehadiran,
)


# ============================================
# MAPPING: nama function → function Python
# ============================================
available_functions = {
    "get_absensi_by_siswa": get_absensi_by_siswa,
    "get_absensi_by_kelas": get_absensi_by_kelas,
    "get_siswa_tidak_hadir": get_siswa_tidak_hadir,
    "get_rekap_absensi": get_rekap_absensi,
    "get_persentase_kehadiran": get_persentase_kehadiran,
}


def run_agent(user_message: str, model: str = None) -> str:
    """
    Jalankan agent untuk menjawab pertanyaan user.
    
    Flow:
    1. User bertanya dalam bahasa natural
    2. LLM menganalisis dan memilih tool yang tepat
    3. Tool dieksekusi → query ke MySQL
    4. Hasil dikirim balik ke LLM
    5. LLM merangkum jawaban dalam bahasa natural
    """
    
    if model is None:
        model = OLLAMA_MODEL
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    print(f"\n{'='*60}")
    print(f"👤 User: {user_message}")
    print(f"🤖 Model: {model}")
    print(f"{'='*60}")

    # ── Step 1: Kirim ke Ollama dengan tools ──
    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            tools=tools
        )
    except Exception as e:
        error_msg = f"❌ Gagal menghubungi Ollama: {str(e)}"
        print(error_msg)
        return error_msg

    # ── Step 2: Cek apakah LLM ingin memanggil tool ──
    if response["message"].get("tool_calls"):

        # Tambahkan response LLM ke history
        messages.append(response["message"])

        for tool_call in response["message"]["tool_calls"]:
            function_name = tool_call["function"]["name"]
            function_args = tool_call["function"]["arguments"]

            print(f"\n🔧 Tool dipanggil : {function_name}")
            print(f"📝 Parameter      : {json.dumps(function_args, indent=2, ensure_ascii=False)}")

            # ── Step 3: Eksekusi function ──
            if function_name in available_functions:
                try:
                    function_to_call = available_functions[function_name]
                    result = function_to_call(**function_args)

                    result_json = json.dumps(result, indent=2, default=str, ensure_ascii=False)
                    print(f"📊 Hasil query    :")
                    print(result_json)

                    # ── Step 4: Kirim hasil ke LLM ──
                    messages.append({
                        "role": "tool",
                        "content": result_json
                    })

                except Exception as e:
                    error_msg = f"Error menjalankan {function_name}: {str(e)}"
                    print(f"❌ {error_msg}")
                    messages.append({
                        "role": "tool",
                        "content": json.dumps({"error": error_msg})
                    })
            else:
                print(f"❌ Function '{function_name}' tidak ditemukan!")
                messages.append({
                    "role": "tool",
                    "content": json.dumps({"error": f"Function {function_name} tidak tersedia"})
                })

        # ── Step 5: Dapatkan jawaban final dari LLM ──
        try:
            final_response = ollama.chat(
                model=model,
                messages=messages
            )
            answer = final_response["message"]["content"]
        except Exception as e:
            answer = f"❌ Gagal mendapatkan response final: {str(e)}"

    else:
        # Jika tidak perlu tool, langsung ambil jawaban
        answer = response["message"]["content"]

    print(f"\n💬 Jawaban:")
    print(answer)
    print(f"{'='*60}\n")

    return answer
```

---

## File 5: `main.py`

```python
# main.py
# Entry point - Contoh penggunaan agent

from agent import run_agent
from config import OLLAMA_MODEL


def main():
    print("=" * 60)
    print("🏫 SISTEM ABSENSI SEKOLAH - AI AGENT")
    print(f"🤖 Model: {OLLAMA_MODEL}")
    print("=" * 60)
    print("Ketik pertanyaan tentang absensi, atau 'quit' untuk keluar.\n")

    # ── Mode 1: Contoh langsung ──
    contoh_pertanyaan = [
        "Siapa saja yang tidak hadir hari ini?",
        "Tampilkan rekap absensi siswa ID 5 bulan Februari 2026",
        "Berapa persentase kehadiran kelas ID 3?",
        "Siapa saja yang alfa hari ini?",
        "Tampilkan absensi siswa ID 10 dari tanggal 2026-02-01 sampai 2026-02-09",
    ]

    print("📋 Contoh pertanyaan yang bisa ditanyakan:")
    for i, q in enumerate(contoh_pertanyaan, 1):
        print(f"   {i}. {q}")
    print()

    # ── Mode 2: Interactive Chat ──
    while True:
        user_input = input("👤 Anda: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["quit", "exit", "q", "keluar"]:
            print("👋 Terima kasih! Sampai jumpa.")
            break

        # Cek apakah user memilih nomor contoh
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(contoh_pertanyaan):
                user_input = contoh_pertanyaan[idx]
                print(f"   → {user_input}")

        run_agent(user_input)


if __name__ == "__main__":
    main()
```

---

## Cara Menjalankan

```bash
# 1. Pastikan Ollama sudah running
ollama serve

# 2. Download model (pilih salah satu)
ollama pull qwen3:8b

# 3. Install dependencies
pip install ollama mysql-connector-python

# 4. Pastikan database MySQL sudah ada
#    (tabel: siswa, kelas, absensi)

# 5. Jalankan
python main.py
```

---

## Contoh Output

```
============================================================
🏫 SISTEM ABSENSI SEKOLAH - AI AGENT
🤖 Model: qwen3:8b
============================================================
Ketik pertanyaan tentang absensi, atau 'quit' untuk keluar.

👤 Anda: Siapa saja yang tidak hadir hari ini?

============================================================
👤 User: Siapa saja yang tidak hadir hari ini?
🤖 Model: qwen3:8b
============================================================

🔧 Tool dipanggil : get_siswa_tidak_hadir
📝 Parameter      : {
  "tanggal": "2026-02-09"
}
📊 Hasil query    :
[
  {
    "nama_siswa": "Ahmad Rizki",
    "nis": "2024001",
    "kelas": "10A",
    "status": "sakit",
    "keterangan": "Demam"
  },
  {
    "nama_siswa": "Siti Nurhaliza",
    "nis": "2024015",
    "kelas": "10B",
    "status": "izin",
    "keterangan": "Acara keluarga"
  },
  {
    "nama_siswa": "Budi Santoso",
    "nis": "2024023",
    "kelas": "11A",
    "status": "alfa",
    "keterangan": null
  }
]

💬 Jawaban:
Hari ini (9 Februari 2026) ada **3 siswa** yang tidak hadir:

1. **Ahmad Rizki** (NIS: 2024001, Kelas 10A) — Sakit (Demam)
2. **Siti Nurhaliza** (NIS: 2024015, Kelas 10B) — Izin (Acara keluarga)
3. **Budi Santoso** (NIS: 2024023, Kelas 11A) — Alfa (tanpa keterangan)
============================================================
```

---

## Struktur Final

```
absensi_agent/
├── config.py              ← Konfigurasi DB & model
├── tools_definition.py    ← Definisi 5 tools (OpenAI format)
├── db_functions.py        ← 5 fungsi SQL query
├── agent.py               ← Logic agent Ollama
└── main.py                ← Entry point + interactive chat
```

---

Mau saya tambahkan juga:
- **Schema SQL** untuk membuat tabel `siswa`, `kelas`, dan `absensi`?
- **FastAPI endpoint** supaya bisa diakses via REST API?
- **Logging ke file** untuk tracking semua query agent?