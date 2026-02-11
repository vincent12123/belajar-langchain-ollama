import React, { useState } from 'react';
import { compareClassAttendance } from '../services/api';
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

const ClassComparisonPage = () => {
  const [formData, setFormData] = useState({
    tingkat: '',
    jurusan: ''
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
      if (formData.tingkat) params.tingkat = parseInt(formData.tingkat);
      if (formData.jurusan) params.jurusan = formData.jurusan;

      const response = await compareClassAttendance(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? {
    labels: result.perbandingan_kelas.map(item => item.kelas),
    datasets: [
      {
        label: 'Persentase Kehadiran (%)',
        data: result.perbandingan_kelas.map(item => item.persen_hadir),
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
        text: 'Perbandingan Kehadiran Antar Kelas'
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
        <h1>📊 Perbandingan Kehadiran Kelas</h1>
        <p>Membandingkan tingkat kehadiran antar kelas untuk evaluasi performa</p>
      </div>

      <div className="card">
        <h2>Parameter Pencarian</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="tingkat">Tingkat (opsional):</label>
            <select
              id="tingkat"
              name="tingkat"
              value={formData.tingkat}
              onChange={handleChange}
            >
              <option value="">Semua Tingkat</option>
              <option value="10">Kelas 10</option>
              <option value="11">Kelas 11</option>
              <option value="12">Kelas 12</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="jurusan">Jurusan (opsional):</label>
            <select
              id="jurusan"
              name="jurusan"
              value={formData.jurusan}
              onChange={handleChange}
            >
              <option value="">Semua Jurusan</option>
              <option value="RPL">RPL (Rekayasa Perangkat Lunak)</option>
              <option value="TKJ">TKJ (Teknik Komputer dan Jaringan)</option>
              <option value="MM">MM (Multimedia)</option>
              <option value="OTKP">OTKP (Otomatisasi dan Tata Kelola Perkantoran)</option>
              <option value="BDP">BDP (Bisnis Daring dan Pemasaran)</option>
              <option value="AKL">AKL (Akuntansi dan Keuangan Lembaga)</option>
            </select>
          </div>

          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Memproses...' : 'Bandingkan Kelas'}
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
          <h2>Hasil Perbandingan</h2>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', marginBottom: '20px' }}>
            <div className="card" style={{ flex: 1, minWidth: '200px' }}>
              <h3>Total Kelas</h3>
              <p style={{ fontSize: '2em', textAlign: 'center', color: '#4a69bd' }}>
                {result.total_kelas}
              </p>
            </div>

            <div className="card" style={{ flex: 1, minWidth: '200px' }}>
              <h3>Rata-rata Kehadiran</h3>
              <p style={{ fontSize: '2em', textAlign: 'center', color: '#28a745' }}>
                {result.rata_rata_kehadiran}%
              </p>
            </div>

            {result.kelas_terbaik && (
              <div className="card" style={{ flex: 1, minWidth: '200px' }}>
                <h3>Kelas Terbaik</h3>
                <p style={{ fontSize: '1.2em', textAlign: 'center', color: '#28a745' }}>
                  {result.kelas_terbaik.kelas}
                </p>
                <p style={{ textAlign: 'center' }}>
                  {result.kelas_terbaik.persen_hadir}% kehadiran
                </p>
              </div>
            )}

            {result.kelas_terendah && (
              <div className="card" style={{ flex: 1, minWidth: '200px' }}>
                <h3>Kelas Terendah</h3>
                <p style={{ fontSize: '1.2em', textAlign: 'center', color: '#dc3545' }}>
                  {result.kelas_terendah.kelas}
                </p>
                <p style={{ textAlign: 'center' }}>
                  {result.kelas_terendah.persen_hadir}% kehadiran
                </p>
              </div>
            )}
          </div>

          {chartData && (
            <Bar data={chartData} options={chartOptions} />
          )}

          <h3>Data Detail Per Kelas</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Kelas</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Hadir</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Total Hari</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>% Kehadiran</th>
              </tr>
            </thead>
            <tbody>
              {result.perbandingan_kelas.map((kelas, index) => (
                <tr key={index}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{kelas.kelas}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{kelas.hadir}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{kelas.total_hari}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <span style={{
                      fontWeight: 'bold',
                      color: kelas.persen_hadir >= 90 ? '#28a745' :
                             kelas.persen_hadir >= 75 ? '#ffc107' : '#dc3545'
                    }}>
                      {kelas.persen_hadir}%
                    </span>
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

export default ClassComparisonPage;