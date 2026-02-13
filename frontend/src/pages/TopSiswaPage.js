import React, { useState } from 'react';
import { getTopSiswa } from '../services/api';
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

const TopSiswaPage = () => {
  const [formData, setFormData] = useState({
    kelas_id: '',
    nama_kelas: '',
    tanggal_mulai: '',
    tanggal_akhir: '',
    status: 'Alfa',
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
        status: formData.status,
        limit: parseInt(formData.limit),
      };
      if (formData.kelas_id) params.kelas_id = parseInt(formData.kelas_id);
      if (formData.nama_kelas) params.nama_kelas = formData.nama_kelas;

      const response = await getTopSiswa(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const statusColor = {
    Alfa: 'rgba(220, 53, 69, 0.7)',
    Sakit: 'rgba(255, 193, 7, 0.7)',
    Izin: 'rgba(23, 162, 184, 0.7)',
    Hadir: 'rgba(40, 167, 69, 0.7)',
  };

  const chartData = result?.data ? {
    labels: result.data.map(s => s.nama_siswa),
    datasets: [{
      label: `Jumlah ${formData.status}`,
      data: result.data.map(s => s.jumlah),
      backgroundColor: statusColor[formData.status] || 'rgba(74, 105, 189, 0.7)',
      borderWidth: 1,
    }]
  } : null;

  const chartOptions = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: `Top Siswa - ${formData.status}` },
    },
  };

  return (
    <div className="space-y-6">
      <div className="text-center py-4">
        <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center mb-3 mx-auto">
          <span className="material-icons-round text-2xl text-amber-600">leaderboard</span>
        </div>
        <h1 className="text-2xl font-bold text-foreground">Top Siswa Absensi</h1>
        <p className="text-muted-foreground text-sm">Ranking siswa berdasarkan jumlah status tertentu (Alfa, Sakit, Izin, Hadir)</p>
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
              <label className="block text-sm font-medium text-foreground mb-1">Status</label>
              <select name="status" value={formData.status} onChange={handleChange}
                className="w-full px-3 py-2 border border-input rounded-lg bg-background text-foreground text-sm">
                <option value="Alfa">Alfa</option>
                <option value="Sakit">Sakit</option>
                <option value="Izin">Izin</option>
                <option value="Hadir">Hadir</option>
              </select>
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
            {loading ? 'Memproses...' : 'Tampilkan Ranking'}
          </button>
        </form>
      </div>

      {error && <div className="bg-destructive/10 text-destructive border border-destructive/20 rounded-xl p-4 text-sm">{error}</div>}

      {result && result.data && (
        <div className="space-y-4">
          {chartData && (
            <div className="bg-card border border-border rounded-xl p-6">
              <Bar data={chartData} options={chartOptions} />
            </div>
          )}

          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="font-semibold text-foreground mb-4">Data Detail</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left p-2 font-medium text-muted-foreground">#</th>
                    <th className="text-left p-2 font-medium text-muted-foreground">Nama Siswa</th>
                    <th className="text-left p-2 font-medium text-muted-foreground">NIS</th>
                    <th className="text-left p-2 font-medium text-muted-foreground">Kelas</th>
                    <th className="text-left p-2 font-medium text-muted-foreground">Jumlah {formData.status}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.data.map((s, idx) => (
                    <tr key={idx} className="border-b border-border hover:bg-accent/50">
                      <td className="p-2 text-muted-foreground">{idx + 1}</td>
                      <td className="p-2 font-medium text-foreground">{s.nama_siswa}</td>
                      <td className="p-2 text-foreground">{s.nis}</td>
                      <td className="p-2 text-foreground">{s.kelas}</td>
                      <td className="p-2">
                        <span className={`font-bold ${
                          formData.status === 'Alfa' ? 'text-red-600' :
                          formData.status === 'Sakit' ? 'text-yellow-600' :
                          formData.status === 'Izin' ? 'text-cyan-600' : 'text-green-600'
                        }`}>{s.jumlah}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TopSiswaPage;