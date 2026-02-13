import React, { useState, useEffect, useCallback } from 'react';
import { checkApiHealth } from '../services/api';

const STATUS = {
  CHECKING: 'checking',
  ONLINE: 'online',
  OFFLINE: 'offline',
};

const STATUS_CONFIG = {
  [STATUS.CHECKING]: {
    color: 'bg-yellow-400',
    ring: 'ring-yellow-400/30',
    text: 'text-yellow-600',
    bgHover: 'hover:bg-yellow-50',
    label: 'Memeriksa...',
    icon: 'sync',
    iconClass: 'animate-spin',
  },
  [STATUS.ONLINE]: {
    color: 'bg-emerald-500',
    ring: 'ring-emerald-500/30',
    text: 'text-emerald-600',
    bgHover: 'hover:bg-emerald-50',
    label: 'Terhubung',
    icon: 'cloud_done',
    iconClass: '',
  },
  [STATUS.OFFLINE]: {
    color: 'bg-red-500',
    ring: 'ring-red-500/30',
    text: 'text-red-600',
    bgHover: 'hover:bg-red-50',
    label: 'Offline',
    icon: 'cloud_off',
    iconClass: '',
  },
};

const POLL_INTERVAL = 30000; // 30 detik
const RETRY_INTERVAL = 10000; // 10 detik saat offline

function ConnectionStatus() {
  const [status, setStatus] = useState(STATUS.CHECKING);
  const [lastChecked, setLastChecked] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const checkConnection = useCallback(async () => {
    try {
      const result = await checkApiHealth();
      setStatus(result.online ? STATUS.ONLINE : STATUS.OFFLINE);
      setLastChecked(new Date());
    } catch {
      setStatus(STATUS.OFFLINE);
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    checkConnection();

    const interval = setInterval(() => {
      checkConnection();
    }, status === STATUS.OFFLINE ? RETRY_INTERVAL : POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [checkConnection, status]);

  const config = STATUS_CONFIG[status];

  const formatTime = (date) => {
    if (!date) return '-';
    return date.toLocaleTimeString('id-ID', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="relative">
      <button
        onClick={checkConnection}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 border-0 cursor-pointer ${config.text} ${config.bgHover} bg-transparent`}
        title="Klik untuk cek ulang koneksi"
      >
        <span className="relative flex h-2.5 w-2.5">
          {status === STATUS.ONLINE && (
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.color} opacity-40`}></span>
          )}
          <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${config.color} ring-2 ${config.ring}`}></span>
        </span>
        <span className={`material-icons-round text-sm ${config.iconClass}`} style={{ fontSize: '14px' }}>
          {config.icon}
        </span>
        <span className="hidden md:inline">{config.label}</span>
      </button>

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 p-3 z-50 text-left">
          <div className="flex items-center gap-2 mb-2">
            <span className={`inline-flex rounded-full h-3 w-3 ${config.color}`}></span>
            <span className={`font-semibold text-sm ${config.text}`}>{config.label}</span>
          </div>
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex justify-between">
              <span>Server:</span>
              <span className="font-mono text-gray-700">localhost:8000</span>
            </div>
            <div className="flex justify-between">
              <span>Terakhir cek:</span>
              <span className="font-mono text-gray-700">{formatTime(lastChecked)}</span>
            </div>
            <div className="flex justify-between">
              <span>Interval:</span>
              <span className="font-mono text-gray-700">
                {status === STATUS.OFFLINE ? '10 detik' : '30 detik'}
              </span>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-gray-100 text-xs text-gray-400 text-center">
            Klik indikator untuk cek ulang
          </div>
        </div>
      )}
    </div>
  );
}

export default ConnectionStatus;
