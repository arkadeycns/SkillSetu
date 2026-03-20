import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../layout/Layout";
import { Zap, Wrench, Hammer, Flame, ArrowRight, Bot, Loader2 } from "lucide-react";

export default function ChooseCoach() {
  const navigate = useNavigate();
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [language, setLanguage] = useState("Hindi"); 
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

  const handleStartCoaching = () => {
    if (!selectedSkill) return;

    setIsInitializing(true);
    
    setTimeout(() => {
      navigate("/guidance-chat", { 
        state: { 
          skill: selectedSkill.name, 
          lang: language,
          sessionId: `coach_${Date.now()}` 
        } 
      });
    }, 1200);
  };

  return (
    <Layout>
      <div className="w-[100vw] relative left-[50%] right-[50%] -ml-[50vw] -mr-[50vw] mt-[-4rem] mb-[-4rem] min-h-screen bg-slate-900 flex flex-col items-center justify-center py-12 px-6 font-sans overflow-x-hidden">
        
        <div className="w-full max-w-3xl text-center mb-6 animate-fade-in-up mt-8">
          <div className="inline-block p-2.5 bg-blue-600/10 border border-blue-500/20 rounded-2xl mb-3">
            <Bot className="text-blue-400" size={28} />
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight mb-3">
            Meet Your <span className="text-blue-500">AI Career Coach</span>
          </h1>
          <p className="text-slate-400 text-base md:text-lg">
            Select your trade and preferred language to start building your upskilling roadmap.
          </p>
        </div>

        <div className="w-full max-w-2xl mb-6 bg-slate-800 p-1.5 rounded-2xl border border-slate-700 grid grid-cols-3 md:grid-cols-6 gap-2 z-10 relative">
          {languages.map((l) => (
            <button
              key={l.id}
              onClick={() => setLanguage(l.id)}
              className={`py-2 rounded-xl font-bold transition-all text-sm ${
                language === l.id 
                  ? "bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.4)]" 
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/50"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>

        <div className="w-full max-w-4xl grid grid-cols-2 md:grid-cols-5 gap-3 md:gap-4 mb-8">
          {skills.map((skill) => (
            <button
              key={skill.name}
              onClick={() => setSelectedSkill(skill)} 
              className={`flex flex-col items-center justify-center p-4 rounded-3xl border-2 transition-all duration-300 ${
                selectedSkill?.name === skill.name 
                  ? "border-blue-500 bg-blue-600/10 text-blue-400 scale-105 shadow-[0_0_20px_rgba(37,99,235,0.2)]"
                  : "border-slate-800 bg-slate-800/40 text-slate-500 hover:border-slate-600 hover:bg-slate-800"
              }`}
            >
              <div className="mb-2">{skill.icon}</div>
              <span className="font-bold text-sm tracking-wide">{skill.name}</span>
            </button>
          ))}
        </div>

        <div className="w-full max-w-xs">
          <button
            onClick={handleStartCoaching}
            disabled={!selectedSkill || isInitializing}
            className={`w-full flex items-center justify-center gap-3 p-4 rounded-2xl font-black text-lg transition-all duration-300 ${
              isInitializing
                ? "bg-slate-700 text-blue-400 cursor-wait border border-slate-600"
                : selectedSkill
                  ? "bg-blue-600 hover:bg-blue-500 text-white shadow-[0_10px_30px_rgba(37,99,235,0.3)] hover:-translate-y-1 active:scale-95"
                  : "bg-slate-800 text-slate-600 cursor-not-allowed border border-slate-700"
            }`}
          >
            {isInitializing ? (
              <>
                <Loader2 size={24} className="animate-spin" />
                <span>Waking Coach...</span>
              </>
            ) : (
              <>
                {selectedSkill ? `Start Mentorship` : "Select a Trade"}
                <ArrowRight size={24} />
              </>
            )}
          </button>
        </div>

      </div>
    </Layout>
  );
}