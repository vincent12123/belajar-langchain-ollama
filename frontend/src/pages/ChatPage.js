import React, { useState, useRef, useEffect } from 'react';
import { chatWithAI } from '../services/api';
import '../custom-styles.css';

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
    if (e) e.preventDefault();
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
      const assistantMessage = { role: 'assistant', content: response.answer };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = { role: 'assistant', content: `Error: ${error.message}` };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-800 dark:text-slate-100 font-display flex overflow-hidden" style={{ height: 'calc(100vh - 80px)' }}> 
      {/* Sidebar - Integrated as part of ChatPage layout, but adjusted to fit in existing App container */}
      <aside className="w-80 flex-shrink-0 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full z-20 shadow-sm relative hidden md:flex">
        {/* Logo & New Chat Header */}
        <div className="p-5 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/30">
              <span className="material-icons-round">school</span>
            </div>
            <h1 className="font-bold text-xl tracking-tight text-slate-900 dark:text-white">EduAttend<span className="text-primary">AI</span></h1>
          </div>
          <button 
            onClick={() => setMessages([])}
            className="w-full bg-primary hover:bg-primary-600 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-md shadow-primary/20 group">
            <span className="material-icons-round text-xl group-hover:rotate-90 transition-transform">add</span>
            New Analysis Session
          </button>
        </div>
        
        {/* History List - Static for demo */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
          <div>
            <h3 className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Today</h3>
            <ul className="space-y-1">
              <li>
                <a className="flex items-center gap-3 px-3 py-3 bg-primary/10 text-primary rounded-lg border border-primary/10" href="#">
                  <span className="material-icons-round text-lg">chat_bubble_outline</span>
                  <span className="text-sm font-medium truncate">Grade 10 Attendance</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* User Profile Footer */}
        <div className="p-4 border-t border-slate-100 dark:border-slate-800 mt-auto">
          <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors">
            <div className="w-10 h-10 rounded-full bg-slate-300 flex items-center justify-center overflow-hidden border-2 border-white dark:border-slate-700 shadow-sm">
                 <span className="material-icons-round text-slate-500">person</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">Administrator</p>
              <p className="text-xs text-slate-500 truncate">School Admin</p>
            </div>
            <span className="material-icons-round text-slate-400">more_vert</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full bg-background-light dark:bg-background-dark relative">
        {/* Top Bar inside Chat */}
        <header className="h-16 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 dark:text-slate-500">Analysis Session /</span>
            <span className="font-semibold text-slate-800 dark:text-white">Active Session</span>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-500 hover:text-primary hover:bg-primary/5 rounded-full transition-colors" title="Download Report">
              <span className="material-icons-round">download</span>
            </button>
            <button className="p-2 text-slate-500 hover:text-primary hover:bg-primary/5 rounded-full transition-colors" title="Settings">
              <span className="material-icons-round">settings</span>
            </button>
          </div>
        </header>

        {/* Chat Container */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-8" id="chat-container">
          {/* Welcome Message if empty */}
          {messages.length === 0 && (
             <div className="flex gap-4 max-w-3xl">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-blue-400 flex-shrink-0 flex items-center justify-center text-white shadow-md">
                <span className="material-icons-round text-xl">smart_toy</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-xs text-slate-500 font-medium ml-1">Assistant</span>
                <div className="bg-white dark:bg-slate-800 p-4 rounded-xl bubble-ai shadow-sm border border-slate-100 dark:border-slate-700 text-slate-800 dark:text-slate-200 leading-relaxed">
                  <p>Good morning. I'm ready to assist you with attendance records. How can I help?</p>
                  <div className="mt-4 flex gap-2 flex-wrap">
                    <button onClick={() => setInputMessage("Siapa saja yang tidak hadir hari ini?")} className="text-xs bg-primary/10 text-primary hover:bg-primary/20 px-3 py-1.5 rounded-full transition-colors font-medium border border-primary/10">Absen Hari Ini</button>
                    <button onClick={() => setInputMessage("Tampilkan rekap absensi kelas X Bulan Ini")} className="text-xs bg-primary/10 text-primary hover:bg-primary/20 px-3 py-1.5 rounded-full transition-colors font-medium border border-primary/10">Rekap Kelas</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Messages Map */}
          {messages.map((message, index) => (
            <div key={index} className={`flex gap-4 max-w-3xl ${message.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
              
              {/* Avatar based on role */}
              {message.role === 'assistant' ? (
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-blue-400 flex-shrink-0 flex items-center justify-center text-white shadow-md">
                   <span className="material-icons-round text-xl">smart_toy</span>
                </div>
              ) : (
                <div className="w-10 h-10 rounded-full flex-shrink-0 border-2 border-white shadow-sm overflow-hidden bg-slate-200 flex items-center justify-center">
                    <span className="material-icons-round text-slate-500">person</span>
                </div>
              )}

              <div className={`flex flex-col gap-1 ${message.role === 'user' ? 'items-end' : 'w-full'}`}>
                <span className="text-xs text-slate-500 font-medium mx-1">{message.role === 'user' ? 'You' : 'Assistant'}</span>
                
                <div className={`
                    p-4 rounded-xl shadow-sm leading-relaxed
                    ${message.role === 'user' 
                      ? 'bg-primary text-white bubble-user shadow-primary/20' 
                      : 'bg-white dark:bg-slate-800 bubble-ai border border-slate-100 dark:border-slate-700 text-slate-800 dark:text-slate-200 w-full'}
                  `}>
                  {/* Allow simple text formatting via whitespace */}
                  <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex gap-4 max-w-3xl">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-blue-400 flex-shrink-0 flex items-center justify-center text-white shadow-md">
                <span className="material-icons-round text-xl">smart_toy</span>
              </div>
              <div className="flex flex-col gap-1">
                 <span className="text-xs text-slate-500 font-medium ml-1">Assistant</span>
                 <div className="bg-white dark:bg-slate-800 p-4 rounded-xl bubble-ai shadow-sm border border-slate-100 dark:border-slate-700 text-slate-800 dark:text-slate-200">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                    </div>
                 </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
          <div className="h-4"></div>
        </div>

        {/* Input Area */}
        <div className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 p-6 z-20">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={handleSubmit}>
              {/* Attachment Button (Visual Only for now) */}
              {/* <button type="button" className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-primary p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors z-10" title="Upload roster or document">
                <span className="material-icons-round">attach_file</span>
              </button> */}
              
              <input 
                className="w-full pl-6 pr-32 py-4 bg-background-light dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent text-slate-800 dark:text-slate-100 placeholder-slate-400 shadow-sm transition-all text-base" 
                placeholder="Ask about attendance trends, specific students, or classes..." 
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                disabled={isLoading}
              />
              
              {/* Action Buttons */}
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                <button 
                  type="submit" 
                  disabled={isLoading}
                  className="bg-primary hover:bg-primary-600 text-white p-2 rounded-lg shadow-md shadow-primary/20 transition-all flex items-center justify-center group disabled:opacity-50">
                  <span className="material-icons-round text-xl group-hover:translate-x-0.5 transition-transform">send</span>
                </button>
              </div>
            </form>
            <p className="text-center text-xs text-slate-400 mt-3">AI can make mistakes. Please verify important attendance records.</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ChatPage;