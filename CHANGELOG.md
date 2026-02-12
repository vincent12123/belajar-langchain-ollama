# Changelog

Semua perubahan penting pada project ini didokumentasikan di file ini.

---

## [2026-02-13] - Chat Memory & Date Suggestion

### Ditambahkan

#### 1. Komponen `DateSuggestion` (Frontend)
- **File:** `frontend/src/components/DateSuggestion.js` *(baru)*
- Komponen yang mendeteksi konteks tanggal dari pesan terakhir assistant
- Menampilkan tombol quick-pick tanggal di area chat:
  - **Mode tunggal:** Hari Ini, Kemarin, Awal Bulan
  - **Mode rentang:** Minggu Ini, Bulan Ini, Bulan Lalu
  - **Custom date picker** dengan input manual (1 atau 2 tanggal)
- Deteksi otomatis mode tunggal vs rentang berdasarkan keyword di pesan assistant
- Pesan yang dikirim bersifat **kontekstual** — mengambil pertanyaan user terakhir dan menyisipkan tanggal yang dipilih
  - Contoh: user tanya *"Siapa yang alfa?"* → klik Hari Ini → kirim *"Siapa yang alfa? pada tanggal 2026-02-13"*
  - Contoh range: user tanya *"Rekap absensi kelas X RPL 1"* → klik Bulan Ini → kirim *"Rekap absensi kelas X RPL 1 dari tanggal 2026-02-01 sampai 2026-02-13"*

#### 2. Chat Memory / Riwayat Percakapan (Backend)
- **File:** `agent.py` — Ditambahkan fungsi `run_agent_with_history()`
  - Menerima parameter `chat_history` (list riwayat percakapan)
  - Menyisipkan maks 20 pesan terakhir ke konteks Ollama
  - AI sekarang memahami konteks percakapan sebelumnya
  - `run_agent()` tetap berfungsi (backward compatible, tanpa history)

- **File:** `api.py` — Endpoint `/api/chat` diperbarui
  - Mengekstrak seluruh riwayat pesan dari request AI SDK (bukan hanya pesan terakhir)
  - Meneruskan history ke `run_agent_with_history()`
  - Mendukung format AI SDK v4 (`content`) dan v5 (`parts`)

#### 3. CSS Animasi Date Picker
- **File:** `frontend/src/custom-styles.css`
  - Ditambahkan animasi `slideInFromTop` untuk date picker custom
  - Styling untuk input `date` agar konsisten

### Diperbaiki

#### 4. Tombol Quick Action & Suggestion Tidak Berfungsi
- **File:** `frontend/src/pages/ChatPage.js`
  - **Masalah:** `handleSuggestionClick` dan `handleDateSelect` menggunakan API lama (`handleSubmit`, `setInput`, `append`) yang tidak ada di `@ai-sdk/react` v3.x
  - **Solusi:** Diganti menggunakan `handler.sendMessage({ text })` yang merupakan API resmi v3
  - Semua tombol (Pertanyaan Cepat di sidebar, suggestion chips di welcome screen, dan date picker) sekarang berfungsi

#### 5. ESLint Warning `no-useless-escape`
- **File:** `frontend/src/components/PdfDownloadDetector.js`
  - Pindahkan `-` ke akhir character class regex (`[...-]`) untuk menghilangkan unnecessary escape

---

### Daftar File yang Diubah

| File | Aksi | Keterangan |
|------|------|------------|
| `agent.py` | Diubah | Tambah `run_agent_with_history()` untuk chat memory |
| `api.py` | Diubah | Kirim full history ke agent, bukan hanya pesan terakhir |
| `frontend/src/components/DateSuggestion.js` | Baru | Komponen date suggestion dengan quick-pick & custom picker |
| `frontend/src/components/PdfDownloadDetector.js` | Diubah | Fix ESLint regex warning |
| `frontend/src/pages/ChatPage.js` | Diubah | Fix `sendMessage` API, integrasi DateSuggestion |
| `frontend/src/custom-styles.css` | Diubah | Tambah animasi & styling date picker |
