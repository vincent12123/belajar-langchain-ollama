# Dokumentasi Frontend - Sistem Absensi Sekolah

Dokumen ini menjelaskan struktur, fitur, dan cara penggunaan aplikasi Frontend untuk Sistem Absensi Sekolah. Aplikasi ini dibangun menggunakan React.js dan menyediakan antarmuka untuk berinteraksi dengan backend AI dan visualisasi data absensi.

## 🛠️ Teknologi yang Digunakan

*   **React**: Framework UI utama (v18.2.0).
*   **React Router DOM**: Untuk manajemen routing halaman.
*   **Axios**: Untuk melakukan HTTP request ke backend API.
*   **Chart.js & React-Chartjs-2**: Untuk membuat grafik visualisasi data trends dan perbandingan.
*   **Create React App**: Digunakan sebagai boilerplate project.

## 📂 Struktur Folder

```
frontend/
├── public/                 # File statis (index.html, favicon, dll)
├── src/                    # Source code aplikasi
│   ├── pages/              # Komponen Halaman (Views)
│   │   ├── AttendanceTrendsPage.js   # Halaman Tren Kehadiran
│   │   ├── ChatPage.js               # Halaman Chat dengan AI
│   │   ├── ClassComparisonPage.js    # Halaman Perbandingan Kelas
│   │   ├── GeolocationAnalysisPage.js # Halaman Analisis Lokasi
│   │   └── HomePage.js               # Halaman Utama
│   ├── services/           # Layanan API
│   │   └── api.js          # Konfigurasi Axios & Fungsi API
│   ├── App.js              # Komponen Utama & Routing
│   ├── App.css             # Styling global
│   ├── index.js            # Entry point aplikasi
│   └── index.css           # Styling dasar
├── package.json            # Daftar dependensi & script
└── README.md               # Dokumentasi bawaan Create React App
```

## 🚀 Cara Menjalankan

### Prasyarat
*   Node.js terinstall.
*   Backend API berjalan di `http://localhost:8000`.

### Langkah-langkah
1.  Buka terminal dan masuk ke folder frontend:
    ```bash
    cd frontend
    ```
2.  Install dependensi (hanya perlu dilakukan sekali):
    ```bash
    npm install
    ```
3.  Jalankan server development:
    ```bash
    npm start
    ```
4.  Buka browser di `http://localhost:3000`.

## 📄 Fitur & Halaman

### 1. Home (Beranda)
*   **Route**: `/`
*   **Deskripsi**: Halaman penyambut yang memberikan ringkasan fitur aplikasi.

### 2. Chat AI
*   **Route**: `/chat`
*   **Deskripsi**: Antarmuka chat interaktif yang memungkinkan pengguna bertanya kepada AI (Agent) mengenai data absensi.
*   **Fitur**:
    *   Input pesan teks.
    *   Tampilan riwayat chat (User & Assistant).
    *   Integrasi ke endpoint `/chat`.

### 3. Tren Kehadiran (Attendance Trends)
*   **Route**: `/trends`
*   **Deskripsi**: Menampilkan grafik tren kehadiran siswa atau kelas dalam periode waktu tertentu.
*   **Fitur**:
    *   Form filter berdasarkan ID Siswa, Nama Siswa, ID Kelas, atau Nama Kelas.
    *   Visualisasi grafik batang (Bar Chart) menggunakan Chart.js.
    *   Integrasi ke endpoint `/api/attendance/trends`.

### 4. Analisis Lokasi (Geolocation Analysis)
*   **Route**: `/geolocation`
*   **Deskripsi**: Menganalisis data lokasi absensi siswa.
*   **Fitur**:
    *   Form filter berdasarkan Kelas dan Tanggal.
    *   Menampilkan data siswa yang melakukan absensi di luar radius yang diizinkan (jika ada).
    *   Integrasi ke endpoint `/api/geolocation/analysis`.

### 5. Perbandingan Kelas (Class Comparison)
*   **Route**: `/comparison`
*   **Deskripsi**: Membandingkan statistik kehadiran antar kelas.
*   **Fitur**:
    *   Form filter berdasarkan Tingkat Kelas (misal: 10, 11, 12) dan Jurusan.
    *   Visualisasi grafik perbandingan persentase kehadiran.
    *   Integrasi ke endpoint `/api/class/comparison`.

## 🔌 API Services (`src/services/api.js`)

File ini mengatur komunikasi dengan backend. Base URL secara default diatur ke `http://localhost:8000`.

*   `chatWithAI(message, model)`: Mengirim pertanyaan ke AI Agent.
*   `getAttendanceTrends(params)`: Mengambil data tren kehadiran.
*   `getGeolocationAnalysis(params)`: Mengambil analisis geolokasi.
*   `getClassComparison(params)`: Mengambil data perbandingan kelas.
*   `searchStudents(name)`: Mencari siswa berdasarkan nama.
*   `getStudentAttendance(studentId, start, end)`: Mengambil riwayat absensi spesifik siswa.

## ⚠️ Troubleshooting

*   **Error 422 Unprocessable Content**: Pastikan format data yang dikirim sesuai dengan yang diharapkan backend (perhatikan nama field JSON).
*   **Connection Refused**: Pastikan server backend FastAPI sudah berjalan (`uvicorn api:app --reload`).
*   **Module not found**: Coba jalankan `npm install` kembali jika ada dependensi yang hilang.
