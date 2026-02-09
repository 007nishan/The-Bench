
import React, { useState } from 'react';

const WarRoom = ({ role }) => {
    const [messages, setMessages] = useState([
        { sender: 'AI', text: `Welcome to your War Room, ${role}. What is our strategy today?` },
    ]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSend = async () => {
        if (!inputText.trim()) return;

        // 1. Add User Message
        const userMsg = { sender: 'User', text: inputText };
        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setIsLoading(true);

        try {
            // 2. Call Backend API
            const response = await fetch('http://localhost:8000/chat/strategy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_role: role,
                    query_text: inputText
                }),
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();

            // 3. Add AI Response
            setMessages(prev => [...prev, { sender: 'AI', text: data.response || "No strategy found." }]);
        } catch (error) {
            setMessages(prev => [...prev, { sender: 'System', text: "Error connecting to The Bench AI. Please ensure the backend server is running." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmitToJudge = async () => {
        if (!inputText.trim()) return;

        const argumentText = inputText;
        setMessages(prev => [...prev, { sender: 'User', text: `[FILING MOTION] ${argumentText}` }]);
        setInputText('');
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/submit_argument', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_role: role,
                    argument_text: argumentText,
                    evidence_ids: [] // Future: Add evidence selection
                }),
            });

            if (!response.ok) throw new Error('Submission Failed');

            const result = await response.json();

            setMessages(prev => [...prev, {
                sender: 'System',
                text: `✅ Motion Filed with The Bench.\nSubmission ID: ${result.submission_id}\nStatus: ${result.status}`
            }]);
        } catch (error) {
            setMessages(prev => [...prev, { sender: 'System', text: "❌ Filing Failed. The Clerk could not process your request." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full space-y-4">
            {/* Chat Area */}
            <div className="flex-1 bg-slate-800/50 rounded-lg p-4 custom-scrollbar overflow-y-auto space-y-4 border border-slate-700/50">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg p-3 ${msg.sender === 'User' ? 'bg-blue-600 text-white' :
                            msg.sender === 'System' ? 'bg-red-900/50 text-red-200 border border-red-500' :
                                'bg-slate-700 text-slate-200'
                            }`}>
                            <div className="flex justify-between items-center gap-4 mb-1">
                                <span className="text-xs font-bold opacity-70">
                                    {msg.sender === 'User' ? 'You' : msg.sender === 'System' ? '⚠️ System Alert' : 'Strategist AI'}
                                </span>
                                <span className="text-[10px] opacity-50 font-mono">
                                    {msg.timestamp || new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                            <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-slate-700/50 p-3 rounded-lg animate-pulse text-slate-400 text-xs">
                            Thinking...
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="h-32 bg-slate-800 rounded-lg border border-slate-700 p-2 flex flex-col gap-2 relative">
                <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    placeholder="Ask for a strategy or draft an official argument..."
                    className="flex-1 bg-transparent resize-none outline-none text-slate-200 placeholder-slate-500 text-sm font-mono custom-scrollbar"
                />
                <div className="flex justify-between items-center px-2 bg-slate-800/50 pt-2 border-t border-slate-700/50">
                    <span className="text-xs text-slate-500">Shift+Enter for new line</span>
                    <div className="flex gap-2">
                        <button
                            onClick={handleSend}
                            disabled={isLoading}
                            className="bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-slate-200 px-3 py-1 rounded text-xs font-semibold transition-colors border border-slate-600"
                        >
                            {isLoading ? 'Thinking...' : 'Ask Strategist'}
                        </button>
                        <button
                            onClick={handleSubmitToJudge}
                            disabled={isLoading || !inputText.trim()}
                            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-3 py-1 rounded text-xs font-semibold transition-colors flex items-center gap-1"
                        >
                            <span>⚖️</span> File Motion
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WarRoom;
