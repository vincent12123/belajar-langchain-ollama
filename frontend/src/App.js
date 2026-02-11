import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import AttendanceTrendsPage from './pages/AttendanceTrendsPage';
import GeolocationAnalysisPage from './pages/GeolocationAnalysisPage';
import ClassComparisonPage from './pages/ClassComparisonPage';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              🏫 Sistem Absensi Sekolah
            </Link>
            <ul className="nav-menu">
              <li className="nav-item">
                <Link to="/" className="nav-link">Home</Link>
              </li>
              <li className="nav-item">
                <Link to="/chat" className="nav-link">Chat AI</Link>
              </li>
              <li className="nav-item">
                <Link to="/trends" className="nav-link">Tren Kehadiran</Link>
              </li>
              <li className="nav-item">
                <Link to="/geolocation" className="nav-link">Analisis Lokasi</Link>
              </li>
              <li className="nav-item">
                <Link to="/comparison" className="nav-link">Perbandingan Kelas</Link>
              </li>
            </ul>
          </div>
        </nav>

        <div className="container">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/trends" element={<AttendanceTrendsPage />} />
            <Route path="/geolocation" element={<GeolocationAnalysisPage />} />
            <Route path="/comparison" element={<ClassComparisonPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;