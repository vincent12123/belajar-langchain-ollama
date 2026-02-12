import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import AttendanceTrendsPage from './pages/AttendanceTrendsPage';
import GeolocationAnalysisPage from './pages/GeolocationAnalysisPage';
import ClassComparisonPage from './pages/ClassComparisonPage';

const NAV_ITEMS = [
  { path: '/', label: 'Home', icon: 'home' },
  { path: '/chat', label: 'Chat AI', icon: 'smart_toy' },
  { path: '/trends', label: 'Tren', icon: 'trending_up' },
  { path: '/geolocation', label: 'Lokasi', icon: 'location_on' },
  { path: '/comparison', label: 'Kelas', icon: 'compare_arrows' },
];

function NavBar() {
  const location = useLocation();

  return (
    <nav className="h-16 bg-white border-b border-border flex items-center px-6 sticky top-0 z-50 shadow-sm">
      <Link to="/" className="flex items-center gap-2 mr-8 no-underline">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="material-icons-round text-white text-base">school</span>
        </div>
        <span className="font-bold text-foreground text-lg tracking-tight">
          EduAttend<span className="text-primary">AI</span>
        </span>
      </Link>
      <div className="flex items-center gap-1">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium no-underline transition-colors ${
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              }`}
            >
              <span className="material-icons-round text-base">{item.icon}</span>
              <span className="hidden sm:inline">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <NavBar />
        <Routes>
          <Route path="/" element={
            <div className="max-w-6xl mx-auto p-6">
              <HomePage />
            </div>
          } />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/trends" element={
            <div className="max-w-6xl mx-auto p-6">
              <AttendanceTrendsPage />
            </div>
          } />
          <Route path="/geolocation" element={
            <div className="max-w-6xl mx-auto p-6">
              <GeolocationAnalysisPage />
            </div>
          } />
          <Route path="/comparison" element={
            <div className="max-w-6xl mx-auto p-6">
              <ClassComparisonPage />
            </div>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;