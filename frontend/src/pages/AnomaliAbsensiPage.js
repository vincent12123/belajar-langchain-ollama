import React, { useState } from 'react';
import { getAnomaliAbsensi } from '../services/api';

const AnomaliAbsensiPage = () => {
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

      const response = await getAnomaliAbsensi(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderAnomalySection = (title, icon, items, color) => {
    if (!items || items.length === 0) return null;
    return (
      <div className="bg-card border border-border rounded-xl p-5 mb-4">
        <h3 className="font-semibold text-foreground flex items-center gap-2 mb-3">
          <span className={`material-icons-round ${color}`}>{icon}</span>
          {title}
          <span className="text-xs bg-destructive/10 text-destructive px-2 py-0.5 rounded-full ml-2">
            {items.length} ditemukan
          </span>
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                {Object.keys(items[0]).map((key) => (
                  <th key={key} className="text-left p-2 font-medium text-muted-foreground">{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.slice(0, 20).map((item, idx) => (
                <tr key={idx} className="border-b border-border hover:bg-accent/50">
                  {Object.values(item).map((val, i) => (
                    <td key={i} className="p-2 text-foreground">{String(val)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="text-center py-4">
        <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center mb-3 mx-auto">
          <span className="material-icons-round text-2xl text-red-600">warning</span>
        </div>
        <h1 className="text-2xl font-bold text-foreground">Deteksi Anomali Absensi</h1>
        <p className="text-muted-foreground text-sm">Deteksi jarak terlalu jauh, koordinat kosong, dan koordinat identik</p>
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
            {loading ? 'Memproses...' : 'Deteksi Anomali'}
          </button>
        </form>
      </div>

      {error && <div className="bg-destructive/10 text-destructive border border-destructive/20 rounded-xl p-4 text-sm">{error}</div>}

      {result && (
        <div className="space-y-4">
          {renderAnomalySection('Jarak Terlalu Jauh', 'place', result.jarak_jauh, 'text-orange-500')}
          {renderAnomalySection('Koordinat Kosong (Non-Manual)', 'gps_off', result.koordinat_kosong, 'text-yellow-600')}
          {renderAnomalySection('Koordinat Identik', 'group', result.koordinat_identik, 'text-red-500')}

          {(!result.jarak_jauh?.length && !result.koordinat_kosong?.length && !result.koordinat_identik?.length) && (
            <div className="bg-green-500/10 text-green-700 border border-green-500/20 rounded-xl p-4 text-sm text-center">
              Tidak ditemukan anomali pada periode ini.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnomaliAbsensiPage;