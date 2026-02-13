import React, { useState } from 'react';
import { getAnalisisMetode } from '../services/api';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const COLORS = [
  'rgba(74, 105, 189, 0.7)',
  'rgba(40, 167, 69, 0.7)',
  'rgba(255, 193, 7, 0.7)',
  'rgba(220, 53, 69, 0.7)',
  'rgba(111, 66, 193, 0.7)',
  'rgba(23, 162, 184, 0.7)',
];

const AnalisisMetodePage = () => {
  const [formData, setFormData] = useState({
    kelas_id: '',
    nama_kelas: '',
    tanggal_mulai: '',
    tanggal_akhir: '',
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
      };
      if (formData.kelas_id) params.kelas_id = parseInt(formData.kelas_id);
      if (formData.nama_kelas) params.nama_kelas = formData.nama_kelas;

      const response = await getAnalisisMetode(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result?.per_metode ? {
    labels: result.per_metode.map(m => m.metode || 'Tidak diketahui'),
    datasets: [{
      data: result.per_metode.map(m => m.total),
      backgroundColor: COLORS.slice(0, result.per_metode.length),
      borderWidth: 1,
    }]
  } : null;

  return (
    <div className="space-y-6">
      <div className="text-center py-4">
        <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center mb-3 mx-auto">
          <span className="material-icons-round text-2xl text-cyan-600">fingerprint</span>
        </div>
        <h1 className="text-2xl font-bold text-foreground">Analisis Metode Absen</h1>
        <p className="text-muted-foreground text-sm">Breakdown metode absen (GPS, manual, QR, dll) dan status per metode</p>
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
              <label className="block text-sm font-medium text-foreground mb-1">ID Kelas (opsional)</label>
              <input type="number" name="kelas_id" value={formData.kelas_id} onChange={handleChange}
                placeholder="ID kelas"
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
          </div>
          <button type="submit" disabled={loading}
            className="bg-primary hover:opacity-90 text-primary-foreground font-medium py-2.5 px-6 rounded-lg transition-all disabled:opacity-50">
            {loading ? 'Memproses...' : 'Analisis Metode'}
          </button>
        </form>
      </div>

      {error && <div className="bg-destructive/10 text-destructive border border-destructive/20 rounded-xl p-4 text-sm">{error}</div>}

      {result && (
        <div className="space-y-4">
          {/* Chart */}
          {chartData && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-foreground mb-4">Distribusi Metode Absen</h3>
              <div className="max-w-sm mx-auto">
                <Doughnut data={chartData} />
              </div>
            </div>
          )}

          {/* Table per metode */}
          {result.per_metode && result.per_metode.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-semibold text-foreground mb-4">Detail Per Metode</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left p-2 font-medium text-muted-foreground">Metode</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Total</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Hadir</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Izin</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Sakit</th>
                      <th className="text-left p-2 font-medium text-muted-foreground">Alfa</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.per_metode.map((m, idx) => (
                      <tr key={idx} className="border-b border-border hover:bg-accent/50">
                        <td className="p-2 font-medium text-foreground">{m.metode || 'Tidak diketahui'}</td>
                        <td className="p-2 text-foreground">{m.total}</td>
                        <td className="p-2 text-green-600">{m.hadir || 0}</td>
                        <td className="p-2 text-blue-600">{m.izin || 0}</td>
                        <td className="p-2 text-yellow-600">{m.sakit || 0}</td>
                        <td className="p-2 text-red-600">{m.alfa || 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalisisMetodePage;