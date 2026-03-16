import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../layout/Layout";
import { Zap, Wrench, Hammer, Car, Flame, ArrowRight, Sparkles } from "lucide-react";

export default function ChooseSkill() {
  const navigate = useNavigate();
  const [selectedSkill, setSelectedSkill] = useState("");

  const skills = [
    { name: "Electrician", icon: <Zap size={32} /> },
    { name: "Plumber", icon: <Wrench size={32} /> },
    { name: "Carpenter", icon: <Hammer size={32} /> },
    { name: "Mechanic", icon: <Car size={32} /> },
    { name: "Welder", icon: <Flame size={32} /> },
  ];

  const startInterview = () => {
    if (selectedSkill) {
      navigate("/interview", { state: { skill: selectedSkill } });
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-6 font-sans">
        
        {/* Header Section */}
        <div className="w-full max-w-3xl text-center mb-12 animate-fade-in-up">
          <div className="inline-block p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-xl mb-4">
            <Sparkles className="text-yellow-500" size={24} />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight mb-4">
            Verify Your <span className="text-yellow-500">Expertise</span>
          </h1>
          <p className="text-slate-400 text-lg">
            Choose your trade to begin the AI voice assessment. <br className="hidden md:block"/> No typing or writing required—just speak your mind.
          </p>
        </div>

        {/* Skill Selection Grid */}
        <div className="w-full max-w-4xl grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-12">
          {skills.map((skill) => (
            <button
              key={skill.name}
              onClick={() => setSelectedSkill(skill.name)}
              className={`flex flex-col items-center justify-center p-8 rounded-3xl border-2 transition-all duration-300 group relative overflow-hidden ${
                selectedSkill === skill.name
                  ? "border-yellow-500 bg-yellow-500/10 text-yellow-500 shadow-[0_0_25px_rgba(234,179,8,0.2)] scale-105"
                  : "border-slate-800 bg-slate-800/40 text-slate-400 hover:border-yellow-500/50 hover:bg-slate-800"
              }`}
            >
              {/* Highlight background effect for selected item */}
              {selectedSkill === skill.name && (
                <div className="absolute top-0 right-0 w-8 h-8 bg-yellow-500 text-slate-900 flex items-center justify-center rounded-bl-xl">
                    <ArrowRight size={14} className="-rotate-45" />
                </div>
              )}

              <div className={`mb-4 transition-colors duration-300 ${
                selectedSkill === skill.name ? "text-yellow-500 scale-110" : "text-slate-500 group-hover:text-yellow-400"
              }`}>
                {skill.icon}
              </div>
              <span className={`font-bold tracking-wide ${
                selectedSkill === skill.name ? "text-white" : "text-slate-400 group-hover:text-slate-200"
              }`}>
                {skill.name}
              </span>
            </button>
          ))}
        </div>

        {/* Action Button */}
        <div className="w-full max-w-sm">
            <button
              onClick={startInterview}
              disabled={!selectedSkill}
              className={`w-full flex items-center justify-center gap-3 p-5 rounded-2xl font-black text-xl tracking-wide transition-all duration-300 ${
                selectedSkill
                  ? "bg-yellow-500 hover:bg-yellow-400 text-slate-900 shadow-[0_10px_30px_rgba(234,179,8,0.3)] hover:-translate-y-1 active:scale-95"
                  : "bg-slate-800 text-slate-600 cursor-not-allowed border border-slate-700"
              }`}
            >
              {selectedSkill ? `Verify as ${selectedSkill}` : "Select a Trade"}
              <ArrowRight size={24} />
            </button>
            <p className="text-center text-slate-500 text-sm mt-6 uppercase tracking-widest font-bold opacity-60">
                AI System Ready • Native Language Support
            </p>
        </div>

      </div>
    </Layout>
  );
}