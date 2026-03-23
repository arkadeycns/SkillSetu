import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import { Mic, Square, Loader2, User, Bot, Trash2, Send, ChevronLeft, BookOpen } from 'lucide-react'; 
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';
import { sendAudioToGuidanceChat, startGuidanceChat } from '../api/aiService';

export default function GuidanceChat() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [sessionId] = useState(location.state?.sessionId || `chat_${Date.now()}`);
  const sessionLang = location.state?.lang || "English";
  const sessionSkill = location.state?.skill || "";

  const { isRecording, startRecording, stopRecording } = useVoiceRecorder();
  
  // Start empty. The backend will send the first message!
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(true); 
  const [stagedAudioBlob, setStagedAudioBlob] = useState(null);
  const [stagedAudioUrl, setStagedAudioUrl] = useState(null);
  
  const chatEndRef = useRef(null);
  const hasInitialized = useRef(false);

  const fallbackGreeting = (() => {
    const roleText = sessionSkill || "your trade";
    const lang = (sessionLang || "English").toLowerCase();
    if (lang === "hindi" || lang === "hinglish") {
      return `Namaste. ${roleText} role ke liye aapko step-by-step guidance dunga. Aaj kis practical problem par kaam karna hai?`;
    }
    return `Welcome. I will guide you step by step for ${roleText}. What practical problem do you want to improve today?`;
  })();

  // ==========================================================
  // THE HANDSHAKE (Calling the new /start endpoint)
  // ==========================================================
  useEffect(() => {
    const initializeChat = async () => {
      try {
        const aiResult = await startGuidanceChat(sessionId, sessionLang, sessionSkill);
        
        if (aiResult && (aiResult.text || aiResult.audioUrl)) {
          setMessages([{ 
            sender: 'ai', 
            text: aiResult.text, 
            audioUrl: aiResult.audioUrl 
          }]);
        } else {
          setMessages([{ sender: 'ai', text: fallbackGreeting }]);
        }
      } catch (error) {
        setMessages([{ sender: 'ai', text: fallbackGreeting }]);
      } finally {
        setIsProcessing(false);
      }
    };

    if (!hasInitialized.current && messages.length === 0) {
      hasInitialized.current = true;
      initializeChat();
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isProcessing, stagedAudioUrl]);

  const handleRecordToggle = async () => {
    if (isRecording) {
      const audioBlob = await stopRecording();
      if (!audioBlob) return;
      setStagedAudioBlob(audioBlob);
      setStagedAudioUrl(URL.createObjectURL(audioBlob));
    } else {
      await startRecording();
    }
  };

  const handleCancelAudio = () => {
    setStagedAudioBlob(null);
    setStagedAudioUrl(null);
  };

  const handleSendAudio = async () => {
    if (!stagedAudioBlob) return;

    setMessages(prev => [...prev, { sender: 'user', audioUrl: stagedAudioUrl }]);
    
    const blobToSend = stagedAudioBlob;
    setStagedAudioBlob(null);
    setStagedAudioUrl(null);
    
    setIsProcessing(true);
    
    // Pass the language context to every chat!
    const aiResult = await sendAudioToGuidanceChat(blobToSend, sessionId, sessionLang, sessionSkill);
    setIsProcessing(false);

    if (aiResult && (aiResult.text || aiResult.audioUrl)) {
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: aiResult.text || "Here is your guidance.", 
        audioUrl: aiResult.audioUrl 
      }]);
    } else if (aiResult && aiResult.error) {
      alert(aiResult.error);
    } else {
      alert("AI is having trouble connecting. Check your internet.");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-200 font-sans">
      
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-md border-b border-slate-700 p-4 flex items-center justify-between relative z-20">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-slate-700 rounded-full transition-colors text-slate-400"
        >
          <ChevronLeft size={24} />
        </button>
        
        <div className="text-center absolute left-1/2 -translate-x-1/2 flex items-center gap-2">
          <BookOpen className="text-blue-400" size={20} />
          <h1 className="text-lg font-bold text-white tracking-wide uppercase">Career Coach</h1>
        </div>

        <div className="w-10"></div> 
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 custom-scrollbar bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-800/20 via-slate-900 to-slate-900">
        
        {messages.length === 0 && isProcessing && (
          <div className="h-full flex flex-col items-center justify-center animate-pulse mt-20">
            <Bot size={64} className="text-blue-500/50 mb-6 animate-bounce" />
            <h2 className="text-2xl font-bold text-white mb-2">Connecting to Coach...</h2>
            <p className="text-slate-400">Preparing your personalized session</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
            
            {msg.sender === 'ai' && (
              <div className="w-10 h-10 rounded-xl bg-slate-800 border border-blue-500/30 flex items-center justify-center mr-3 shadow-lg">
                <Bot className="text-blue-400" size={22} />
              </div>
            )}

            <div className={`max-w-[85%] md:max-w-[70%] p-5 rounded-2xl shadow-xl ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-none font-bold' 
                : 'bg-slate-800 border border-slate-700 text-slate-100 rounded-tl-none'
            }`}>
              {msg.text && <p className={`leading-relaxed text-lg ${msg.audioUrl ? 'mb-4' : ''}`}>{msg.text}</p>}
              
              {msg.audioUrl && (
                  <audio 
                    src={msg.audioUrl} 
                    controls 
                    autoPlay={msg.sender === 'ai'} 
                    className={`h-10 w-full min-w-[240px] rounded-lg ${msg.sender === 'user' ? 'brightness-90 invert' : 'brightness-110'}`}
                  />
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center ml-3 shadow-lg shadow-blue-500/20">
                <User className="text-white" size={22} />
              </div>
            )}
          </div>
        ))}

        {messages.length > 0 && isProcessing && (
          <div className="flex justify-start items-center space-x-3 text-blue-400 bg-slate-800/30 w-fit p-4 rounded-2xl border border-slate-700">
            <Loader2 className="animate-spin" size={20} />
            <span className="text-sm font-bold tracking-wide animate-pulse">Coach is thinking...</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Action Bar */}
      <div className={`bg-slate-800/80 backdrop-blur-xl border-t border-slate-700 p-6 flex justify-center items-center min-h-[120px] transition-opacity ${messages.length === 0 ? 'opacity-50 pointer-events-none' : ''}`}>
        
        {stagedAudioUrl ? (
          <div className="flex items-center gap-4 w-full max-w-lg bg-slate-900 p-3 pr-4 rounded-2xl shadow-2xl border border-blue-500/30 animate-fade-in-up">
            <button 
              onClick={handleCancelAudio}
              className="p-3 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
            >
              <Trash2 size={24} />
            </button>
            
            <audio src={stagedAudioUrl} controls className="flex-1 h-10 brightness-110" />
            
            <button 
              onClick={handleSendAudio}
              className="p-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all shadow-lg shadow-blue-500/20"
            >
              <Send size={22} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em] font-black">
                {isRecording ? "Listening to your question..." : "Tap to Speak to Coach"}
            </p>
            <button 
                onClick={handleRecordToggle}
                disabled={isProcessing}
                className={`relative flex items-center justify-center w-24 h-24 rounded-3xl transition-all duration-500 shadow-2xl ${
                isRecording 
                    ? 'bg-red-500 scale-110 shadow-red-500/40' 
                    : 'bg-blue-600 hover:scale-105 shadow-blue-500/20'
                } ${isProcessing ? 'opacity-20 cursor-not-allowed' : 'cursor-pointer'}`}
            >
                {isRecording ? (
                <Square className="text-white fill-current" size={32} />
                ) : (
                <Mic className="text-white" size={40} />
                )}
                
                {isRecording && (
                <>
                    <span className="absolute w-full h-full rounded-3xl border-4 border-red-500 animate-ping opacity-40"></span>
                    <span className="absolute w-[120%] h-[120%] rounded-3xl border border-red-500/20 animate-pulse"></span>
                </>
                )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}