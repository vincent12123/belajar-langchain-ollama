import React, { useState } from 'react';
import { getGeolocationAnalysis } from '../services/api';

const GeolocationAnalysisPage = () => {
  const [formData, setFormData] = useState({
    kelas_id: '',
    nama_kelas: '',
    tanggal: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const params = {};

      // Only include non-empty fields
      if (formData.kelas_id) params.kelas_id = parseInt(formData.kelas_id);
      if (formData.nama_kelas) params.nama_kelas = formData.nama_kelas;
      if (formData.tanggal) params.tanggal = formData.tanggal;

      const response = await getGeolocationAnalysis(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="header">
        <h1>📍 Analisis Geolokasi Absensi</h1>
        <p>Menganalisis data geolokasi untuk validasi absensi dan mendeteksi anomali</p>
      </div>

      <div className="card">
        <h2>Parameter Pencarian</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="kelas_id">ID Kelas (opsional):</label>
            <input
              type="number"
              id="kelas_id"
              name="kelas_id"
              value={formData.kelas_id}
              onChange={handleChange}
              placeholder="Masukkan ID kelas"
            />
          </div>

          <div className="form-group">
            <label htmlFor="nama_kelas">Nama Kelas (opsional):</label>
            <input
              type="text"
              id="nama_kelas"
              name="nama_kelas"
              value={formData.nama_kelas}
              onChange={handleChange}
              placeholder="Masukkan nama kelas (contoh: X RPL 1)"
            />
          </div>

          <div className="form-group">
            <label htmlFor="tanggal">Tanggal (opsional):</label>
            <input
              type="date"
              id="tanggal"
              name="tanggal"
              value={formData.tanggal}
              onChange={handleChange}
            />
          </div>

          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Memproses...' : 'Analisis Lokasi'}
          </button>
        </form>
      </div>

      {error && (
        <div className="card">
          <div className="error">{error}</div>
        </div>
      )}

      {result && (
        <div className="card">
          <h2>Hasil Analisis</h2>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', marginBottom: '20px' }}>
            <div className="card" style={{ flex: 1, minWidth: '200px' }}>
              <h3>Total Records</h3>
              <p style={{ fontSize: '2em', textAlign: 'center', color: '#4a69bd' }}>
                {result.total_records}
              </p>
            </div>

            <div className="card" style={{ flex: 1, minWidth: '200px' }}>
              <h3>Koordinat Valid</h3>
              <p style={{ fontSize: '2em', textAlign: 'center', color: '#28a745' }}>
                {result.valid_coordinates}
              </p>
            </div>

            <div className="card" style={{ flex: 1, minWidth: '200px' }}>
              <h3>% Koordinat Valid</h3>
              <p style={{ fontSize: '2em', textAlign: 'center', color: '#ffc107' }}>
                {result.percentage_valid_coordinates}%
              </p>
            </div>

            <div className="card" style={{ flex: 1, minWidth: '200px' }}>
              <h3>Lokasi Mencurigakan</h3>
              <p style={{ fontSize: '2em', textAlign: 'center', color: '#dc3545' }}>
                {result.flagged_records_count}
              </p>
            </div>
          </div>

          {result.suspicious_locations && result.suspicious_locations.length > 0 && (
            <div className="card">
              <h3>Lokasi Mencurigakan Terdeteksi</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Koordinat</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Jumlah Siswa</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Tanggal</th>
                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Siswa</th>
                  </tr>
                </thead>
                <tbody>
                  {result.suspicious_locations.map((location, index) => (
                    <tr key={index}>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{location.coordinates}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{location.student_count}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>{location.tanggal}</td>
                      <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                        {location.students.join(', ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {(!result.suspicious_locations || result.suspicious_locations.length === 0) && (
            <div className="success">
              Tidak ditemukan lokasi mencurigakan. Data geolokasi tampak valid.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GeolocationAnalysisPage;