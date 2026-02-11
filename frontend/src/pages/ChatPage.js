import React, { useState, useRef, useEffect } from 'react';
import { chatWithAI } from '../services/api';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Add user message
    const userMessage = { role: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call API
      const response = await chatWithAI(inputMessage);

      // Add assistant message
      const assistantMessage = { role: 'assistant', content: response.response };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = { role: 'assistant', content: `Error: ${error.message}` };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="header">
        <h1>💬 Chat dengan AI Asisten Sekolah</h1>
        <p>Tanyakan apa saja tentang absensi, laporan, atau surat peringatan</p>
      </div>

      <div className="card">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message message-${message.role}`}>
              <strong>{message.role === 'user' ? 'Anda' : 'AI'}:</strong>
              <div>{message.content}</div>
            </div>
          ))}
          {isLoading && (
            <div className="message message-assistant">
              <strong>AI:</strong>
              <div>⏳ Sedang memproses...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Tulis pertanyaan Anda... (contoh: 'Siapa saja yang alfa hari ini?')"
              disabled={isLoading}
            />
          </div>
          <button type="submit" className="btn" disabled={isLoading}>
            {isLoading ? 'Memproses...' : 'Kirim'}
          </button>
        </form>
      </div>

      <div className="card">
        <h3>Contoh Pertanyaan</h3>
        <ul>
          <li>"Siapa saja yang tidak hadir hari ini?"</li>
          <li>"Tampilkan rekap absensi Budi bulan Februari 2026"</li>
          <li>"Berapa persentase kehadiran kelas X RPL 1?"</li>
          <li>"Buatkan surat peringatan untuk Ani yang alfa"</li>
          <li>"Tampilkan absensi siswa ID 10 dari tanggal 2026-02-01 sampai 2026-02-09"</li>
        </ul>
      </div>
    </div>
  );
};

export default ChatPage;