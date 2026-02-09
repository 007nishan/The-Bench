
import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

const DashboardLayout = ({ role, children }) => {
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [uploadStatus, setUploadStatus] = useState(null); // 'uploading', 'success', 'error'
    const [currentTime, setCurrentTime] = useState(new Date());
    const [courtLog, setCourtLog] = useState([]);
    const fileInputRef = useRef(null);

    // Live Clock & Court Log
    React.useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);

        const fetchLog = async () => {
            try {
                const res = await fetch('http://localhost:8000/court_log');
                if (res.ok) {
                    const data = await res.json();
                    setCourtLog(data);
                }
            } catch (e) {
                console.error("Log fetch error", e);
            }
        };
        fetchLog(); // Initial
        const logTimer = setInterval(fetchLog, 3000);

        return () => {
            clearInterval(timer);
            clearInterval(logTimer);
        };
    }, []);

    const getRoleColor = () => {
        switch (role) {
            case 'accuser': return 'border-blue-500';
            case 'accused': return 'border-red-500';
            case 'judge': return 'border-amber-500';
            default: return 'border-gray-500';
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setUploadStatus('uploading');
        const formData = new FormData();
        formData.append('user_role', role);
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/upload_doc', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Upload failed');

            const data = await response.json();

            setUploadedFiles(prev => [...prev, file.name]);
            setUploadStatus('success');
            setTimeout(() => setUploadStatus(null), 3000);
        } catch (error) {
            console.error("Upload Error:", error);
            setUploadStatus('error');
            setTimeout(() => setUploadStatus(null), 3000);
        }
    };

    return (
        <div className="flex h-screen bg-slate-900 text-slate-100 overflow-hidden font-sans">
            {/* LEFT SIDEBAR: Private Context */}
            <aside className="w-1/5 bg-slate-800 border-r border-slate-700 p-4 flex flex-col">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        {role === 'judge' ? 'Case Files' : 'Private Vault'}
                    </h2>
                    {role !== 'judge' && (
                        <button
                            onClick={() => fileInputRef.current.click()}
                            className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition"
                            title="Upload Evidence"
                        >
                            <Upload size={16} />
                        </button>
                    )}
                </div>

                {/* Hidden Input */}
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    className="hidden"
                    accept=".txt,.md,.json"
                />

                {/* Upload Status */}
                {uploadStatus === 'uploading' && <div className="text-xs text-blue-400 mb-2 animate-pulse">Uploading...</div>}
                {uploadStatus === 'success' && <div className="text-xs text-green-400 mb-2 flex items-center gap-1"><CheckCircle size={12} /> Uploaded</div>}
                {uploadStatus === 'error' && <div className="text-xs text-red-400 mb-2 flex items-center gap-1"><AlertCircle size={12} /> Failed</div>}

                <div className="flex-1 overflow-y-auto space-y-2 custom-scrollbar pr-1">
                    {/* Default Files (Mock) */}
                    <div className="p-2 bg-slate-700/50 rounded text-sm hover:bg-slate-700 cursor-pointer transition flex items-center gap-2 group">
                        <FileText size={14} className="text-slate-500 group-hover:text-slate-300" />
                        <span className="truncate">Case Strategy.docx</span>
                    </div>

                    {/* Uploaded Files */}
                    {uploadedFiles.map((fname, idx) => (
                        <div key={idx} className="p-2 bg-slate-700/30 border border-slate-600/50 rounded text-sm hover:bg-slate-700 cursor-pointer transition flex items-center gap-2 group">
                            <FileText size={14} className="text-blue-500/70 group-hover:text-blue-400" />
                            <span className="truncate">{fname}</span>
                        </div>
                    ))}
                </div>
            </aside>

            {/* CENTER: Main Workspace */}
            <main className={`flex-1 flex flex-col relative bg-slate-900 ${getRoleColor()} border-x-4`}>
                <header className="h-14 bg-slate-800/50 border-b border-slate-700 flex items-center justify-between px-6">
                    <h1 className="text-lg font-semibold capitalize flex items-center gap-2">
                        {role === 'judge' ? 'The Bench' : `${role}'s War Room`}
                    </h1>
                    <div className="flex items-center gap-4">
                        <span className="text-xs font-mono text-slate-400">
                            {currentTime.toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit' })} IST
                        </span>
                        <span className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300 flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                            Session Active
                        </span>
                    </div>
                </header>

                <div className="flex-1 p-6 overflow-y-auto relative custom-scrollbar">
                    {children}
                </div>
            </main>

            {/* RIGHT SIDEBAR: Common Ground */}
            <aside className="w-1/4 bg-slate-800 border-l border-slate-700 p-4 flex flex-col">
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
                    <span>🏛️</span> Court Record
                </h2>
                <div className="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar">
                    {courtLog.length === 0 && (
                        <div className="border-l-2 border-slate-600 pl-3 py-1 opacity-60">
                            <span className="text-[10px] text-slate-400">System</span>
                            <p className="text-sm text-slate-400 mt-1 italic">Session commenced. No activity yet.</p>
                        </div>
                    )}

                    {[...courtLog].reverse().map((log, i) => (
                        <div key={i} className={`border-l-2 pl-3 py-1 ${log.actor === 'Judge' ? 'border-amber-500' :
                            log.actor === 'Accuser' ? 'border-blue-500' :
                                log.actor === 'Accused' ? 'border-red-500' :
                                    'border-slate-600'
                            }`}>
                            <span className="text-[10px] text-slate-400 font-mono">{log.timestamp} • {log.actor}</span>
                            <div className="text-sm text-slate-200 mt-1">
                                <span className="font-semibold block text-xs opacity-70 mb-0.5">{log.action}</span>
                                {log.details}
                            </div>
                        </div>
                    ))}
                </div>
            </aside>
        </div>
    );
};

export default DashboardLayout;
