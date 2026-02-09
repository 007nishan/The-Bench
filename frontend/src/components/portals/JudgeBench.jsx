
import React, { useState, useEffect } from 'react';

const JudgeBench = () => {
    const [submissions, setSubmissions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [verifyingId, setVerifyingId] = useState(null);

    // Fetch Pending Submissions
    useEffect(() => {
        const fetchPending = async () => {
            try {
                const res = await fetch('http://localhost:8000/judge/pending');
                if (res.ok) {
                    const data = await res.json();
                    setSubmissions(data);
                }
            } catch (err) {
                console.error("Failed to fetch pending cases:", err);
            }
        };

        // Initial fetch + Poll every 5s
        fetchPending();
        const interval = setInterval(fetchPending, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleVerify = async (id) => {
        setVerifyingId(id);

        try {
            const res = await fetch('http://localhost:8000/judge/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ submission_id: id })
            });

            if (res.ok) {
                const result = await res.json();
                // Update local state with result (or just refetch)
                const updated = result.details;
                setSubmissions(prev => prev.map(s => s.id === id ? updated : s));
            }
        } catch (err) {
            console.error("Verification failed:", err);
        } finally {
            setVerifyingId(null);
        }
    };

    return (
        <div className="flex flex-col h-full space-y-6">
            <div className="flex items-center justify-between text-slate-300">
                <h2 className="text-xl font-bold">Pending Review</h2>
                <span className="text-xs bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
                    {submissions.filter(s => s.status === 'pending').length} Actions Required
                </span>
            </div>

            <div className="space-y-4">
                {submissions.length === 0 && (
                    <div className="text-center text-slate-500 py-10 italic">
                        No pending arguments. The Bench is clear.
                    </div>
                )}

                {submissions.map((sub) => (
                    <div key={sub.id} className="bg-slate-800 rounded-lg border border-slate-700 p-6 shadow-sm relative overflow-hidden group">

                        {/* Status Bar */}
                        <div className={`absolute top-0 left-0 w-1 h-full transition-colors duration-500 ${sub.status === 'admitted' ? 'bg-green-500' :
                            sub.status === 'rejected' ? 'bg-red-500' :
                                'bg-amber-500'
                            }`}></div>

                        <div className="flex justify-between items-start mb-4 pl-4 gap-4">
                            <div className="flex-1">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                                        Filed by: {sub.sender}
                                    </span>
                                    <span className="text-[10px] font-mono text-slate-500">{sub.timestamp}</span>
                                </div>

                                <p className="text-slate-200 text-lg leading-relaxed font-serif bg-slate-900/30 p-3 rounded border border-slate-700/50">
                                    "{sub.argument}"
                                </p>

                                {/* AI Notes (Only visible after verification) */}
                                {sub.status !== 'pending' && sub.ai_notes && (
                                    <div className={`mt-3 text-sm p-3 rounded border ${sub.status === 'admitted' ? 'bg-green-900/10 border-green-900/30 text-green-300' : 'bg-red-900/10 border-red-900/30 text-red-300'
                                        }`}>
                                        <strong className="block mb-1 opacity-70">BENCH RULING NOTES:</strong>
                                        <div className="whitespace-pre-wrap">{sub.ai_notes}</div>
                                    </div>
                                )}
                            </div>

                            {/* Action Button */}
                            {sub.status === 'pending' && (
                                <button
                                    onClick={() => handleVerify(sub.id)}
                                    disabled={verifyingId === sub.id}
                                    className={`shrink-0 px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-[0_0_15px_rgba(245,158,11,0.2)] ${verifyingId === sub.id
                                        ? 'bg-slate-700 text-slate-400 cursor-wait'
                                        : 'bg-amber-500 hover:bg-amber-400 text-slate-900'
                                        }`}
                                >
                                    {verifyingId === sub.id ? 'Auditing...' : 'Verify Schema'}
                                </button>
                            )}
                            {sub.status !== 'pending' && (
                                <div className={`shrink-0 px-3 py-1 rounded text-xs font-bold uppercase border ${sub.status === 'admitted' ? 'border-green-500 text-green-500' : 'border-red-500 text-red-500'
                                    }`}>
                                    {sub.status}
                                </div>
                            )}
                        </div>

                        {/* References Footer */}
                        <div className="pl-4 border-t border-slate-700/50 pt-3 flex flex-wrap gap-2">
                            {sub.references && sub.references.map((ref, i) => (
                                <span key={i} className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded flex items-center gap-1 hover:bg-slate-600 cursor-pointer">
                                    📄 {ref}
                                </span>
                            ))}
                            {(!sub.references || sub.references.length === 0) && (
                                <span className="text-xs text-red-400 flex items-center gap-1">
                                    ⚠️ No citations provided
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default JudgeBench;
