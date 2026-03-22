import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import { Mic, Square, Loader2, User, Bot, Trash2, Send, ChevronLeft, Flag } from 'lucide-react'; 
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';
import { sendAudioToAI, getInterviewSummary } from '../api/aiService';
import { useAuth, useUser } from "@clerk/clerk-react"; 

export default function AIInterview() {
  const navigate = useNavigate();
  const location = useLocation();
  const { userId } = useAuth(); 
  const { user } = useUser(); 
  
  const selectedSkill = location.state?.skill || "General Trade";
  const selectedLang = location.state?.lang || "Hindi";
  const userLocation = location.state?.userState || "Maharashtra";
  const sessionId = location.state?.sessionId || "dev_session";
  const initialQuestion = location.state?.initialQuestion || "Welcome to the assessment.";
  const initialAudioUrl = location.state?.initialAudioUrl || null; 
  
  const { isRecording, startRecording, stopRecording } = useVoiceRecorder();
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [stagedAudioBlob, setStagedAudioBlob] = useState(null);
  const [stagedAudioUrl, setStagedAudioUrl] = useState(null);
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    setMessages([
      { sender: 'ai', text: initialQuestion, audioUrl: initialAudioUrl }
    ]);
  }, [initialQuestion, initialAudioUrl]);

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
    const aiResult = await sendAudioToAI(blobToSend, sessionId);
    setIsProcessing(false);

    if (aiResult && aiResult.audioUrl) {
      setMessages(prev => [...prev, { sender: 'ai', text: aiResult.text, audioUrl: aiResult.audioUrl }]);
    } else if (aiResult && aiResult.error) {
      alert(aiResult.error);
    } else {
      alert("AI is having trouble connecting. Check your internet.");
    }
  };

  // --- HANDLE ENDING THE INTERVIEW & SAVING TO MONGODB --
  const handleEndInterview = async () => {
    if (isProcessing) return; 

    const confirmEnd = window.confirm("Are you sure you want to end the assessment? Your final score will be calculated.");
    if (!confirmEnd) return;

    setIsFinishing(true);

    try {
      const summaryData = await getInterviewSummary(sessionId);
      const finalScore = summaryData.score || summaryData.overall_score || 0;
      const isPass = finalScore >= 70;

      
      if (userId) {
        try {
          await fetch("http://localhost:8000/api/user/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              clerk_id: userId,
              user_name: user?.fullName || "Worker",
              skill_name: selectedSkill,
              score: finalScore,
              result: isPass ? "PASS" : "FAIL",
              state: userLocation, 
              badges: isPass ? ["AI Verified", "Safety Cleared"] : ["Beginner"]
            })
          });
        } catch (syncError) {
           console.error("Failed to sync interview to DB:", syncError);
        }
      }
      
      if (summaryData) {
        navigate("/result", { 
          state: { 
            skill: selectedSkill,
            summary: summaryData,
            sessionId: sessionId
          } 
        });
      } else {
        alert("Failed to generate summary. Please try again.");
        setIsFinishing(false);
      }
    } catch (error) {
      console.error("Error fetching summary:", error);
      alert("Error generating result.");
      setIsFinishing(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-200 font-sans">
      
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-md border-b border-slate-700 p-4 flex items-center justify-between relative">
        <button 
          onClick={() => navigate('/chooseskill')}
          className="p-2 hover:bg-slate-700 rounded-full transition-colors text-slate-400"
        >
          <ChevronLeft size={24} />
        </button>
        
        <div className="text-center absolute left-1/2 -translate-x-1/2">
          <h1 className="text-lg font-bold text-white tracking-wide uppercase">AI Mentor: {selectedSkill}</h1>
          <div className="flex items-center justify-center gap-1.5">
            <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></span>
            <p className="text-[10px] text-yellow-500 font-black uppercase tracking-widest">
              Lang: {selectedLang} | Session: {sessionId.substring(0,6)}
            </p>
          </div>
        </div>

        {/* End Assessment Button */}
        <button 
          onClick={handleEndInterview}
          disabled={isFinishing || isProcessing}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-bold transition-all ${
            isFinishing || isProcessing
              ? "bg-slate-700 text-slate-500 cursor-not-allowed"
              : "bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500 hover:text-white"
          }`}
        >
          {isFinishing ? <Loader2 size={16} className="animate-spin" /> : <Flag size={16} />}
          <span className="hidden sm:inline">{isFinishing ? "Scoring..." : "End"}</span>
        </button>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 custom-scrollbar bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-800/20 via-slate-900 to-slate-900">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
            
            {msg.sender === 'ai' && (
              <div className="w-10 h-10 rounded-xl bg-slate-800 border border-yellow-500/30 flex items-center justify-center mr-3 shadow-lg">
                <Bot className="text-yellow-500" size={22} />
              </div>
            )}

            <div className={`max-w-[85%] md:max-w-[70%] p-5 rounded-2xl shadow-xl ${
              msg.sender === 'user' 
                ? 'bg-yellow-500 text-slate-900 rounded-tr-none font-bold' 
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
              <div className="w-10 h-10 rounded-xl bg-yellow-500 flex items-center justify-center ml-3 shadow-lg shadow-yellow-500/20">
                <User className="text-slate-900" size={22} />
              </div>
            )}
          </div>
        ))}

        {isProcessing && (
          <div className="flex justify-start items-center space-x-3 text-yellow-500/80 bg-slate-800/30 w-fit p-4 rounded-2xl border border-slate-700">
            <Loader2 className="animate-spin" size={20} />
            <span className="text-sm font-bold tracking-wide animate-pulse">AI is analyzing your expertise...</span>
          </div>
        )}

        {isFinishing && (
          <div className="flex justify-center items-center mt-10 animate-fade-in-up">
            <div className="bg-slate-800 border border-yellow-500/50 p-6 rounded-2xl shadow-2xl flex flex-col items-center gap-4">
               <Loader2 className="animate-spin text-yellow-500" size={40} />
               <p className="text-lg font-bold text-white">Generating Final Report...</p>
               <p className="text-sm text-slate-400">Please wait while AI grades your answers.</p>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Action Bar */}
      <div className={`bg-slate-800/80 backdrop-blur-xl border-t border-slate-700 p-6 flex justify-center items-center min-h-[120px] transition-opacity ${isFinishing ? 'opacity-50 pointer-events-none' : ''}`}>
        
        {stagedAudioUrl ? (
          <div className="flex items-center gap-4 w-full max-w-lg bg-slate-900 p-3 pr-4 rounded-2xl shadow-2xl border border-yellow-500/30 animate-fade-in-up">
            <button 
              onClick={handleCancelAudio}
              className="p-3 text-slate-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
            >
              <Trash2 size={24} />
            </button>
            
            <audio src={stagedAudioUrl} controls className="flex-1 h-10 brightness-110" />
            
            <button 
              onClick={handleSendAudio}
              className="p-4 bg-yellow-500 hover:bg-yellow-400 text-slate-900 rounded-xl transition-all shadow-lg shadow-yellow-500/20"
            >
              <Send size={22} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em] font-black">
                {isRecording ? "Listening to your response..." : "Tap to Speak"}
            </p>
            <button 
                onClick={handleRecordToggle}
                disabled={isProcessing}
                className={`relative flex items-center justify-center w-24 h-24 rounded-3xl transition-all duration-500 shadow-2xl ${
                isRecording 
                    ? 'bg-red-500 scale-110 shadow-red-500/40' 
                    : 'bg-yellow-500 hover:scale-105 shadow-yellow-500/20'
                } ${isProcessing ? 'opacity-20 cursor-not-allowed' : 'cursor-pointer'}`}
            >
                {isRecording ? (
                <Square className="text-white fill-current" size={32} />
                ) : (
                <Mic className="text-slate-900" size={40} />
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