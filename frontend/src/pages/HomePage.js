import React from 'react';

const HomePage = () => {
  return (
    <div>
      <div className="header">
        <h1>🏫 Sistem Absensi Sekolah</h1>
        <p>Sistem berbasis AI untuk mengelola dan menganalisis data absensi siswa</p>
      </div>

      <div className="card">
        <h2>Fitur Utama</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          <div className="card" style={{ flex: 1, minWidth: '250px' }}>
            <h3>💬 Chat dengan AI</h3>
            <p>Tanyakan apa saja tentang absensi siswa dalam bahasa alami.</p>
            <a href="/chat" className="btn">Mulai Chat</a>
          </div>

          <div className="card" style={{ flex: 1, minWidth: '250px' }}>
            <h3>📈 Tren Kehadiran</h3>
            <p>Analisis tren kehadiran siswa atau kelas dalam beberapa bulan terakhir.</p>
            <a href="/trends" className="btn">Lihat Tren</a>
          </div>

          <div className="card" style={{ flex: 1, minWidth: '250px' }}>
            <h3>📍 Analisis Lokasi</h3>
            <p>Validasi data geolokasi absensi dan deteksi anomali lokasi.</p>
            <a href="/geolocation" className="btn">Analisis Lokasi</a>
          </div>

          <div className="card" style={{ flex: 1, minWidth: '250px' }}>
            <h3>📊 Perbandingan Kelas</h3>
            <p>Bandingkan tingkat kehadiran antar kelas untuk evaluasi performa.</p>
            <a href="/comparison" className="btn">Bandingkan Kelas</a>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Cara Penggunaan</h2>
        <ol>
          <li><strong>Chat dengan AI</strong>: Tanyakan pertanyaan seperti "Siapa saja yang alfa hari ini?" atau "Buatkan surat peringatan untuk Budi"</li>
          <li><strong>Tren Kehadiran</strong>: Analisis pola kehadiran siswa/kelas dalam periode waktu tertentu</li>
          <li><strong>Analisis Lokasi</strong>: Deteksi kecurangan atau anomali dalam data geolokasi absensi</li>
          <li><strong>Perbandingan Kelas</strong>: Bandingkan performa kehadiran antar kelas untuk evaluasi</li>
        </ol>
      </div>
    </div>
  );
};

export default HomePage;