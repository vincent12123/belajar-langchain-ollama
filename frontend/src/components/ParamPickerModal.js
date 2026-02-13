import React, { useState, useEffect, useCallback } from 'react';
import { getKelasList } from '../services/api';

/**
 * Modal untuk memilih parameter (kelas, tanggal, dll) sebelum mengirim suggested question.
 * Props:
 *   - open: boolean
 *   - config: { title, fields: [{ key, label, type, required }] }
 *   - onSubmit: (values) => void
 *   - onClose: () => void
 */
const ParamPickerModal = ({ open, config, onSubmit, onClose }) => {
  const [kelasList, setKelasList] = useState([]);
  const [loadingKelas, setLoadingKelas] = useState(false);
  const [values, setValues] = useState({});

  // Fetch kelas list when modal opens and has a kelas field
  useEffect(() => {
    if (!open || !config) return;

    const hasKelasField = config.fields?.some(f => f.type === 'kelas');
    if (hasKelasField && kelasList.length === 0) {
      setLoadingKelas(true);
      getKelasList()
        .then(data => setKelasList(data))
        .catch(err => console.error('Failed to load kelas:', err))
        .finally(() => setLoadingKelas(false));
    }

    // Initialize default values
    const defaults = {};
    config.fields?.forEach(f => {
      if (f.type === 'date' && f.defaultToday) {
        defaults[f.key] = new Date().toISOString().split('T')[0];
      } else if (f.type === 'date_range') {
        // Default: current month
        const now = new Date();
        const y = now.getFullYear();
        const m = String(now.getMonth() + 1).padStart(2, '0');
        defaults[f.key + '_mulai'] = `${y}-${m}-01`;
        defaults[f.key + '_akhir'] = now.toISOString().split('T')[0];
      } else {
        defaults[f.key] = f.default || '';
      }
    });
    setValues(defaults);
  }, [open, config]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleChange = useCallback((key, val) => {
    setValues(prev => ({ ...prev, [key]: val }));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(values);
  };

  if (!open || !config) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-primary/5">
          <div className="flex items-center gap-2">
            <span className="material-icons-round text-primary text-xl">tune</span>
            <h3 className="font-semibold text-foreground text-base">{config.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-muted-foreground hover:text-foreground rounded-full hover:bg-accent transition-colors"
          >
            <span className="material-icons-round text-xl">close</span>
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {config.fields?.map((field) => (
            <div key={field.key}>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>

              {field.type === 'kelas' && (
                loadingKelas ? (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground py-2">
                    <span className="material-icons-round text-base animate-spin">sync</span>
                    Memuat daftar kelas...
                  </div>
                ) : (
                  <select
                    value={values[field.key] || ''}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    required={field.required}
                    className="w-full border border-border rounded-lg px-3 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
                  >
                    <option value="">-- Pilih Kelas --</option>
                    {kelasList.map(k => (
                      <option key={k.id} value={k.nama}>
                        {k.nama} ({k.jurusan} - Tingkat {k.tingkat})
                      </option>
                    ))}
                  </select>
                )
              )}

              {field.type === 'date' && (
                <input
                  type="date"
                  value={values[field.key] || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  required={field.required}
                  className="w-full border border-border rounded-lg px-3 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
                />
              )}

              {field.type === 'date_range' && (
                <div className="flex gap-2">
                  <div className="flex-1">
                    <span className="text-xs text-muted-foreground">Dari</span>
                    <input
                      type="date"
                      value={values[field.key + '_mulai'] || ''}
                      onChange={(e) => handleChange(field.key + '_mulai', e.target.value)}
                      required={field.required}
                      className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
                    />
                  </div>
                  <div className="flex-1">
                    <span className="text-xs text-muted-foreground">Sampai</span>
                    <input
                      type="date"
                      value={values[field.key + '_akhir'] || ''}
                      onChange={(e) => handleChange(field.key + '_akhir', e.target.value)}
                      required={field.required}
                      className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
                    />
                  </div>
                </div>
              )}

              {field.type === 'text' && (
                <input
                  type="text"
                  value={values[field.key] || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  placeholder={field.placeholder || ''}
                  required={field.required}
                  className="w-full border border-border rounded-lg px-3 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
                />
              )}

              {field.type === 'select' && (
                <select
                  value={values[field.key] || field.default || ''}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  required={field.required}
                  className="w-full border border-border rounded-lg px-3 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
                >
                  {field.options?.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              )}
            </div>
          ))}

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-border text-sm font-medium text-muted-foreground rounded-lg hover:bg-accent transition-colors"
            >
              Batal
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:opacity-90 transition-colors shadow-md"
            >
              <span className="flex items-center justify-center gap-1.5">
                <span className="material-icons-round text-base">send</span>
                Kirim
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ParamPickerModal;
