import React, { useMemo, useState, useCallback } from 'react';

/**
 * Keywords (Indonesian) that indicate the conversation involves dates.
 * Matches the last assistant message to decide whether to show date suggestions.
 */
const DATE_KEYWORDS = [
  'tanggal', 'bulan', 'hari', 'kapan', 'periode',
  'dari tanggal', 'sampai tanggal', 'mulai', 'hingga',
  'rentang waktu', 'minggu', 'semester', 'tahun',
  'antara tanggal', 'sejak', 'berapa lama',
  'rekap', 'laporan', 'absensi', 'kehadiran',
  'start_date', 'end_date', 'date',
];

/** Check if text suggests a date-range context (two dates needed) */
const RANGE_KEYWORDS = [
  'dari tanggal', 'sampai tanggal', 'rentang', 'periode',
  'mulai.*hingga', 'antara tanggal', 'start.*end',
  'dari.*sampai', 'range',
];

const fmt = (d) => {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
};

const fmtReadable = (d) =>
  d.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' });

const getQuickDates = () => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - today.getDay() + 1); // Monday

  const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);

  const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);

  return {
    today,
    yesterday,
    weekStart,
    monthStart,
    lastMonthStart,
    lastMonthEnd,
  };
};

const DateSuggestion = ({ messages, onSelectDate }) => {
  const [showCustom, setShowCustom] = useState(false);
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');

  /** Determine if last assistant message is date-related, and if it's a range context */
  const { shouldShow, isRange } = useMemo(() => {
    if (!messages || messages.length === 0) return { shouldShow: false, isRange: false };

    // Find the last assistant message
    let lastAssistant = null;
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'assistant') {
        lastAssistant = messages[i];
        break;
      }
    }
    if (!lastAssistant) return { shouldShow: false, isRange: false };

    let text = '';
    if (typeof lastAssistant.content === 'string') {
      text = lastAssistant.content;
    } else if (lastAssistant.parts) {
      text = lastAssistant.parts
        .filter((p) => p.type === 'text')
        .map((p) => p.text)
        .join(' ');
    }
    if (!text) return { shouldShow: false, isRange: false };

    const lower = text.toLowerCase();

    const hasDate = DATE_KEYWORDS.some((kw) => lower.includes(kw));
    if (!hasDate) return { shouldShow: false, isRange: false };

    const hasRange = RANGE_KEYWORDS.some((kw) => {
      try {
        return new RegExp(kw, 'i').test(lower);
      } catch {
        return lower.includes(kw);
      }
    });

    return { shouldShow: true, isRange: hasRange };
  }, [messages]);

  /** Extract the last user question to build contextual follow-up.
   *  Strip any previously appended date suffixes to prevent stacking. */
  const lastUserQuestion = useMemo(() => {
    if (!messages || messages.length === 0) return '';
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role !== 'user') continue;
      let text = '';
      if (typeof messages[i].content === 'string') {
        text = messages[i].content;
      } else if (messages[i].parts) {
        text = messages[i].parts
          .filter((p) => p.type === 'text')
          .map((p) => p.text)
          .join(' ');
      }
      if (text) {
        // Remove previously appended date strings to avoid stacking
        // Matches: " pada tanggal ...", " dari tanggal ... sampai ..."
        text = text.replace(/\s+(pada tanggal|dari tanggal)\s+\d{4}-\d{2}-\d{2}(\s+sampai\s+\d{4}-\d{2}-\d{2})?/g, '');
        return text.trim();
      }
    }
    return '';
  }, [messages]);

  /**
   * Build a contextual message that references the previous conversation.
   * If we know what the user asked before, repeat it with the date.
   * Otherwise, send a generic but neutral date reference.
   */
  const buildContextMessage = useCallback((dateStr) => {
    if (lastUserQuestion) {
      return `${lastUserQuestion} pada tanggal ${dateStr}`;
    }
    return `Tampilkan data absensi pada tanggal ${dateStr}`;
  }, [lastUserQuestion]);

  const buildContextRangeMessage = useCallback((startStr, endStr) => {
    if (lastUserQuestion) {
      return `${lastUserQuestion} dari tanggal ${startStr} sampai ${endStr}`;
    }
    return `Tampilkan data absensi dari tanggal ${startStr} sampai ${endStr}`;
  }, [lastUserQuestion]);

  const handleQuickDate = useCallback(
    (label, dateStr) => {
      onSelectDate(label, buildContextMessage(dateStr));
    },
    [onSelectDate, buildContextMessage]
  );

  const handleQuickRange = useCallback(
    (label, startStr, endStr) => {
      onSelectDate(label, buildContextRangeMessage(startStr, endStr));
    },
    [onSelectDate, buildContextRangeMessage]
  );

  const handleCustomSubmit = useCallback(() => {
    if (!customStart) return;
    if (isRange && customEnd) {
      const s = new Date(customStart);
      const e = new Date(customEnd);
      onSelectDate(
        `${fmtReadable(s)} - ${fmtReadable(e)}`,
        buildContextRangeMessage(customStart, customEnd)
      );
    } else {
      const d = new Date(customStart);
      onSelectDate(fmtReadable(d), buildContextMessage(customStart));
    }
    setShowCustom(false);
    setCustomStart('');
    setCustomEnd('');
  }, [customStart, customEnd, isRange, onSelectDate, buildContextMessage, buildContextRangeMessage]);

  if (!shouldShow) return null;

  const q = getQuickDates();

  return (
    <div className="px-4 pb-2">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <span className="material-icons-round text-primary text-base">event</span>
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            Pilih Tanggal
          </span>
        </div>

        {/* Quick date chips */}
        <div className="flex flex-wrap gap-2 mb-2">
          {!isRange ? (
            <>
              <QuickChip
                icon="today"
                label="Hari Ini"
                sub={fmtReadable(q.today)}
                onClick={() => handleQuickDate('Hari ini', fmt(q.today))}
              />
              <QuickChip
                icon="event"
                label="Kemarin"
                sub={fmtReadable(q.yesterday)}
                onClick={() => handleQuickDate('Kemarin', fmt(q.yesterday))}
              />
              <QuickChip
                icon="date_range"
                label="Awal Bulan"
                sub={fmtReadable(q.monthStart)}
                onClick={() => handleQuickDate(`Awal bulan (${fmtReadable(q.monthStart)})`, fmt(q.monthStart))}
              />
            </>
          ) : (
            <>
              <QuickChip
                icon="date_range"
                label="Minggu Ini"
                sub={`${fmtReadable(q.weekStart)} – ${fmtReadable(q.today)}`}
                onClick={() =>
                  handleQuickRange('Minggu ini', fmt(q.weekStart), fmt(q.today))
                }
              />
              <QuickChip
                icon="calendar_month"
                label="Bulan Ini"
                sub={`${fmtReadable(q.monthStart)} – ${fmtReadable(q.today)}`}
                onClick={() =>
                  handleQuickRange('Bulan ini', fmt(q.monthStart), fmt(q.today))
                }
              />
              <QuickChip
                icon="history"
                label="Bulan Lalu"
                sub={`${fmtReadable(q.lastMonthStart)} – ${fmtReadable(q.lastMonthEnd)}`}
                onClick={() =>
                  handleQuickRange(
                    'Bulan lalu',
                    fmt(q.lastMonthStart),
                    fmt(q.lastMonthEnd)
                  )
                }
              />
            </>
          )}

          {/* Custom date toggle */}
          <button
            onClick={() => setShowCustom((v) => !v)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-medium border transition-colors ${
              showCustom
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-white text-muted-foreground border-border hover:border-primary hover:text-primary'
            }`}
          >
            <span className="material-icons-round text-sm">edit_calendar</span>
            Pilih Tanggal
          </button>
        </div>

        {/* Custom date picker */}
        {showCustom && (
          <div className="flex items-end gap-2 p-3 bg-accent/50 rounded-lg border border-border animate-in slide-in-from-top-1">
            <div className="flex-1 min-w-0">
              <label className="block text-xs font-medium text-muted-foreground mb-1">
                {isRange ? 'Dari Tanggal' : 'Tanggal'}
              </label>
              <input
                type="date"
                value={customStart}
                onChange={(e) => setCustomStart(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
            </div>
            {isRange && (
              <div className="flex-1 min-w-0">
                <label className="block text-xs font-medium text-muted-foreground mb-1">
                  Sampai Tanggal
                </label>
                <input
                  type="date"
                  value={customEnd}
                  onChange={(e) => setCustomEnd(e.target.value)}
                  min={customStart}
                  className="w-full px-3 py-2 text-sm border border-border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                />
              </div>
            )}
            <button
              onClick={handleCustomSubmit}
              disabled={!customStart || (isRange && !customEnd)}
              className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg hover:opacity-90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 whitespace-nowrap"
            >
              <span className="material-icons-round text-sm">send</span>
              Kirim
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

/** Reusable quick-date chip button */
const QuickChip = ({ icon, label, sub, onClick }) => (
  <button
    onClick={onClick}
    className="flex items-center gap-2 px-3 py-2 bg-white border border-border rounded-full hover:border-primary hover:bg-primary/5 transition-colors group text-left"
  >
    <span className="material-icons-round text-sm text-muted-foreground group-hover:text-primary transition-colors">
      {icon}
    </span>
    <div className="flex flex-col leading-tight">
      <span className="text-xs font-medium text-foreground">{label}</span>
      {sub && <span className="text-[10px] text-muted-foreground">{sub}</span>}
    </div>
  </button>
);

export default DateSuggestion;
