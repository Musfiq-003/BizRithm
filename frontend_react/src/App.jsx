import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, MessageSquare, Database, LineChart, FileText, Upload, Settings } from 'lucide-react';
import { useState } from 'react';

// We will implement these views next
import DashboardView from './views/DashboardView';
import ChatView from './views/ChatView';
import ForecastingView from './views/ForecastingView';
import SqlView from './views/SqlView';
import UploadView from './views/UploadView';
import ReportsView from './views/ReportsView';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/chat', label: 'AI Chat', icon: MessageSquare },
  { path: '/sql', label: 'SQL Explorer', icon: Database },
  { path: '/forecast', label: 'Forecasting', icon: LineChart },
  { path: '/reports', label: 'Reports', icon: FileText },
  { path: '/upload', label: 'Data', icon: Upload },
];

function Sidebar() {
  const location = useLocation();
  
  return (
    <div className="w-64 h-screen border-r border-card-border bg-[#0a0a0a]/80 backdrop-blur-xl flex flex-col fixed left-0 top-0">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-lg shadow-[0_0_15px_rgba(99,102,241,0.5)]">
          B
        </div>
        <span className="font-bold text-xl tracking-tight">BizRithm</span>
      </div>
      
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Link key={item.path} to={item.path} className="relative block">
              {isActive && (
                <motion.div 
                  layoutId="activeNav"
                  className="absolute inset-0 bg-primary/10 border border-primary/20 rounded-lg"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2 }}
                />
              )}
              <div className={`relative flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${isActive ? 'text-primary' : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/5'}`}>
                <Icon size={18} className={isActive ? 'text-primary' : ''} />
                <span className="font-medium text-sm">{item.label}</span>
              </div>
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-card-border">
        <button className="flex items-center gap-3 px-4 py-2 text-zinc-400 hover:text-zinc-100 transition-colors w-full rounded-lg hover:bg-white/5">
          <Settings size={18} />
          <span className="font-medium text-sm">Settings</span>
        </button>
      </div>
    </div>
  );
}

function Topbar() {
  return (
    <header className="h-16 border-b border-card-border bg-[#0a0a0a]/80 backdrop-blur-xl sticky top-0 z-10 flex items-center justify-between px-8">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-zinc-400">Workspace / </span>
        <span className="text-sm font-medium text-zinc-100">Production</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-card-border">
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse"></div>
          <span className="text-xs font-medium text-zinc-300">Agents Online</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-zinc-800 border border-card-border"></div>
      </div>
    </header>
  );
}

const PageWrapper = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    transition={{ duration: 0.3 }}
    className="h-full"
  >
    {children}
  </motion.div>
);

export default function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-background text-foreground">
        <Sidebar />
        <main className="flex-1 ml-64 flex flex-col">
          <Topbar />
          <div className="flex-1 p-8 overflow-auto">
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<PageWrapper><DashboardView /></PageWrapper>} />
                <Route path="/chat" element={<PageWrapper><ChatView /></PageWrapper>} />
                <Route path="/forecast" element={<PageWrapper><ForecastingView /></PageWrapper>} />
                <Route path="/sql" element={<PageWrapper><SqlView /></PageWrapper>} />
                <Route path="/upload" element={<PageWrapper><UploadView /></PageWrapper>} />
                <Route path="/reports" element={<PageWrapper><ReportsView /></PageWrapper>} />
              </Routes>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </Router>
  );
}
