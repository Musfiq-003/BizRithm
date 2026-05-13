import { useState } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud, FileSpreadsheet, Database, CheckCircle2 } from 'lucide-react';

export default function UploadView() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files).map(f => ({
        name: f.name,
        size: (f.size / 1024).toFixed(2) + ' KB',
        status: 'Success'
      }));
      setUploadedFiles(prev => [...prev, ...newFiles]);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight glow-text mb-1">Data Ingestion</h1>
        <p className="text-zinc-400">Securely upload your business datasets to the BizRithm vector store.</p>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`mt-8 border-2 border-dashed rounded-2xl p-12 text-center transition-all ${isDragging ? 'border-primary bg-primary/5 shadow-[0_0_30px_rgba(99,102,241,0.2)]' : 'border-card-border bg-card'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="w-16 h-16 bg-zinc-900 border border-card-border rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
          <UploadCloud className="text-primary" size={32} />
        </div>
        <h3 className="text-xl font-semibold text-zinc-100 mb-2">Drag and drop your data</h3>
        <p className="text-zinc-400 text-sm mb-6 max-w-sm mx-auto">
          We support CSV, Excel, and JSON files. Data is automatically encrypted and processed into PostgreSQL.
        </p>
        <div className="flex justify-center gap-4">
          <button className="px-6 py-2.5 bg-zinc-100 text-zinc-900 rounded-lg font-medium hover:bg-white transition shadow-lg">
            Browse Files
          </button>
          <button className="px-6 py-2.5 bg-zinc-900 border border-card-border text-zinc-300 rounded-lg font-medium hover:bg-zinc-800 transition">
            Import Demo Data
          </button>
        </div>
      </motion.div>

      {uploadedFiles.length > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-8">
          <h3 className="text-sm font-semibold text-zinc-100 mb-4 flex items-center gap-2">
            <Database size={16} className="text-primary" /> Processed Datasets
          </h3>
          <div className="space-y-3">
            {uploadedFiles.map((file, idx) => (
              <div key={idx} className="glass-panel p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-zinc-900 rounded-lg text-emerald-400">
                    <FileSpreadsheet size={20} />
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-zinc-100">{file.name}</h4>
                    <p className="text-xs text-zinc-500">{file.size} • 100% indexed</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs font-medium text-emerald-400 bg-emerald-400/10 px-3 py-1.5 rounded-full">
                  <CheckCircle2 size={14} /> Ready
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
