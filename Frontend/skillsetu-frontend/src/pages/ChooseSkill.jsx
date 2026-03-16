import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../layout/Layout";
import { Zap, Wrench, Hammer, Car, Flame, ArrowRight, Sparkles, Loader2 } from "lucide-react";
import { startInterviewSession } from "../api/aiService";

export default function ChooseSkill() {
  const navigate = useNavigate();
  // 1. Initialize as null so we can store the whole skill object
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [language, setLanguage] = useState("Hindi"); 
  const [isInitializing, setIsInitializing] = useState(false);

  // 2. Add backend-friendly IDs to map to question_bank.fixed.json
  const skills = [
    { name: "Electrician", id: "electrical", icon: <Zap size={32} /> },
    { name: "Plumber", id: "plumbing", icon: <Wrench size={32} /> },
    { name: "Carpenter", id: "carpentry", icon: <Hammer size={32} /> },
    { name: "Mason", id: "masonry", icon: <Hammer size={32} /> }, // Masonry instead of Mechanic
    { name: "Welder", id: "welding", icon: <Flame size={32} /> },
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
    if (!selectedSkill) return;

    setIsInitializing(true);
    try {
      // 3. Send the strict backend ID (e.g. "plumbing") to FastAPI
      const response = await startInterviewSession(selectedSkill.id, language);
      
      // Navigate to the interview with ALL the generated data
      navigate("/interview", { 
        state: { 
          skill: selectedSkill.name, // Send the pretty name (e.g. "Plumber") to the UI
          lang: language,
          sessionId: response.sessionId,
          initialQuestion: response.initialQuestionText,
          initialAudioUrl: response.initialAudioUrl // The raw audio blob URL
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
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-6 font-sans">
        
        {/* Header */}
        <div className="w-full max-w-3xl text-center mb-10 animate-fade-in-up">
          <div className="inline-block p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-xl mb-4">
            <Sparkles className="text-yellow-500" size={24} />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight mb-4">
            Verify Your <span className="text-yellow-500">Expertise</span>
          </h1>
          <p className="text-slate-400 text-lg">
            Select your trade and preferred language to begin.
          </p>
        </div>

        {/* --- LANGUAGE SELECTION --- */}
        <div className="w-full max-w-2xl mb-8 bg-slate-800 p-2 rounded-2xl border border-slate-700 grid grid-cols-3 md:grid-cols-6 gap-2 z-10 relative">
          {languages.map((l) => (
            <button
              key={l.id}
              onClick={() => setLanguage(l.id)}
              className={`py-3 rounded-xl font-bold transition-all text-sm ${
                language === l.id 
                  ? "bg-yellow-500 text-slate-900 shadow-[0_0_15px_rgba(234,179,8,0.4)]" 
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/50"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>

        {/* Skill Selection Grid */}
        <div className="w-full max-w-4xl grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
          {skills.map((skill) => (
            <button
              key={skill.name}
              onClick={() => setSelectedSkill(skill)} // Store the whole object
              className={`flex flex-col items-center justify-center p-6 rounded-3xl border-2 transition-all duration-300 ${
                selectedSkill?.name === skill.name // Compare the name
                  ? "border-yellow-500 bg-yellow-500/10 text-yellow-500 scale-105 shadow-[0_0_20px_rgba(234,179,8,0.2)]"
                  : "border-slate-800 bg-slate-800/40 text-slate-500 hover:border-slate-600 hover:bg-slate-800"
              }`}
            >
              <div className="mb-3">{skill.icon}</div>
              <span className="font-bold text-sm tracking-wide">{skill.name}</span>
            </button>
          ))}
        </div>

        {/* The Smart Action Button */}
        <div className="w-full max-w-xs">
          <button
            onClick={handleStartAssessment}
            disabled={!selectedSkill || isInitializing}
            className={`w-full flex items-center justify-center gap-3 p-5 rounded-2xl font-black text-xl transition-all duration-300 ${
              isInitializing
                ? "bg-slate-700 text-yellow-500 cursor-wait border border-slate-600"
                : selectedSkill
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
                {selectedSkill ? `Start Assessment` : "Select a Trade"}
                <ArrowRight size={24} />
              </>
            )}
          </button>
        </div>

      </div>
    </Layout>
  );
}