
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Gavel, Scale } from 'lucide-react';

const Login = () => {
    const navigate = useNavigate();

    const handleLogin = (role) => {
        navigate(`/${role}`);
    };

    return (
        <div className="flex h-screen items-center justify-center bg-slate-900 text-slate-100">
            <div className="text-center space-y-8">
                <div className="space-y-2">
                    <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-slate-200 to-amber-400 bg-clip-text text-transparent">
                        The Bench
                    </h1>
                    <p className="text-slate-400 text-sm uppercase tracking-[0.2em]">Three Perspectives. One Truth.</p>
                </div>

                <div className="flex gap-6 mt-12">
                    {/* Accuser Button */}
                    <button
                        onClick={() => handleLogin('accuser')}
                        className="group relative w-40 h-48 bg-slate-800 border border-slate-700 hover:border-blue-500 rounded-xl p-6 flex flex-col items-center justify-center gap-4 transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(59,130,246,0.2)]"
                    >
                        <div className="p-3 bg-slate-900 rounded-full group-hover:bg-blue-500/20 transition-colors">
                            <Scale size={32} className="text-blue-500" />
                        </div>
                        <span className="font-semibold text-slate-300 group-hover:text-blue-400">Accuser</span>
                    </button>

                    {/* Judge Button */}
                    <button
                        onClick={() => handleLogin('judge')}
                        className="group relative w-40 h-48 bg-slate-800 border border-slate-700 hover:border-amber-500 rounded-xl p-6 flex flex-col items-center justify-center gap-4 transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(245,158,11,0.2)] z-10"
                    >
                        <div className="absolute -top-3 px-3 py-1 bg-amber-500/10 border border-amber-500/50 rounded-full text-[10px] text-amber-500 font-bold uppercase tracking-wider">
                            Presiding
                        </div>
                        <div className="p-3 bg-slate-900 rounded-full group-hover:bg-amber-500/20 transition-colors">
                            <Gavel size={32} className="text-amber-500" />
                        </div>
                        <span className="font-semibold text-slate-300 group-hover:text-amber-400">Judge</span>
                    </button>

                    {/* Accused Button */}
                    <button
                        onClick={() => handleLogin('accused')}
                        className="group relative w-40 h-48 bg-slate-800 border border-slate-700 hover:border-red-500 rounded-xl p-6 flex flex-col items-center justify-center gap-4 transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(239,68,68,0.2)]"
                    >
                        <div className="p-3 bg-slate-900 rounded-full group-hover:bg-red-500/20 transition-colors">
                            <Shield size={32} className="text-red-500" />
                        </div>
                        <span className="font-semibold text-slate-300 group-hover:text-red-400">Accused</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;
