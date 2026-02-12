import React from 'react';
import { Link } from 'react-router-dom';

const features = [
  {
    icon: 'smart_toy',
    title: 'Chat dengan AI',
    desc: 'Tanyakan apa saja tentang absensi siswa dalam bahasa alami.',
    link: '/chat',
    color: 'bg-blue-500/10 text-blue-600',
  },
  {
    icon: 'trending_up',
    title: 'Tren Kehadiran',
    desc: 'Analisis tren kehadiran siswa atau kelas dalam beberapa bulan terakhir.',
    link: '/trends',
    color: 'bg-green-500/10 text-green-600',
  },
  {
    icon: 'location_on',
    title: 'Analisis Lokasi',
    desc: 'Validasi data geolokasi absensi dan deteksi anomali lokasi.',
    link: '/geolocation',
    color: 'bg-orange-500/10 text-orange-600',
  },
  {
    icon: 'compare_arrows',
    title: 'Perbandingan Kelas',
    desc: 'Bandingkan tingkat kehadiran antar kelas untuk evaluasi performa.',
    link: '/comparison',
    color: 'bg-purple-500/10 text-purple-600',
  },
];

const HomePage = () => {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-8">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4 mx-auto">
          <span className="material-icons-round text-4xl text-primary">school</span>
        </div>
        <h1 className="text-3xl font-bold text-foreground mb-2">
          EduAttend <span className="text-primary">AI</span>
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Sistem berbasis AI untuk mengelola dan menganalisis data absensi siswa. 
          Powered by LLM untuk analisis cerdas.
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {features.map((f, idx) => (
          <Link
            key={idx}
            to={f.link}
            className="bg-card border border-border rounded-xl p-6 hover:shadow-lg transition-all group no-underline"
          >
            <div className="flex items-start gap-4">
              <div className={`w-12 h-12 rounded-xl ${f.color} flex items-center justify-center flex-shrink-0`}>
                <span className="material-icons-round text-2xl">{f.icon}</span>
              </div>
              <div>
                <h3 className="font-semibold text-foreground text-lg mb-1 group-hover:text-primary transition-colors">
                  {f.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{f.desc}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Usage Guide */}
      <div className="bg-card border border-border rounded-xl p-6">
        <h2 className="font-semibold text-foreground text-lg mb-4 flex items-center gap-2">
          <span className="material-icons-round text-primary">help_outline</span>
          Cara Penggunaan
        </h2>
        <ol className="space-y-3 text-sm text-muted-foreground list-decimal list-inside">
          <li><strong className="text-foreground">Chat dengan AI</strong> — Tanyakan pertanyaan seperti "Siapa saja yang alfa hari ini?" atau "Buatkan surat peringatan untuk Budi"</li>
          <li><strong className="text-foreground">Tren Kehadiran</strong> — Analisis pola kehadiran siswa/kelas dalam periode waktu tertentu</li>
          <li><strong className="text-foreground">Analisis Lokasi</strong> — Deteksi kecurangan atau anomali dalam data geolokasi absensi</li>
          <li><strong className="text-foreground">Perbandingan Kelas</strong> — Bandingkan performa kehadiran antar kelas untuk evaluasi</li>
        </ol>
      </div>
    </div>
  );
};

export default HomePage;
