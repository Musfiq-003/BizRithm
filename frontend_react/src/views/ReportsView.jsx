import { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, FileDown, ShieldCheck, CheckCircle2, LayoutTemplate } from 'lucide-react';

export default function ReportsView() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDone, setIsDone] = useState(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    setIsDone(false);
    setTimeout(() => {
      setIsGenerating(false);
      setIsDone(true);
      setTimeout(() => setIsDone(false), 3000);
    }, 2000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight glow-text mb-1 flex items-center gap-2">
          <FileText className="text-primary" size={24} /> Automated Reports
        </h1>
        <p className="text-zinc-400">Generate board-ready executive summaries with AI-driven insights.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-panel p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary/20 rounded-lg text-primary">
              <LayoutTemplate size={24} />
            </div>
            <h2 className="text-xl font-semibold text-zinc-100">Report Configuration</h2>
          </div>

          <div className="space-y-5">
            <div>
              <label className="text-sm font-medium text-zinc-400 mb-2 block">Report Type</label>
              <div className="grid grid-cols-2 gap-3">
                <button className="py-2.5 px-4 bg-zinc-800 border border-primary/50 text-zinc-100 rounded-lg text-sm font-medium shadow-inner">
                  Executive Summary
                </button>
                <button className="py-2.5 px-4 bg-[#0a0a0a] border border-card-border text-zinc-400 hover:text-zinc-300 rounded-lg text-sm transition-colors">
                  Deep Dive Analytics
                </button>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-zinc-400 mb-2 block">Include Sections</label>
              <div className="space-y-3 p-4 bg-[#0a0a0a] border border-card-border rounded-xl">
                {[
                  { id: 'kpis', label: 'Key Performance Indicators (KPIs)', checked: true },
                  { id: 'forecasts', label: 'ML Revenue Forecasts', checked: true },
                  { id: 'anomalies', label: 'Anomaly Detection Logs', checked: true },
                  { id: 'strategy', label: 'AI Strategic Recommendations', checked: true }
                ].map(item => (
                  <label key={item.id} className="flex items-center gap-3 cursor-pointer group">
                    <input type="checkbox" defaultChecked={item.checked} className="rounded border-card-border bg-zinc-900 text-primary focus:ring-0 w-4 h-4" />
                    <span className="text-sm text-zinc-300 group-hover:text-zinc-100 transition-colors">{item.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <button 
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full flex items-center justify-center gap-2 py-3.5 bg-primary hover:bg-primary-hover text-white rounded-xl font-medium transition shadow-[0_0_20px_rgba(99,102,241,0.3)] disabled:opacity-70 disabled:shadow-none"
            >
              {isDone ? <CheckCircle2 size={18} /> : <FileDown size={18} className={isGenerating ? "animate-bounce" : ""} />}
              {isGenerating ? "Compiling PDF..." : isDone ? "Report Downloaded!" : "Generate PDF Report"}
            </button>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex flex-col justify-center">
          <div className="bg-[#121212] border border-card-border rounded-2xl p-6 shadow-2xl relative overflow-hidden aspect-[1/1.2] max-w-sm mx-auto w-full">
            {/* PDF Mockup */}
            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-primary to-accent"></div>
            <div className="flex justify-between items-start mb-8 mt-2">
              <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-primary font-bold">B</div>
              <div className="text-right">
                <div className="text-[10px] font-medium text-zinc-500 uppercase tracking-widest">Confidential</div>
                <div className="text-xs text-zinc-400 mt-1">Oct 2026</div>
              </div>
            </div>
            
            <div className="space-y-6">
              <div>
                <div className="h-6 w-3/4 bg-zinc-800 rounded-md mb-2"></div>
                <div className="h-3 w-1/2 bg-zinc-900 rounded-md"></div>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="h-16 bg-zinc-900/50 border border-zinc-800 rounded-lg p-3">
                  <div className="h-2 w-8 bg-zinc-700 rounded mb-3"></div>
                  <div className="h-4 w-16 bg-emerald-500/50 rounded"></div>
                </div>
                <div className="h-16 bg-zinc-900/50 border border-zinc-800 rounded-lg p-3">
                  <div className="h-2 w-8 bg-zinc-700 rounded mb-3"></div>
                  <div className="h-4 w-16 bg-emerald-500/50 rounded"></div>
                </div>
              </div>

              <div className="h-24 bg-zinc-900 rounded-lg border border-zinc-800 relative overflow-hidden">
                <div className="absolute bottom-0 inset-x-0 h-12 bg-gradient-to-t from-primary/20 to-transparent"></div>
                <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                  <path d="M0,80 Q40,60 80,70 T160,40 T240,50 T320,20 L320,100 L0,100 Z" fill="rgba(99,102,241,0.1)" stroke="#6366f1" strokeWidth="1.5" />
                </svg>
              </div>

              <div className="space-y-2">
                <div className="h-2 w-full bg-zinc-800 rounded"></div>
                <div className="h-2 w-full bg-zinc-800 rounded"></div>
                <div className="h-2 w-5/6 bg-zinc-800 rounded"></div>
              </div>
            </div>

            {/* Shield overlay */}
            <div className="absolute bottom-4 right-4 flex items-center gap-1.5 text-xs text-zinc-500">
              <ShieldCheck size={14} className="text-emerald-500" /> Auto-Generated
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
