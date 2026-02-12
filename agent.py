# agent.py
# Agent Router menggunakan Ollama

import ollama
import json
from config import OLLAMA_MODEL, SYSTEM_PROMPT
from tools_definition import tools
from db_functions import (
    cari_siswa,
    get_siswa_by_kelas,
    get_absensi_by_siswa,
    get_absensi_by_kelas,
    get_siswa_tidak_hadir,
    get_rekap_absensi,
    get_rekap_absensi_bulanan,
    get_persentase_kehadiran,
    buat_surat_peringatan_alfa,
    buat_laporan_alfa,
    get_attendance_trends,
    get_geolocation_analysis,
    compare_class_attendance,
    get_ringkasan_absensi_harian,
    get_ringkasan_absensi_range,
    get_rekap_absensi_kelas_range,
    get_top_siswa_absensi,
    get_analisis_metode_absen,
    get_anomali_absensi,
    get_statistik_waktu_absen,
)


# ============================================
# MAPPING: nama function → function Python
# ============================================
available_functions = {
    "cari_siswa": cari_siswa,
    "get_siswa_by_kelas": get_siswa_by_kelas,
    "get_absensi_by_siswa": get_absensi_by_siswa,
    "get_absensi_by_kelas": get_absensi_by_kelas,
    "get_siswa_tidak_hadir": get_siswa_tidak_hadir,
    "get_rekap_absensi": get_rekap_absensi,
    "get_rekap_absensi_bulanan": get_rekap_absensi_bulanan,
    "get_persentase_kehadiran": get_persentase_kehadiran,
    "buat_surat_peringatan_alfa": buat_surat_peringatan_alfa,
    "buat_laporan_alfa": buat_laporan_alfa,
    "get_attendance_trends": get_attendance_trends,
    "get_geolocation_analysis": get_geolocation_analysis,
    "compare_class_attendance": compare_class_attendance,
    "get_ringkasan_absensi_harian": get_ringkasan_absensi_harian,
    "get_ringkasan_absensi_range": get_ringkasan_absensi_range,
    "get_rekap_absensi_kelas_range": get_rekap_absensi_kelas_range,
    "get_top_siswa_absensi": get_top_siswa_absensi,
    "get_analisis_metode_absen": get_analisis_metode_absen,
    "get_anomali_absensi": get_anomali_absensi,
    "get_statistik_waktu_absen": get_statistik_waktu_absen,
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
    6. LLM memberikan analisis 
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