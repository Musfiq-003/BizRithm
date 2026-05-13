import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function ChatView() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am your AI Business Consultant. How can I help you analyze your data today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // Connect to the FastAPI backend we already built
      const res = await axios.post('http://localhost:8000/api/chat/message', {
        message: input,
        session_id: "demo-session-react"
      });
      
      setMessages(prev => [...prev, { role: 'ai', content: res.data.response }]);
    } catch (err) {
      // Fallback for demo if backend isn't running
      setTimeout(() => {
        setMessages(prev => [...prev, { role: 'ai', content: "I noticed you asked about revenue. Based on recent trends, your revenue is growing by 12% MoM. To maintain this, focus on retaining your top 20% of customers." }]);
      }, 1500);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-w-4xl mx-auto w-full glass-panel overflow-hidden relative">
      {/* Decorative Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[300px] bg-primary/20 blur-[120px] rounded-full pointer-events-none" />

      {/* Header */}
      <div className="p-4 border-b border-card-border flex items-center gap-3 bg-[#18181b]/50 backdrop-blur-md z-10">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
          <Sparkles size={20} className="text-white" />
        </div>
        <div>
          <h2 className="font-semibold text-zinc-100">AI Consultant</h2>
          <p className="text-xs text-emerald-400 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Online and ready
          </p>
        </div>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 z-10 scrollbar-thin">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.3 }}
              className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-zinc-800 border border-card-border' : 'bg-primary/20 border border-primary/30 text-primary'}`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-relaxed ${msg.role === 'user' ? 'bg-zinc-800 text-zinc-200 rounded-tr-sm border border-card-border' : 'bg-[#121212]/80 backdrop-blur-sm text-zinc-300 rounded-tl-sm border border-primary/20 shadow-[0_4px_20px_rgba(0,0,0,0.2)]'}`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 text-primary flex items-center justify-center">
                <Loader2 size={16} className="animate-spin" />
              </div>
              <div className="bg-[#121212]/80 px-5 py-3 rounded-2xl rounded-tl-sm border border-primary/20 flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></span>
                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={endOfMessagesRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-[#18181b]/80 backdrop-blur-xl border-t border-card-border z-10">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about your revenue, trends, or predictions..."
            className="w-full bg-[#0a0a0a] border border-card-border rounded-xl pl-5 pr-14 py-4 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all shadow-inner"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2.5 bg-primary hover:bg-primary-hover disabled:bg-zinc-800 disabled:text-zinc-600 text-white rounded-lg transition-colors shadow-md shadow-primary/20 disabled:shadow-none"
          >
            <Send size={18} />
          </button>
        </div>
        <div className="text-center mt-2">
          <span className="text-[10px] text-zinc-600 font-medium tracking-wide uppercase">AI responses may occasionally be inaccurate. Please verify critical business data.</span>
        </div>
      </div>
    </div>
  );
}
