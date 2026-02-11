import React, { useState } from 'react';
import { getAttendanceTrends } from '../services/api';
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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const AttendanceTrendsPage = () => {
  const [formData, setFormData] = useState({
    siswa_id: '',
    nama_siswa: '',
    kelas_id: '',
    nama_kelas: '',
    months: 6
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
      if (formData.siswa_id) params.siswa_id = parseInt(formData.siswa_id);
      if (formData.nama_siswa) params.nama_siswa = formData.nama_siswa;
      if (formData.kelas_id) params.kelas_id = parseInt(formData.kelas_id);
      if (formData.nama_kelas) params.nama_kelas = formData.nama_kelas;
      if (formData.months) params.months = parseInt(formData.months);

      const response = await getAttendanceTrends(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? {
    labels: result.data.map(item => `${item.bulan}/${item.tahun}`),
    datasets: [
      {
        label: 'Persentase Kehadiran (%)',
        data: result.data.map(item => item.persen_hadir),
        backgroundColor: 'rgba(74, 105, 189, 0.6)',
        borderColor: 'rgba(74, 105, 189, 1)',
        borderWidth: 1,
      }
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Tren Kehadiran'
      }
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  return (
    <div>
      <div className="header">
        <h1>📈 Analisis Tren Kehadiran</h1>
        <p>Menganalisis pola kehadiran siswa atau kelas dalam beberapa bulan terakhir</p>
      </div>

      <div className="card">
        <h2>Parameter Pencarian</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="siswa_id">ID Siswa (opsional):</label>
            <input
              type="number"
              id="siswa_id"
              name="siswa_id"
              value={formData.siswa_id}
              onChange={handleChange}
              placeholder="Masukkan ID siswa"
            />
          </div>

          <div className="form-group">
            <label htmlFor="nama_siswa">Nama Siswa (opsional):</label>
            <input
              type="text"
              id="nama_siswa"
              name="nama_siswa"
              value={formData.nama_siswa}
              onChange={handleChange}
              placeholder="Masukkan nama siswa"
            />
          </div>

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
            <label htmlFor="months">Jumlah Bulan:</label>
            <input
              type="number"
              id="months"
              name="months"
              value={formData.months}
              onChange={handleChange}
              min="1"
              max="24"
            />
          </div>

          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Memproses...' : 'Analisis Tren'}
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
          <p><strong>Periode Analisis:</strong> {result.periode_analisis}</p>

          {chartData && (
            <Bar data={chartData} options={chartOptions} />
          )}

          <h3>Data Detail</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Bulan/Tahun</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Hadir</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Total Hari</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>% Kehadiran</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Tren</th>
              </tr>
            </thead>
            <tbody>
              {result.data.map((item, index) => (
                <tr key={index}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{item.bulan}/{item.tahun}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{item.hadir}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{item.total_hari}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{item.persen_hadir}%</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    {item.trend === 'meningkat' ? '↗️ Meningkat' :
                     item.trend === 'menurun' ? '↘️ Menurun' :
                     item.trend === 'stabil' ? '➡️ Stabil' :
                     '🆕 Terbaru'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AttendanceTrendsPage;