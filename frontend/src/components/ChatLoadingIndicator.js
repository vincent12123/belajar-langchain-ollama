import React, { useState, useEffect } from 'react';

const LOADING_TEXTS = [
  'Menganalisis pertanyaan...',
  'Mencari data di database...',
  'Memproses hasil query...',
  'Menyusun jawaban...',
];

function ChatLoadingIndicator({ isLoading }) {
  const [textIndex, setTextIndex] = useState(0);
  const [dots, setDots] = useState('');

  // Cycle through loading texts
  useEffect(() => {
    if (!isLoading) {
      setTextIndex(0);
      setDots('');
      return;
    }

    const textTimer = setInterval(() => {
      setTextIndex((prev) => (prev + 1) % LOADING_TEXTS.length);
    }, 3000);

    return () => clearInterval(textTimer);
  }, [isLoading]);

  // Animate dots
  useEffect(() => {
    if (!isLoading) return;

    const dotTimer = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);

    return () => clearInterval(dotTimer);
  }, [isLoading]);

  if (!isLoading) return null;

  return (
    <div className="flex items-start gap-3 px-4 py-3 max-w-4xl mx-auto animate-fadeIn">
      {/* AI Avatar */}
      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
        <span className="material-icons-round text-primary text-base">smart_toy</span>
      </div>

      {/* Loading Bubble */}
      <div className="bg-white border border-border rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm max-w-xs">
        {/* Bouncing dots */}
        <div className="flex items-center gap-1.5 mb-1.5">
          <span className="typing-dot w-2 h-2 rounded-full bg-primary/60" style={{ animationDelay: '0ms' }} />
          <span className="typing-dot w-2 h-2 rounded-full bg-primary/60" style={{ animationDelay: '150ms' }} />
          <span className="typing-dot w-2 h-2 rounded-full bg-primary/60" style={{ animationDelay: '300ms' }} />
        </div>

        {/* Status text */}
        <p className="text-xs text-muted-foreground transition-all duration-300">
          {LOADING_TEXTS[textIndex]}{dots}
        </p>
      </div>
    </div>
  );
}

export default ChatLoadingIndicator;
