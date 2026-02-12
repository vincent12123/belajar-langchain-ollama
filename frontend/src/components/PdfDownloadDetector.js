import React, { useMemo } from 'react';
import { downloadFile } from '../services/api';

/**
 * Scans chat messages for PDF file paths and renders download buttons.
 * Detects patterns like: output/xxx.pdf, surat_peringatan_xxx.pdf, etc.
 */
const PdfDownloadDetector = ({ messages }) => {
  const pdfFiles = useMemo(() => {
    const files = new Set();
    const pdfPattern = /([\w/\\:.-]+\.pdf)/gi;

    for (const msg of messages) {
      if (msg.role !== 'assistant') continue;

      // Extract text content from message
      let text = '';
      if (typeof msg.content === 'string') {
        text = msg.content;
      } else if (msg.parts) {
        text = msg.parts
          .filter(p => p.type === 'text')
          .map(p => p.text)
          .join(' ');
      }

      if (!text) continue;

      const matches = text.matchAll(pdfPattern);
      for (const match of matches) {
        const raw = match[1];
        // Extract just the filename from path
        const parts = raw.replace(/\\/g, '/').split('/');
        const filename = parts[parts.length - 1];
        if (filename && filename.endsWith('.pdf')) {
          files.add(filename);
        }
      }
    }

    return Array.from(files);
  }, [messages]);

  if (pdfFiles.length === 0) return null;

  const handleDownload = async (filename) => {
    try {
      await downloadFile(filename);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  return (
    <div className="px-4 pb-3">
      <div className="max-w-3xl mx-auto space-y-2">
        {pdfFiles.map((filename, idx) => (
          <button
            key={`${filename}-${idx}`}
            onClick={() => handleDownload(filename)}
            className="flex items-center gap-3 w-full px-4 py-3 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg transition-colors group text-left"
          >
            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
              <span className="material-icons-round text-green-600 text-xl">picture_as_pdf</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-green-800 truncate">{filename}</p>
              <p className="text-xs text-green-600">Klik untuk download</p>
            </div>
            <span className="material-icons-round text-green-500 group-hover:text-green-700 transition-colors">download</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default PdfDownloadDetector;
