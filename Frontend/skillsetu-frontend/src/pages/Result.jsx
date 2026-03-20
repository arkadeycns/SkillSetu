import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import Layout from '../layout/Layout'; 
import { Trophy, Home, Star, AlertCircle, CheckCircle, BookOpen, ArrowRight, Loader2 } from 'lucide-react';
import { getTrainingRecommendations } from '../api/aiService';

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();

  // Retrieve the data passed from the AIInterview page
  const { skill, summary, sessionId, lang } = location.state || {};
  
  // State for the training roadmap
  const [trainingPlan, setTrainingPlan] = useState(null);
  const [isLoadingPlan, setIsLoadingPlan] = useState(true);

  // Fetch the training plan when the page loads
  useEffect(() => {
    async function fetchPlan() {
      if (sessionId) {
        const data = await getTrainingRecommendations(sessionId);
        if (data && data.recommendations) {
          setTrainingPlan(data.recommendations);
        }
      }
      setIsLoadingPlan(false);
    }
    fetchPlan();
  }, [sessionId]);

  // If someone tries to visit /result directly without an interview, send them back
  if (!summary) {
    return <Navigate to="/chooseskill" replace />;
  }

  // Safe data parsing to handle different summary shapes
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
              {skill}
            </p>
          </div>

          {/* Main Card */}
          <div className="bg-slate-800 border border-slate-700 rounded-3xl p-6 md:p-10 shadow-2xl mb-8">
            
            {/* Score Display */}
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

            {/* Dynamic Strengths & Weaknesses */}
            {(strengths.length > 0 || weaknesses.length > 0) && (
              <div className="grid md:grid-cols-2 gap-6 mb-10">
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
                      <AlertCircle size={20} /> Skill Gaps Detected
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

            {/* AI Training Roadmap */}
            <div className="bg-blue-500/10 border border-blue-500/20 p-6 rounded-2xl">
              <h3 className="text-blue-400 text-xl font-bold flex items-center gap-2 mb-2">
                <BookOpen size={24} /> Upskilling Roadmap
              </h3>
              
              {isLoadingPlan ? (
                <div className="flex items-center gap-3 text-blue-400 p-4">
                  <Loader2 className="animate-spin" size={20} />
                  <span>AI is generating your custom curriculum...</span>
                </div>
              ) : trainingPlan?.modules && trainingPlan.modules.length > 0 ? (
                <div className="mt-4 space-y-4">
                  <p className="text-slate-400 text-sm mb-4">Focus on these topics to improve your technical profile:</p>
                  
                  {/* Updated mapping to match the new JSON structure */}
                  {trainingPlan.modules.map((mod, idx) => (
                    <div key={idx} className="bg-slate-900/50 p-5 rounded-xl border border-slate-700">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="text-white font-bold text-lg">{mod.module}</h4>
                        <span className="text-xs font-black uppercase tracking-wider px-2 py-1 rounded-md bg-blue-500/20 text-blue-400">
                          {mod.duration || "Self-Paced"}
                        </span>
                      </div>
                      
                      <p className="text-slate-400 text-sm italic mb-3">
                        Practice: {mod.practice_task}
                      </p>

                      <div className="flex flex-wrap gap-2 mt-2">
                        {mod.skills_to_learn && mod.skills_to_learn.map((skillItem, sIdx) => (
                          <span key={sIdx} className="bg-blue-600/20 border border-blue-500/30 text-blue-300 text-xs px-2 py-1 rounded-md">
                            {skillItem}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-slate-900/50 p-5 rounded-xl border border-slate-700 mt-4">
                   <p className="text-slate-300 leading-relaxed text-sm">
                     {typeof trainingPlan === 'object' && trainingPlan.plan 
                        ? trainingPlan.plan 
                        : "No specific training modules recommended at this time."}
                   </p>
                </div>
              )}
            </div>

          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center justify-center gap-3 px-8 py-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-2xl font-bold transition-all shadow-lg"
            >
              <Home size={20} />
              Return Home
            </button>
            
            {/* Jump to Chat with context passed */}
            <button
              onClick={() => navigate('/guidance-chat', { 
                state: { 
                  sessionId: sessionId,
                  skill: skill,
                  lang: lang || "English"
                } 
              })}
              className="flex items-center justify-center gap-3 px-8 py-4 bg-yellow-500 hover:bg-yellow-400 text-slate-900 rounded-2xl font-black transition-all shadow-[0_10px_30px_rgba(234,179,8,0.2)] hover:-translate-y-1"
            >
              Start AI Guidance Chat
              <ArrowRight size={20} />
            </button>
          </div>

        </div>
      </div>
    </Layout>
  );
}