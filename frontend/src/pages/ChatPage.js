import React, { useState } from 'react';
import { useChat } from '@ai-sdk/react';
import { TextStreamChatTransport } from 'ai';
import {
  ChatSection,
  ChatMessages,
  ChatInput,
} from '@llamaindex/chat-ui';
import '@llamaindex/chat-ui/styles/markdown.css';
import '../custom-styles.css';
import PdfDownloadDetector from '../components/PdfDownloadDetector';
import DateSuggestion from '../components/DateSuggestion';

const SUGGESTED_QUESTIONS = [
  { label: "Absen Hari Ini", text: "Siapa saja yang tidak hadir hari ini?" },
  { label: "Rekap Kelas", text: "Tampilkan rekap absensi kelas X RPL 1 bulan ini" },
  { label: "Siswa Alfa", text: "Siapa saja yang alfa hari ini?" },
  { label: "Persentase Kehadiran", text: "Berapa persentase kehadiran bulan ini?" },
  { label: "Top Siswa Bolos", text: "Siapa 5 siswa paling sering alfa?" },
  { label: "Analisis Anomali", text: "Cek anomali absensi hari ini" },
];

const ChatPage = () => {
  const [chatKey, setChatKey] = useState(0);

  const handler = useChat({
    chatId: `chat-${chatKey}`,
    transport: new TextStreamChatTransport({
      api: 'http://localhost:8000/api/chat',
    }),
  });

  const handleNewChat = () => {
    setChatKey(prev => prev + 1);
  };

  const handleSuggestionClick = (text) => {
    handler.sendMessage({ text });
  };

  const handleDateSelect = (_label, dateText) => {
    handler.sendMessage({ text: dateText });
  };

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 bg-white border-r border-border flex-col h-full hidden md:flex">
        {/* Logo & New Chat */}
        <div className="p-5 border-b border-border">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center text-primary-foreground shadow-lg">
              <span className="material-icons-round text-xl">school</span>
            </div>
            <h1 className="font-bold text-lg tracking-tight text-foreground">
              EduAttend<span className="text-primary">AI</span>
            </h1>
          </div>
          <button
            onClick={handleNewChat}
            className="w-full bg-primary hover:opacity-90 text-primary-foreground font-medium py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-md"
          >
            <span className="material-icons-round text-lg">add</span>
            Sesi Baru
          </button>
        </div>

        {/* Quick Actions */}
        <div className="flex-1 overflow-y-auto p-4 space-y-1">
          <h3 className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Pertanyaan Cepat
          </h3>
          {SUGGESTED_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSuggestionClick(q.text)}
              className="w-full text-left flex items-center gap-2 px-3 py-2.5 text-sm text-foreground hover:bg-accent rounded-lg transition-colors"
            >
              <span className="material-icons-round text-base text-muted-foreground">chat_bubble_outline</span>
              <span className="truncate">{q.label}</span>
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3 p-2 rounded-lg">
            <div className="w-9 h-9 rounded-full bg-muted flex items-center justify-center">
              <span className="material-icons-round text-muted-foreground text-lg">person</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-foreground truncate">Administrator</p>
              <p className="text-xs text-muted-foreground">School Admin</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full bg-background relative">
        {/* Header */}
        <header className="h-14 bg-white/80 backdrop-blur-md border-b border-border flex items-center justify-between px-6 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground text-sm">Sesi Analisis /</span>
            <span className="font-semibold text-sm text-foreground">Sesi Aktif</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleNewChat}
              className="p-2 text-muted-foreground hover:text-primary hover:bg-accent rounded-full transition-colors md:hidden"
              title="New Chat"
            >
              <span className="material-icons-round text-xl">add</span>
            </button>
          </div>
        </header>

        {/* Chat Content - LlamaIndex Chat UI */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <ChatSection handler={handler} className="h-full flex flex-col flex-1">
            <div className="flex-1 overflow-y-auto">
              {handler.messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-4 py-12">
                  <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
                    <span className="material-icons-round text-3xl text-primary">school</span>
                  </div>
                  <h2 className="text-xl font-bold text-foreground mb-2">
                    Selamat Datang di EduAttend AI
                  </h2>
                  <p className="text-muted-foreground mb-6 max-w-md">
                    Asisten AI untuk mengelola dan menganalisis data absensi siswa.
                    Tanyakan apa saja tentang kehadiran, rekap, atau analisis.
                  </p>
                  <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                    {SUGGESTED_QUESTIONS.slice(0, 4).map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(q.text)}
                        className="text-xs bg-primary/10 text-primary hover:bg-primary/20 px-3 py-2 rounded-full transition-colors font-medium border border-primary/20"
                      >
                        {q.label}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <ChatMessages />
              )}
            </div>
            <PdfDownloadDetector messages={handler.messages} />
            <DateSuggestion messages={handler.messages} onSelectDate={handleDateSelect} />
            <div className="border-t border-border bg-white p-4">
              <div className="max-w-4xl mx-auto">
                <ChatInput>
                  <ChatInput.Form>
                    <ChatInput.Field type="textarea" />
                    <ChatInput.Submit />
                  </ChatInput.Form>
                </ChatInput>
                <p className="text-center text-xs text-muted-foreground mt-2">
                  AI dapat melakukan kesalahan. Mohon verifikasi data absensi yang penting.
                </p>
              </div>
            </div>
          </ChatSection>
        </div>
      </main>
    </div>
  );
};

export default ChatPage;
