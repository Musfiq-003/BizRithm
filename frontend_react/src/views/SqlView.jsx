import { useState } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Database, Table, Play, Search, AlertTriangle } from 'lucide-react';

export default function SqlView() {
  const [query, setQuery] = useState('SELECT date, revenue, active_users \nFROM business_metrics \nORDER BY date DESC \nLIMIT 10;');
  const [isExecuting, setIsExecuting] = useState(false);

  const handleExecute = () => {
    setIsExecuting(true);
    setTimeout(() => setIsExecuting(false), 800);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto h-full flex flex-col">
      <div>
        <h1 className="text-3xl font-bold tracking-tight glow-text mb-1 flex items-center gap-2">
          <Terminal className="text-primary" size={24} /> SQL Explorer
        </h1>
        <p className="text-zinc-400">Write custom queries or let the AI translate natural language into safe PostgreSQL.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Left Col: Query Editor */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="glass-panel flex-1 flex flex-col overflow-hidden">
            <div className="p-3 border-b border-card-border bg-[#18181b]/50 backdrop-blur-md flex justify-between items-center">
              <span className="text-xs font-medium text-zinc-400 flex items-center gap-2">
                <Database size={14} /> editor.sql
              </span>
            </div>
            <textarea
              className="flex-1 w-full bg-[#0a0a0a] text-emerald-400 font-mono text-sm p-4 outline-none resize-none"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              spellCheck="false"
            />
            <div className="p-3 border-t border-card-border bg-[#18181b]/50 backdrop-blur-md">
              <button 
                onClick={handleExecute}
                className="w-full flex items-center justify-center gap-2 py-2 bg-primary hover:bg-primary-hover text-white rounded-md text-sm font-medium transition shadow-lg shadow-primary/20"
              >
                <Play size={14} fill="currentColor" /> {isExecuting ? 'Executing...' : 'Run Query'}
              </button>
            </div>
          </div>

          <div className="glass-panel p-4 bg-amber-500/5 border-amber-500/20">
            <div className="flex gap-3 text-amber-500 mb-2">
              <AlertTriangle size={18} className="shrink-0" />
              <h4 className="text-sm font-medium">Safe Execution Mode</h4>
            </div>
            <p className="text-xs text-amber-500/70 ml-7 leading-relaxed">
              All queries are strictly sanitized. DROP, DELETE, UPDATE, and INSERT operations are blocked by the DB engine.
            </p>
          </div>
        </div>

        {/* Right Col: Results */}
        <div className="lg:col-span-2 glass-panel flex flex-col overflow-hidden relative">
          {/* Subtle grid background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>
          
          <div className="p-4 border-b border-card-border bg-[#18181b]/50 backdrop-blur-md flex justify-between items-center relative z-10">
            <div className="flex items-center gap-2">
              <Table size={16} className="text-zinc-400" />
              <h3 className="text-sm font-medium text-zinc-200">Query Results</h3>
            </div>
            <div className="relative">
              <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-500" />
              <input type="text" placeholder="Filter..." className="pl-8 pr-3 py-1 bg-zinc-900 border border-card-border rounded-md text-xs text-zinc-300 outline-none focus:border-primary w-48" />
            </div>
          </div>

          <div className="flex-1 overflow-auto relative z-10 p-4">
            <div className="rounded-lg overflow-hidden border border-card-border">
              <table className="w-full text-sm text-left">
                <thead className="bg-[#18181b] text-zinc-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">date</th>
                    <th className="px-4 py-3 font-medium">revenue</th>
                    <th className="px-4 py-3 font-medium">active_users</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-card-border bg-[#0a0a0a]">
                  {[
                    ['2026-10-29', '$4,800.00', '4,210'],
                    ['2026-10-22', '$4,600.00', '4,050'],
                    ['2026-10-15', '$4,100.00', '3,890'],
                    ['2026-10-08', '$4,200.00', '3,920'],
                    ['2026-10-01', '$4,000.00', '3,800'],
                  ].map((row, i) => (
                    <motion.tr key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: isExecuting ? i * 0.05 : 0 }} className="hover:bg-zinc-900/50 transition">
                      {row.map((cell, j) => (
                        <td key={j} className={`px-4 py-3 ${j === 0 ? 'text-zinc-300' : 'text-emerald-400 font-mono'}`}>{cell}</td>
                      ))}
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
