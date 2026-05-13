import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  AreaChart, Area, BarChart, Bar, ComposedChart, Line, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { 
  ArrowUpRight, TrendingUp, DollarSign, Users, Activity, RefreshCw, 
  Download, Check, Calendar, AlertTriangle, Zap, CheckCircle2 
} from 'lucide-react';

const revenueData = [
  { name: 'Jan', value: 4000 }, { name: 'Feb', value: 3000 }, { name: 'Mar', value: 2000 },
  { name: 'Apr', value: 2780 }, { name: 'May', value: 1890 }, { name: 'Jun', value: 2390 },
  { name: 'Jul', value: 3490 }, { name: 'Aug', value: 4200 }, { name: 'Sep', value: 3800 },
  { name: 'Oct', value: 5100 }, { name: 'Nov', value: 5900 }, { name: 'Dec', value: 7200 },
];

const regionData = [
  { name: 'NA', revenue: 4000 }, { name: 'EU', revenue: 3000 }, 
  { name: 'APAC', revenue: 2000 }, { name: 'LATAM', revenue: 1500 }
];

const customerData = [
  { name: 'Q1', acquired: 1200, churned: 300, net: 900 },
  { name: 'Q2', acquired: 1500, churned: 400, net: 1100 },
  { name: 'Q3', acquired: 2200, churned: 350, net: 1850 },
  { name: 'Q4', acquired: 3100, churned: 500, net: 2600 },
];

const kpis = [
  { title: "Total Revenue", value: "$1.2M", change: "+12.4%", icon: DollarSign },
  { title: "Active Users", value: "48.2K", change: "+8.2%", icon: Users },
  { title: "Growth Rate", value: "24.1%", change: "+4.1%", icon: TrendingUp },
  { title: "System Health", value: "99.9%", change: "Optimal", icon: Activity },
];

