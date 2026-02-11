# Sistem Absensi Sekolah - Frontend React

Frontend React.js untuk sistem absensi sekolah berbasis AI.

## Fitur

1. **Chat dengan AI** - Tanyakan pertanyaan natural language tentang absensi
2. **Analisis Tren Kehadiran** - Visualisasi tren kehadiran siswa/kelas
3. **Analisis Geolokasi** - Validasi data geolokasi absensi
4. **Perbandingan Kelas** - Bandingkan tingkat kehadiran antar kelas

## Teknologi yang Digunakan

- React.js 18
- Axios untuk API calls
- Chart.js untuk visualisasi data
- React Router untuk navigasi
- FastAPI sebagai backend

## Cara Instalasi

1. Pastikan Anda berada di direktori `frontend`:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Cara Menjalankan

1. Jalankan development server:
   ```
   npm start
   ```

2. Buka browser di http://localhost:3000

## Struktur Direktori

```
frontend/
├── public/           # File statis
├── src/
│   ├── components/   # Komponen React reusable
│   ├── pages/        # Halaman aplikasi
│   ├── services/     # Service API
│   ├── assets/       # Asset seperti gambar
│   ├── App.js        # Komponen utama
│   ├── App.css       # Styling utama
│   └── index.js      # Entry point
├── package.json      # Dependencies dan scripts
└── README.md         # Dokumentasi ini
```

## Integrasi dengan Backend

Frontend berkomunikasi dengan backend FastAPI melalui API endpoints:

- `POST /chat` - Chat dengan AI
- `POST /api/attendance/trends` - Analisis tren kehadiran
- `POST /api/geolocation/analysis` - Analisis geolokasi
- `POST /api/class/comparison` - Perbandingan kelas

## Pengembangan Lebih Lanjut

Untuk menambahkan fitur baru:

1. Buat komponen baru di `src/components/`
2. Tambahkan halaman baru di `src/pages/`
3. Tambahkan service API di `src/services/`
4. Tambahkan route di `src/App.js`

## Deployment

Untuk build production:
```
npm run build
```

File hasil build akan tersedia di direktori `build/` yang dapat di-deploy ke server web.