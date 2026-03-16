import React from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import Layout from '../layout/Layout'; // Assuming you have this from ChooseSkill
import { Trophy, Home, Star, AlertCircle, CheckCircle } from 'lucide-react';

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();

  // Retrieve the data passed from the AIInterview page
  const { skill, summary } = location.state || {};

  // Security check: If someone tries to visit /result directly without an interview, send them back
  if (!summary) {
    return <Navigate to="/chooseskill" replace />;
  }

  // --- SAFE DATA PARSING ---
  // Depending on how your friend wrote the backend, 'summary' might be a string or a JSON object.
  // We will safely extract the pieces we need.
  const score = summary.overall_score || summary.score || "Complete";
  const mainFeedback = typeof summary === 'string' ? summary : summary.feedback || summary.summary || "You have successfully completed the assessment.";
  const strengths = summary.strengths || summary.pros || [];
  const weaknesses = summary.improvements || summary.weaknesses || summary.cons || [];

  return (
    <Layout>
      <div className="min-h-screen bg-slate-900 flex flex-col items-center py-12 px-4 font-sans text-slate-200">
        
        <div className="w-full max-w-3xl animate-fade-in-up">
          
          {/* Header Section */}
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-yellow-500/10 rounded-full border-4 border-yellow-500/30 mb-6 shadow-[0_0_30px_rgba(234,179,8,0.2)]">
              <Trophy className="text-yellow-500" size={48} />
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-2">
              Assessment <span className="text-yellow-500">Complete</span>
            </h1>
            <p className="text-lg text-slate-400 font-bold tracking-wide uppercase">
              {skill} Trade
            </p>
          </div>

          {/* Main Card */}
          <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6 md:p-10 shadow-2xl mb-8">
            
            {/* Score Display (Only shows if backend provided a number) */}
            {score !== "Complete" && (
              <div className="flex flex-col items-center justify-center mb-10 pb-10 border-b border-slate-700">
                <p className="text-sm text-slate-400 uppercase tracking-widest font-black mb-2">Overall Score</p>
                <div className="text-6xl font-black text-white">{score}<span className="text-3xl text-slate-500">/100</span></div>
              </div>
            )}

            {/* General Feedback */}
            <div className="mb-8">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Star className="text-yellow-500" size={24} /> 
                AI Mentor Feedback
              </h2>
              <p className="text-slate-300 leading-relaxed text-lg bg-slate-900/50 p-6 rounded-2xl border border-slate-700/50">
                {mainFeedback}
              </p>
            </div>

            {/* Dynamic Strengths & Weaknesses (Only shows if backend provided arrays) */}
            {(strengths.length > 0 || weaknesses.length > 0) && (
              <div className="grid md:grid-cols-2 gap-6">
                {strengths.length > 0 && (
                  <div className="bg-green-500/10 border border-green-500/20 p-5 rounded-2xl">
                    <h3 className="text-green-500 font-bold flex items-center gap-2 mb-3">
                      <CheckCircle size={20} /> Strengths
                    </h3>
                    <ul className="space-y-2">
                      {strengths.map((item, idx) => (
                        <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                          <span className="text-green-500 mt-1">•</span> {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {weaknesses.length > 0 && (
                  <div className="bg-red-500/10 border border-red-500/20 p-5 rounded-2xl">
                    <h3 className="text-red-500 font-bold flex items-center gap-2 mb-3">
                      <AlertCircle size={20} /> Areas to Improve
                    </h3>
                    <ul className="space-y-2">
                      {weaknesses.map((item, idx) => (
                        <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                          <span className="text-red-500 mt-1">•</span> {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center">
            <button
              onClick={() => navigate('/chooseskill')}
              className="flex items-center gap-3 px-8 py-4 bg-yellow-500 hover:bg-yellow-400 text-slate-900 rounded-2xl font-black text-lg transition-all shadow-[0_10px_30px_rgba(234,179,8,0.2)] hover:-translate-y-1"
            >
              <Home size={24} />
              Return Home
            </button>
          </div>

        </div>
      </div>
    </Layout>
  );
}