const activityFeed = [
  { id: 1, time: "2 min ago", type: "alert", text: "Revenue anomaly detected in EU region", icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10" },
  { id: 2, time: "1 hr ago", type: "ai", text: "AI generated Q3 Forecasting Report", icon: Zap, color: "text-primary", bg: "bg-primary/10" },
  { id: 3, time: "3 hrs ago", type: "success", text: "Stripe data sync completed", icon: CheckCircle2, color: "text-emerald-500", bg: "bg-emerald-500/10" },
  { id: 4, time: "5 hrs ago", type: "ai", text: "Optimization insight available for Ad Spend", icon: Zap, color: "text-primary", bg: "bg-primary/10" },
  { id: 5, time: "1 day ago", type: "success", text: "Monthly batch processing finished", icon: CheckCircle2, color: "text-emerald-500", bg: "bg-emerald-500/10" },
];

export default function DashboardView() {
  const [isSyncing, setIsSyncing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [syncDone, setSyncDone] = useState(false);
  const [exportDone, setExportDone] = useState(false);
  const [dateRange, setDateRange] = useState("Last 30 Days");

  const handleSync = () => {
    setIsSyncing(true); setSyncDone(false);
    setTimeout(() => {
      setIsSyncing(false); setSyncDone(true);
      setTimeout(() => setSyncDone(false), 2000);
    }, 1500);
  };

  const handleExport = () => {
    setIsExporting(true); setExportDone(false);
    setTimeout(() => {
      setIsExporting(false); setExportDone(true);
      setTimeout(() => setExportDone(false), 2000);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight glow-text mb-1">Command Center</h1>
          <p className="text-zinc-400">Live analytics and AI insights for your business.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Global Date Range */}
          <div className="flex items-center bg-zinc-900 border border-card-border rounded-lg px-3 py-2">
            <Calendar size={16} className="text-zinc-400 mr-2" />
            <select 
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="bg-transparent text-sm font-medium text-zinc-100 outline-none focus:ring-0 cursor-pointer"
            >
              <option>Today</option>
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
              <option>Year to Date</option>
              <option>All Time</option>
            </select>
          </div>

          <button 
            onClick={handleExport} disabled={isExporting}
            className="flex items-center gap-2 px-4 py-2 bg-[#121212] border border-card-border rounded-lg text-sm font-medium hover:bg-zinc-800 transition disabled:opacity-70"
          >
            {exportDone ? <Check size={16} className="text-emerald-400" /> : <Download size={16} className={isExporting ? "animate-bounce" : ""} />}
            <span className="hidden sm:inline">{isExporting ? "Exporting..." : exportDone ? "Exported!" : "Export CSV"}</span>
          </button>
          <button 
            onClick={handleSync} disabled={isSyncing}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover shadow-[0_0_15px_rgba(99,102,241,0.4)] transition disabled:opacity-70 disabled:shadow-none"
          >
            {syncDone ? <Check size={16} /> : <RefreshCw size={16} className={isSyncing ? "animate-spin" : ""} />}
            <span className="hidden sm:inline">{isSyncing ? "Syncing..." : syncDone ? "Synced!" : "Trigger Sync"}</span>
          </button>
        </div>
      </div>

      {/* KPIs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {kpis.map((kpi, i) => (
          <motion.div
            key={kpi.title}
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
            className="glass-panel p-5 group hover:border-primary/50 transition-colors relative overflow-hidden"
          >
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors"></div>
            <div className="flex justify-between items-start mb-3">
              <div className="p-2 bg-zinc-900 rounded-lg text-zinc-400 group-hover:text-primary transition-colors border border-card-border">
                <kpi.icon size={18} />
              </div>
              <span className="flex items-center text-xs font-semibold text-emerald-400 bg-emerald-400/10 px-2.5 py-1 rounded-full border border-emerald-400/20">
                {kpi.change} <ArrowUpRight size={12} className="ml-1" />
              </span>
            </div>
            <h3 className="text-3xl font-bold text-zinc-100 mb-1">{kpi.value}</h3>
            <p className="text-xs text-zinc-500 font-medium uppercase tracking-wider">{kpi.title}</p>
          </motion.div>
        ))}
      </div>

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Column: Charts */}
        <div className="xl:col-span-2 space-y-6">
          {/* Main Revenue Area Chart */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="glass-panel p-6 h-[350px] flex flex-col"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
                <TrendingUp size={18} className="text-primary" /> Revenue Trajectory
              </h2>
            </div>
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={revenueData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" />
                  <XAxis dataKey="name" stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#6366f1' }}
                  />
                  <Area type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Secondary Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Regional Bar Chart */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
              className="glass-panel p-5 h-[280px] flex flex-col"
            >
              <h2 className="text-sm font-semibold text-zinc-300 mb-4">Revenue by Region</h2>
              <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={regionData} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" />
                    <XAxis dataKey="name" stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                    <Tooltip cursor={{fill: '#27272a', opacity: 0.4}} contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }} />
                    <Bar dataKey="revenue" fill="#818cf8" radius={[4, 4, 0, 0]} barSize={30} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Acquisition vs Churn Composed Chart */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
              className="glass-panel p-5 h-[280px] flex flex-col"
            >
              <h2 className="text-sm font-semibold text-zinc-300 mb-4">Acquisition vs Churn</h2>
              <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={customerData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" />
                    <XAxis dataKey="name" stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="#52525b" fontSize={11} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', fontSize: '12px' }} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    <Bar dataKey="acquired" name="Acquired" fill="#10b981" radius={[2, 2, 0, 0]} barSize={20} />
                    <Bar dataKey="churned" name="Churned" fill="#ef4444" radius={[2, 2, 0, 0]} barSize={20} />
                    <Line type="monotone" dataKey="net" name="Net Trend" stroke="#6366f1" strokeWidth={2} dot={{ r: 4 }} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Right Column: Activity Feed */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
          className="glass-panel flex flex-col h-full xl:max-h-[654px]"
        >
          <div className="p-5 border-b border-card-border">
            <h2 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
              <Activity size={18} className="text-primary" /> Live Activity Feed
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar relative">
            {/* Timeline line */}
            <div className="absolute left-[31px] top-6 bottom-6 w-px bg-zinc-800"></div>
            
            {activityFeed.map((activity, i) => (
              <motion.div 
                key={activity.id}
                initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + (i * 0.1) }}
                className="flex gap-4 relative z-10"
              >
                <div className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center border border-card-border ${activity.bg}`}>
                  <activity.icon size={14} className={activity.color} />
                </div>
                <div className="flex-1 pt-1">
                  <p className="text-sm text-zinc-300 leading-snug mb-1">{activity.text}</p>
                  <p className="text-[11px] font-medium text-zinc-500">{activity.time}</p>
                </div>
              </motion.div>
            ))}
          </div>
          <div className="p-4 border-t border-card-border bg-[#0a0a0a]/50">
            <button className="w-full text-xs font-medium text-zinc-400 hover:text-primary transition-colors py-1">
              View All Logs
            </button>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
