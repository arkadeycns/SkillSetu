import React from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import Layout from "../layout/Layout";
import { ShieldCheck, Mic, FileText, LayoutDashboard, BarChart3, Users } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();
  const { isSignedIn, isLoaded } = useUser();
  const role = localStorage.getItem("role");

  // Routing Handlers
  const handleProfessionalClick = () => {
    if (!isSignedIn) navigate("/signup");
    else navigate("/resume-parser");
  };

  const handleBlueCollarClick = () => {
    if (!isSignedIn) navigate("/signup");
    else navigate("/chooseskill");
  };

  if (!isLoaded) return null;

  return (
    <Layout>
      <div className="w-[100vw] relative left-[50%] right-[50%] -ml-[50vw] -mr-[50vw] flex flex-col font-sans overflow-x-hidden mt-[-4rem] mb-[-4rem]">
        
        {/* --- CONDITION 1: GOVERNMENT VIEW (Command Center) --- */}
        {isSignedIn && role === "government" ? (
          <div className="w-full min-h-[85vh] bg-slate-900 flex flex-col justify-center items-center p-8 text-center border-b border-slate-800">
            <div className="max-w-3xl space-y-8 animate-fade-in-up">
              <div className="inline-block px-4 py-1.5 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-yellow-500 text-sm font-bold tracking-widest uppercase">
                Official Administrative Access
              </div>
              <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight leading-tight">
                National Skill <br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500">
                  Command Center
                </span>
              </h1>
              <p className="text-slate-400 text-xl max-w-2xl mx-auto leading-relaxed">
                Welcome back, Officer. You have full access to the regional competency heatmaps, workforce analytics, and verified certification logs.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                <button 
                  onClick={() => navigate('/dashboard')}
                  className="px-8 py-4 bg-yellow-500 hover:bg-yellow-400 text-slate-900 font-bold rounded-xl shadow-[0_0_20px_rgba(234,179,8,0.3)] transition-all flex items-center gap-3"
                >
                  <LayoutDashboard size={20} />
                  Open Analytics Dashboard
                </button>
                <button 
                  onClick={() => navigate('/regional-reports')}
                  className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl border border-slate-700 transition-all flex items-center gap-3"
                >
                  <BarChart3 size={20} />
                  View Regional Reports
                </button>
              </div>

              {/* Stats Preview for Govt */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6 pt-12">
                <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700">
                  <div className="text-yellow-500 text-2xl font-bold">12.4k</div>
                  <div className="text-slate-500 text-xs uppercase font-bold tracking-tighter">Verified Workers</div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700">
                  <div className="text-yellow-500 text-2xl font-bold">84%</div>
                  <div className="text-slate-500 text-xs uppercase font-bold tracking-tighter">Placement Rate</div>
                </div>
                <div className="hidden md:block p-4 rounded-2xl bg-slate-800/50 border border-slate-700">
                  <div className="text-yellow-500 text-2xl font-bold">Uttar Pradesh</div>
                  <div className="text-slate-500 text-xs uppercase font-bold tracking-tighter">Top Region</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          
          /* --- CONDITION 2: CANDIDATE VIEW (Standard 50/50 Split) --- */
          <div className="flex flex-col md:flex-row w-full min-h-[85vh]">
            {/* PATH 1: PROFESSIONALS */}
            <div className="w-full md:w-1/2 flex flex-col justify-center items-center p-8 lg:p-16 bg-slate-900 text-white transition-all duration-300 hover:bg-slate-800 border-r border-slate-800">
              <div className="max-w-md text-center md:text-left space-y-6">
                <div className="inline-block p-3 bg-slate-800 rounded-lg border border-yellow-500/30 mb-2">
                  <FileText className="w-8 h-8 text-yellow-500" />
                </div>
                <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500">
                  For Professionals
                </h2>
                <p className="text-slate-300 text-lg leading-relaxed">
                  Upload your resume for deep AI parsing. Align your corporate and technical skills with industry standards.
                </p>
                <button 
                  onClick={handleProfessionalClick}
                  className="w-full sm:w-auto px-8 py-4 bg-yellow-500 hover:bg-yellow-400 text-slate-900 font-bold rounded-md shadow-[0_0_15px_rgba(234,179,8,0.3)] transition-all flex items-center justify-center gap-2"
                >
                  {isSignedIn ? "Upload Resume" : "Get Started"}
                  <span>→</span>
                </button>
              </div>
            </div>

            {/* PATH 2: BLUE COLLAR */}
            <div className="w-full md:w-1/2 flex flex-col justify-center items-center p-8 lg:p-16 bg-yellow-50 text-slate-800 transition-all duration-300 hover:bg-yellow-100">
              <div className="max-w-md text-center md:text-left space-y-6">
                <div className="inline-block p-3 bg-white rounded-lg shadow-sm border border-yellow-200 mb-2">
                  <Mic className="w-8 h-8 text-yellow-600" />
                </div>
                <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-slate-900">
                  For Trades & Crafts
                </h2>
                <p className="text-slate-600 text-lg leading-relaxed">
                  Get your skills certified instantly. Talk directly to our AI mentor in your native language.
                </p>
                <button 
                  onClick={handleBlueCollarClick}
                  className="w-full sm:w-auto px-8 py-4 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-md shadow-lg transition-all flex items-center justify-center gap-2"
                >
                  {isSignedIn ? "Start Voice Interview" : "Get Started"}
                  <span>→</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* --- FEATURES SECTION --- */}
        <section className="px-6 py-24 bg-slate-900 border-t border-slate-800">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-extrabold text-white">The Ultimate Skill Verification Platform</h2>
              <p className="text-slate-400 mt-4 max-w-2xl mx-auto">Bridging the gap between manual labor, technical skillsets, and administrative oversight.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-slate-800/50 p-8 rounded-3xl border border-slate-700">
                <div className="w-14 h-14 bg-slate-800 border border-yellow-500/30 rounded-2xl flex items-center justify-center mb-6">
                  <FileText className="text-yellow-500" size={28} />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Resume Intelligence</h3>
                <p className="text-slate-400">NLP-driven extraction for technical and white-collar roles.</p>
              </div>
              <div className="bg-slate-800/50 p-8 rounded-3xl border border-slate-700">
                <div className="w-14 h-14 bg-slate-800 border border-yellow-500/30 rounded-2xl flex items-center justify-center mb-6">
                  <Mic className="text-yellow-500" size={28} />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Vernacular Voice AI</h3>
                <p className="text-slate-400">Verbal competency testing in Hindi, Hinglish, and English.</p>
              </div>
              <div className="bg-slate-800/50 p-8 rounded-3xl border border-slate-700">
                <div className="w-14 h-14 bg-slate-800 border border-yellow-500/30 rounded-2xl flex items-center justify-center mb-6">
                  <ShieldCheck className="text-yellow-500" size={28} />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Verified Skill Wallet</h3>
                <p className="text-slate-400">Secured, dynamic trust scores for instant workforce deployment.</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}