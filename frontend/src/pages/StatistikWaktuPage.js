import React, { useState } from 'react';
import { getStatistikWaktu } from '../services/api';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const StatistikWaktuPage = () => {
  const [formData, setFormData] = useState({
    kelas_id: '',
    nama_kelas: '',
    tanggal_mulai: '',
    tanggal_akhir: '',
    jam_telat: '07:15:00',
    limit: 10,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.tanggal_mulai || !formData.tanggal_akhir) {
      setError('Tanggal mulai dan tanggal akhir wajib diisi');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const params = {
        tanggal_mulai: formData.tanggal_mulai,
        tanggal_akhir: formData.tanggal_akhir,
        jam_telat: formData.jam_telat,
        limit: parseInt(formData.limit),
      };
      if (formData.kelas_id) params.kelas_id = parseInt(formData.kelas_id);
      if (formData.nama_kelas) params.nama_kelas = formData.nama_kelas;

      const response = await getStatistikWaktu(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const distributionChart = result?.distribusi_jam ? {
    labels: result.distribusi_jam.map(d => d.jam),
    datasets: [{
      label: 'Jumlah Absensi',
      data: result.distribusi_jam.map(d => d.jumlah),
      backgroundColor: result.distribusi_jam.map(d => {
        const hour = parseInt(d.jam);
        if (hour < 7) return 'rgba(23, 162, 184, 0.7)';
        if (hour === 7) return 'rgba(40, 167, 69, 0.7)';
        return 'rgba(255, 193, 7, 0.7)';
      }),
      borderWidth: 1,
    }]
  } : null;

  const distributionOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Distribusi Waktu Absensi per Jam' },
    },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: 'Jumlah' } },
      x: { title: { display: true, text: 'Jam' } },
    },
  };

  const telatChart = result?.siswa_sering_telat ? {
    labels: result.siswa_sering_telat.map(s => s.nama_siswa),
    datasets: [{
      label: 'Jumlah Telat',
      data: result.siswa_sering_telat.map(s => s.jumlah_telat),
      backgroundColor: 'rgba(220, 53, 69, 0.7)',
      borderWidth: 1,
    }]
  } : null;

  const telatOptions = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: `Siswa Sering Telat (setelah ${formData.jam_telat})` },
    },
  };

  return (
    <div className="space-y-6">
      <div className="text-center py-4">
        <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center mb-3 mx-auto">
          <span className="material-icons-round text-2xl text-indigo-600">schedule</span>
        </div>
        <h1 className="text-2xl font-bold text-foreground">Statistik Waktu Absen</h1>
        <p className="text-muted-foreground text-sm">Analisis distribusi waktu absensi dan identifikasi siswa yang sering telat</p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6">
        <h2 className="font-semibold text-foreground mb-4">Parameter</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Nama Kelas (opsional)</label>
              <input type="text" name="nama_kelas" value={formData.nama_kelas} onChange={handleChange}
                placeholder="Contoh: X RPL 1"
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Jam Batas Telat</label>
              <input type="time" name="jam_telat" value={formData.jam_telat} onChange={handleChange} step="1"
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Tanggal Mulai *</label>
              <input type="date" name="tanggal_mulai" value={formData.tanggal_mulai} onChange={handleChange} required
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Tanggal Akhir *</label>
              <input type="date" name="tanggal_akhir" value={formData.tanggal_akhir} onChange={handleChange} required
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Limit</label>
              <input type="number" name="limit" value={formData.limit} onChange={handleChange} min="1" max="50"
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground text-sm" />
            </div>
          </div>
          <button type="submit" disabled={loading}
            className="bg-primary hover:opacity-90 text-primary-foreground font-medium py-2.5 px-6 rounded-lg transition-all disabled:opacity-50">
            {loading ? 'Memproses...' : 'Tampilkan Statistik'}
          </button>
        </form>
      </div>

      {error && <div className="bg-destructive/10 text-destructive border border-destructive/20 rounded-xl p-4 text-sm">{error}</div>}

      {result && (
        <div className="space-y-4">
          {result.ringkasan && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-foreground mb-4">Ringkasan</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(result.ringkasan).map(([key, value]) => (
                  <div key={key} className="bg-accent/50 rounded-lg p-3 text-center">
                    <p className="text-xs text-muted-foreground mb-1">{key.replace(/_/g, ' ')}</p>
                    <p className="text-lg font-bold text-foreground">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {distributionChart && (
            <div className="bg-card border border-border rounded-xl p-6">
              <Bar data={distributionChart} options={distributionOptions} />
            </div>
          )}

          {telatChart && result.siswa_sering_telat.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-6">
              <Bar data={telatChart} options={telatOptions} />
            </div>
          )}

          {result.siswa_sering_telat && result.siswa_sering_telat.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-foreground mb-4">Detail Siswa Sering Telat</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left p-2 font-medium text-muted-foreground">#</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Nama Siswa</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">NIS</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Kelas</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Jumlah Telat</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Rata-rata Jam</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.siswa_sering_telat.map((s, idx) => (
                      <tr key={idx} className="border-b border-border hover:bg-accent/50">
                        <td className="p-2 text-muted-foreground">{idx + 1}</td>
                        <td className="p-2 font-medium text-foreground">{s.nama_siswa}</td>
                        <td className="p-2 text-foreground">{s.nis || '-'}</td>
                        <td className="p-2 text-foreground">{s.kelas || '-'}</td>
                        <td className="p-2">
                          <span className="font-bold text-red-600">{s.jumlah_telat}</span>
                        </td>
                        <td className="p-2 text-foreground">{s.rata_rata_jam || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {result.distribusi_jam && result.distribusi_jam.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-foreground mb-4">Detail Distribusi per Jam</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left p-2 font-medium text-muted-foreground">Jam</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Jumlah</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Persentase</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.distribusi_jam.map((d, idx) => (
                      <tr key={idx} className="border-b border-border hover:bg-accent/50">
                        <td className="p-2 font-medium text-foreground">{d.jam}:00</td>
                        <td className="p-2 text-foreground">{d.jumlah}</td>
                        <td className="p-2 text-foreground">{d.persentase || '-'}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {(!result.distribusi_jam?.length && !result.siswa_sering_telat?.length && !result.ringkasan) && (
            <div className="bg-accent/50 text-muted-foreground border border-border rounded-xl p-4 text-sm text-center">
              Tidak ada data statistik waktu untuk periode ini.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StatistikWaktuPage;
