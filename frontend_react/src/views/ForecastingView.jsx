import { useState } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Settings2, Play, AlertCircle, Sparkles } from 'lucide-react';

const forecastData = [
  { date: 'Oct 01', actual: 4000, prophet: null, xgboost: null },
  { date: 'Oct 08', actual: 4200, prophet: null, xgboost: null },
  { date: 'Oct 15', actual: 4100, prophet: null, xgboost: null },
  { date: 'Oct 22', actual: 4600, prophet: null, xgboost: null },
  { date: 'Oct 29', actual: 4800, prophet: null, xgboost: null },
  { date: 'Nov 05', actual: null, prophet: 5100, xgboost: 4900 },
  { date: 'Nov 12', actual: null, prophet: 5300, xgboost: 5050 },
  { date: 'Nov 19', actual: null, prophet: 5600, xgboost: 5400 },
  { date: 'Nov 26', actual: null, prophet: 5900, xgboost: 5750 },
  { date: 'Dec 03', actual: null, prophet: 6100, xgboost: 6000 },
];

export default function ForecastingView() {
  const [activeModel, setActiveModel] = useState('All');

  return (
    <div className="space-y-6 max-w-6xl mx-auto h-full flex flex-col">
      <div>
        <h1 className="text-3xl font-bold tracking-tight glow-text mb-1 flex items-center gap-2">
          <Sparkles className="text-primary" size={24} /> ML Forecast Engine
        </h1>
        <p className="text-zinc-400">Predict future business metrics using advanced ensemble models.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        {/* Controls Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <div className="glass-panel p-5 space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2 mb-4">
                <Settings2 size={16} className="text-primary" /> Configuration
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-zinc-500 mb-1.5 block">Target Metric</label>
                  <select className="w-full bg-[#0a0a0a] border border-card-border text-zinc-300 text-sm rounded-lg px-3 py-2 outline-none focus:border-primary transition-colors">
                    <option>Revenue</option>
                    <option>Active Users</option>
                    <option>Profit Margin</option>
                  </select>
                </div>
                
                <div>
                  <label className="text-xs font-medium text-zinc-500 mb-1.5 block">Forecast Horizon</label>
                  <select className="w-full bg-[#0a0a0a] border border-card-border text-zinc-300 text-sm rounded-lg px-3 py-2 outline-none focus:border-primary transition-colors">
                    <option>30 Days</option>
                    <option>60 Days</option>
                    <option>90 Days</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-zinc-500 mb-1.5 block">Models</label>
                  <div className="space-y-2">
                    {['Prophet', 'XGBoost', 'Random Forest', 'LSTM'].map(model => (
                      <label key={model} className="flex items-center gap-2 text-sm text-zinc-300 cursor-pointer group">
                        <input type="checkbox" defaultChecked={['Prophet', 'XGBoost'].includes(model)} className="rounded border-card-border bg-[#0a0a0a] text-primary focus:ring-primary/50 focus:ring-offset-0" />
                        <span className="group-hover:text-zinc-100 transition-colors">{model}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-card-border">
              <button className="w-full flex items-center justify-center gap-2 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary/20">
                <Play size={16} fill="currentColor" /> Run Forecast
              </button>
            </div>
          </div>

          {/* Model Stats */}
          <div className="glass-panel p-5">
             <h3 className="text-sm font-semibold text-zinc-100 mb-4">Model Performance</h3>
             <div className="space-y-3">
               <div className="flex justify-between items-center text-sm">
                 <span className="text-zinc-400">Prophet R²</span>
                 <span className="text-emerald-400 font-mono bg-emerald-400/10 px-1.5 rounded">0.942</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-zinc-400">XGBoost R²</span>
                 <span className="text-emerald-400 font-mono bg-emerald-400/10 px-1.5 rounded">0.915</span>
               </div>
               <div className="flex justify-between items-center text-sm pt-3 border-t border-card-border">
                 <span className="text-zinc-400">Best Model</span>
                 <span className="text-primary font-medium">Prophet</span>
               </div>
             </div>
          </div>
        </div>

        {/* Chart Area */}
        <div className="lg:col-span-3 glass-panel p-6 flex flex-col relative overflow-hidden">
          {/* Subtle grid background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>

          <div className="relative z-10 flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-zinc-100">Revenue Projection (Next 30 Days)</h2>
            <div className="flex bg-[#0a0a0a] p-1 rounded-lg border border-card-border">
              {['All', 'Prophet', 'XGBoost'].map(m => (
                <button 
                  key={m}
                  onClick={() => setActiveModel(m)}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${activeModel === m ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>
          
          <div className="relative z-10 flex-1 w-full min-h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecastData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" />
                <XAxis dataKey="date" stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px' }}
                  itemStyle={{ fontSize: '13px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} />
                
                <Line type="monotone" dataKey="actual" name="Historical Data" stroke="#a1a1aa" strokeWidth={2} dot={{ r: 4, fill: '#18181b', strokeWidth: 2 }} activeDot={{ r: 6 }} />
                
                {(activeModel === 'All' || activeModel === 'Prophet') && (
                  <Line type="monotone" dataKey="prophet" name="Prophet Forecast" stroke="#6366f1" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 4, fill: '#18181b', strokeWidth: 2 }} />
                )}
                
                {(activeModel === 'All' || activeModel === 'XGBoost') && (
                  <Line type="monotone" dataKey="xgboost" name="XGBoost Forecast" stroke="#06b6d4" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 4, fill: '#18181b', strokeWidth: 2 }} />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="relative z-10 mt-6 bg-primary/10 border border-primary/20 rounded-lg p-4 flex gap-3">
            <AlertCircle className="text-primary shrink-0" size={20} />
            <div>
              <h4 className="text-sm font-medium text-primary-light">Insight Alert</h4>
              <p className="text-xs text-zinc-300 mt-1">The Prophet model projects a <strong className="text-emerald-400">27% revenue increase</strong> by December 3rd, driven by seasonal holiday trends detected in historical data.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
