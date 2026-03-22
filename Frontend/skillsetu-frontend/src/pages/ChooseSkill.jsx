import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../layout/Layout";
import { Zap, Wrench, Hammer, Flame, ArrowRight, Sparkles, Loader2, MapPin } from "lucide-react";
import { startInterviewSession } from "../api/aiService";

// 1. ADDED LIST OF STATES
const INDIAN_STATES = [
  "Andhra Pradesh", "Bihar", "Delhi", "Gujarat", "Haryana", 
  "Karnataka", "Kerala", "Maharashtra", "Punjab", "Rajasthan", 
  "Tamil Nadu", "Telangana", "Uttar Pradesh", "West Bengal"
];

export default function ChooseSkill() {
  const navigate = useNavigate();
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [language, setLanguage] = useState("Hindi"); 
  const [userState, setUserState] = useState(""); 
  const [isInitializing, setIsInitializing] = useState(false);

  const skills = [
    { name: "Electrician", id: "electrical", icon: <Zap size={28} /> },
    { name: "Plumber", id: "plumbing", icon: <Wrench size={28} /> },
    { name: "Carpenter", id: "carpentry", icon: <Hammer size={28} /> },
    { name: "Mason", id: "masonry", icon: <Hammer size={28} /> }, 
    { name: "Welder", id: "welding", icon: <Flame size={28} /> },
  ];

  const languages = [
    { id: "English", label: "English" },
    { id: "Hindi", label: "हिन्दी" },
    { id: "Hinglish", label: "Hinglish" },
    { id: "Tamil", label: "தமிழ்" },
    { id: "Telugu", label: "తెలుగు" },
    { id: "Bengali", label: "বাংলা" },
  ];

  const handleStartAssessment = async () => {
    if (!selectedSkill || !userState) return; 

    setIsInitializing(true);
    try {
      const response = await startInterviewSession(selectedSkill.id, language);
      
      navigate("/interview", { 
        state: { 
          skill: selectedSkill.name,
          lang: language,
          userState: userState, 
          sessionId: response.sessionId,
          initialQuestion: response.initialQuestionText,
          initialAudioUrl: response.initialAudioUrl 
        } 
      });
    } catch (error) {
      alert("Failed to connect to the AI Mentor. Please check your backend.");
    } finally {
      setIsInitializing(false);
    }
  };

  return (
    <Layout>
      <div className="w-[100vw] relative left-[50%] right-[50%] -ml-[50vw] -mr-[50vw] mt-[-4rem] mb-[-4rem] min-h-[calc(100vh-80px)] bg-slate-900 flex flex-col items-center justify-center py-6 px-6 font-sans overflow-x-hidden">
        
        <div className="w-full max-w-3xl text-center mb-6 animate-fade-in-up mt-6">
          <div className="inline-block p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-xl mb-3">
            <Sparkles className="text-yellow-500" size={24} />
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight mb-3">
            Verify Your <span className="text-yellow-500">Expertise</span>
          </h1>
          <p className="text-slate-400 text-base md:text-lg">
            Select your trade, language, and location to begin.
          </p>
        </div>

        {/* Language Selector */}
        <div className="w-full max-w-2xl mb-6 bg-slate-800 p-1.5 rounded-2xl border border-slate-700 grid grid-cols-3 md:grid-cols-6 gap-2 z-10 relative">
          {languages.map((l) => (
            <button
              key={l.id}
              onClick={() => setLanguage(l.id)}
              className={`py-2 rounded-xl font-bold transition-all text-sm ${
                language === l.id 
                  ? "bg-yellow-500 text-slate-900 shadow-[0_0_15px_rgba(234,179,8,0.4)]" 
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/50"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>

        {/* Skill Selector */}
        <div className="w-full max-w-4xl grid grid-cols-2 md:grid-cols-5 gap-3 md:gap-4 mb-8">
          {skills.map((skill) => (
            <button
              key={skill.name}
              onClick={() => setSelectedSkill(skill)}
              className={`flex flex-col items-center justify-center p-4 rounded-3xl border-2 transition-all duration-300 ${
                selectedSkill?.name === skill.name
                  ? "border-yellow-500 bg-yellow-500/10 text-yellow-500 scale-105 shadow-[0_0_20px_rgba(234,179,8,0.2)]"
                  : "border-slate-800 bg-slate-800/40 text-slate-500 hover:border-slate-600 hover:bg-slate-800"
              }`}
            >
              <div className="mb-2">{skill.icon}</div>
              <span className="font-bold text-sm tracking-wide">{skill.name}</span>
            </button>
          ))}
        </div>

        {/* 4. ADDED LOCATION DROPDOWN */}
        <div className="w-full max-w-xs mb-6 relative">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <MapPin size={20} className="text-slate-400" />
          </div>
          <select 
            value={userState}
            onChange={(e) => setUserState(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 text-slate-200 pl-12 pr-4 py-4 rounded-2xl appearance-none focus:outline-none focus:border-yellow-500 focus:ring-1 focus:ring-yellow-500 transition-all font-semibold"
          >
            <option value="" disabled>Select your State...</option>
            {INDIAN_STATES.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        <div className="w-full max-w-xs">
          <button
            onClick={handleStartAssessment}
            disabled={!selectedSkill || !userState || isInitializing}
            className={`w-full flex items-center justify-center gap-3 p-4 rounded-2xl font-black text-lg transition-all duration-300 ${
              isInitializing
                ? "bg-slate-700 text-yellow-500 cursor-wait border border-slate-600"
                : (selectedSkill && userState)
                  ? "bg-yellow-500 hover:bg-yellow-400 text-slate-900 shadow-[0_10px_30px_rgba(234,179,8,0.3)] hover:-translate-y-1 active:scale-95"
                  : "bg-slate-800 text-slate-600 cursor-not-allowed border border-slate-700"
            }`}
          >
            {isInitializing ? (
              <>
                <Loader2 size={24} className="animate-spin" />
                <span>Waking AI...</span>
              </>
            ) : (
              <>
                {(selectedSkill && userState) ? `Start Assessment` : "Complete Selections"}
                <ArrowRight size={24} />
              </>
            )}
          </button>
        </div>

      </div>
    </Layout>
  );
}