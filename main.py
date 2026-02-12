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
        "Analisis metode absen kelas 10A bulan ini",
        "Siapa top 5 siswa paling rajin absen di kelas 11B?",
        "Cek anomali absensi di kelas 12C",
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