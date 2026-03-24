import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { parseResume, getTrainingRecommendations } from "../api/aiService";
import { BookOpen, Bot, Loader2, MapPin } from "lucide-react";
import { useAuth, useUser } from "@clerk/clerk-react"; 
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, '');
const INDIAN_STATES = [
  "Andhra Pradesh", "Bihar", "Delhi", "Gujarat", "Haryana", 
  "Karnataka", "Kerala", "Maharashtra", "Punjab", "Rajasthan", 
  "Tamil Nadu", "Telangana", "Uttar Pradesh", "West Bengal"
];

export const ResumeParser = () => {
  const navigate = useNavigate();
  const { userId } = useAuth(); 
  const { user } = useUser();   
  
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [parseStep, setParseStep] = useState("");
  const [parsedResult, setParsedResult] = useState(null);
  const [userState, setUserState] = useState(""); 
  
  const [trainingPlan, setTrainingPlan] = useState(null);
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [sessionId, setSessionId] = useState("");

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === "application/pdf" || droppedFile.name.endsWith(".docx") || droppedFile.name.endsWith(".txt"))) {
      setFile(droppedFile);
    } else {
      alert("Please upload a valid PDF, DOCX, or TXT file.");
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) setFile(selectedFile);
  };

  const handleParse = async () => {
    if (!file || !userState) return; 
    
    setIsParsing(true);
    setParseStep("Extracting and analyzing document with AI...");
    
    const currentSessionId = `prof_${Date.now()}`;
    setSessionId(currentSessionId);

    try {
      const result = await parseResume(file);
      const score = result.blue_collar_report?.suitability_score || 0;
      const role = result.role || "Professional";
      
      setParsedResult({
        name: result.name || "Candidate Profile",
        role: role,
        confidence: result.confidence || "N/A",
        skills: result.skills || [],
        experience: result.experience_level || "Experience Level Unknown",
        summary: result.blue_collar_report?.fitment_summary || "Profile analyzed successfully.",
        score: score
      });

    
      if (userId) {
        try {
          await fetch(`${API_BASE_URL}/api/user/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              clerk_id: userId,
              user_name: user?.fullName || result.name || "Resume Candidate",
              skill_name: role,
              score: score,
              result: score >= 50 ? "PASS" : "FAIL",
              state: userState, 
              badges: ["Resume Parsed", "AI Verified"]
            })
          });
        } catch (syncError) {
          console.error("Failed to sync resume to DB:", syncError);
        }
      }

      setParseStep("Generating custom upskilling roadmap...");
      setIsLoadingPlan(true);
      
      const planData = await getTrainingRecommendations(currentSessionId);
      if (planData) {
        setTrainingPlan(planData.recommendations || planData);
      }

    } catch (error) {
      console.error("Resume parsing failed:", error);
      alert(error.message || "Failed to parse resume. Please check your backend connection.");
      setFile(null);
    } finally {
      setIsParsing(false);
      setIsLoadingPlan(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 font-sans p-6 md:p-12 flex flex-col items-center">
      
      {/* Navigation & Header */}
      <div className="w-full max-w-4xl flex justify-between items-center mb-12 animate-fade-in-up">
        <button 
          onClick={() => navigate('/')}
          className="text-slate-400 hover:text-yellow-500 transition-colors flex items-center gap-2 text-sm font-semibold"
        >
          <span>←</span> Back to Home
        </button>
        <div className="px-3 py-1 bg-slate-800 border border-yellow-500/30 rounded-full text-xs text-yellow-500 tracking-widest uppercase shadow-[0_0_10px_rgba(234,179,8,0.1)]">
          Intelligence Portal
        </div>
      </div>

      <div className="w-full max-w-3xl text-center space-y-4 mb-10 animate-fade-in-up">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500">
          AI Resume Intelligence
        </h1>
        <p className="text-slate-400 text-lg">
          Upload your resume. Our AI engine will extract your core competencies and benchmark them against industry standards.
        </p>
      </div>

      {/* Main Interface */}
      <div className="w-full max-w-3xl bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 shadow-2xl animate-fade-in-up">
        
        {/* Upload Zone */}
        {!isParsing && !parsedResult && (
          <div 
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center text-center transition-all duration-300 ${
              isDragging 
                ? "border-yellow-500 bg-yellow-500/10" 
                : "border-slate-600 hover:border-yellow-500/50 hover:bg-slate-800"
            }`}
          >
            <input 
              type="file" 
              accept=".pdf,.docx,.txt" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleFileSelect}
            />
            <svg className={`w-12 h-12 mb-4 transition-colors ${file ? 'text-yellow-500' : 'text-slate-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            
            {file ? (
              <div className="space-y-2">
                <p className="text-xl font-semibold text-white">{file.name}</p>
                <p className="text-sm text-slate-400">Ready for processing</p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-xl font-semibold text-white">Drag & drop your resume</p>
                <p className="text-sm text-slate-400">or click to browse (PDF, DOCX, TXT)</p>
              </div>
            )}
          </div>
        )}

        {/* Parsing Animation */}
        {isParsing && (
          <div className="py-16 flex flex-col items-center justify-center space-y-6">
            <div className="relative w-20 h-20">
              <div className="absolute inset-0 rounded-full border-t-2 border-yellow-500 animate-spin"></div>
              <div className="absolute inset-2 rounded-full border-r-2 border-yellow-200 animate-spin delay-150"></div>
            </div>
            <div className="text-center space-y-2">
              <h3 className="text-xl font-bold text-white">AI Engine Active</h3>
              <p className="text-yellow-400 animate-pulse">{parseStep}</p>
            </div>
          </div>
        )}

        {/* Parsed Results & Roadmap */}
        {parsedResult && !isParsing && (
          <div className="space-y-8 animate-fade-in-up">
            
            {/* Top Stats */}
            <div className="flex items-center justify-between border-b border-slate-700 pb-4">
              <div>
                <h3 className="text-2xl font-bold text-white">{parsedResult.role}</h3>
                <p className="text-slate-400 font-medium">{parsedResult.name} • {parsedResult.experience}</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-slate-400">Match Confidence</div>
                <div className="text-2xl font-bold text-yellow-500">{parsedResult.confidence}</div>
              </div>
            </div>
            
            {/* Fitment Summary */}
            <div className="bg-slate-900/50 p-5 rounded-xl border border-slate-700">
               <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">AI Fitment Summary</h4>
               <p className="text-slate-300 text-sm leading-relaxed">{parsedResult.summary}</p>
            </div>

            {/* Extracted Skills */}
            <div>
              <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Extracted Skills</h4>
              <div className="flex flex-wrap gap-2">
                {parsedResult.skills && parsedResult.skills.length > 0 ? (
                  parsedResult.skills.map((skill, index) => (
                    <span key={index} className="px-3 py-1 bg-slate-700 border border-slate-600 rounded-md text-sm text-yellow-50">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500 italic">No skills explicitly identified.</span>
                )}
              </div>
            </div>

            {/* Professional Training Roadmap */}
            <div className="bg-blue-600/10 border border-blue-500/20 p-6 rounded-2xl mt-8">
              <h3 className="text-blue-400 text-xl font-bold flex items-center gap-2 mb-2">
                <BookOpen size={24} /> Professional Upskilling Roadmap
              </h3>
              
              {isLoadingPlan ? (
                <div className="flex items-center gap-3 text-blue-400 p-4">
                  <Loader2 className="animate-spin" size={20} />
                  <span>Generating your custom corporate curriculum...</span>
                </div>
              ) : trainingPlan?.modules && trainingPlan.modules.length > 0 ? (
                <div className="mt-4 space-y-4">
                  <p className="text-slate-400 text-sm mb-4">Based on your profile, focus on these modules:</p>
                  
                  {trainingPlan.modules.map((mod, idx) => (
                    <div key={idx} className="bg-slate-900/60 p-5 rounded-xl border border-slate-700">
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
                        {mod.skills_to_learn && mod.skills_to_learn.map((skill, sIdx) => (
                          <span key={sIdx} className="bg-blue-600/20 border border-blue-500/30 text-blue-300 text-xs px-2 py-1 rounded-md">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-slate-900/50 p-5 rounded-xl border border-slate-700 mt-4">
                   <p className="text-slate-300 leading-relaxed text-sm">
                     {trainingPlan?.plan 
                        ? trainingPlan.plan 
                        : "Your profile is highly optimized. No critical skill gaps detected right now."}
                   </p>
                </div>
              )}
            </div>

          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-8 pt-6 border-t border-slate-700 flex flex-col sm:flex-row justify-end gap-4 items-center">
          {parsedResult ? (
            <>
              <button 
                onClick={() => { setParsedResult(null); setFile(null); setTrainingPlan(null); }}
                className="px-6 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-slate-700 transition-colors font-semibold"
              >
                Scan Another Resume
              </button>
              
              <button 
                onClick={() => navigate('/guidance-chat', { 
                  state: { 
                    sessionId: sessionId,
                    skill: parsedResult.role
                  } 
                })} 
                className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-black rounded-xl shadow-[0_5px_20px_rgba(37,99,235,0.3)] transition-all flex items-center gap-2 hover:-translate-y-1"
              >
                <Bot size={20} />
                Talk to AI Mentor
              </button>
            </>
          ) : (
            <>
              {/* NEW LOCATION DROPDOWN */}
              <div className="w-full sm:w-64 relative">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                  <MapPin size={20} className="text-slate-400" />
                </div>
                <select 
                  value={userState}
                  onChange={(e) => setUserState(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-slate-200 pl-12 pr-4 py-4 rounded-xl appearance-none focus:outline-none focus:border-yellow-500 font-semibold"
                >
                  <option value="" disabled>Select your State...</option>
                  {INDIAN_STATES.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>

              {/* UPDATED ANALYZE BUTTON */}
              <button 
                onClick={handleParse}
                disabled={!file || !userState || isParsing}
                className={`w-full sm:w-auto px-8 py-4 font-black rounded-xl text-lg transition-all ${
                  !file || !userState || isParsing
                    ? "bg-slate-700 text-slate-500 cursor-not-allowed" 
                    : "bg-yellow-500 hover:bg-yellow-400 text-slate-900 shadow-[0_0_15px_rgba(234,179,8,0.3)] hover:-translate-y-1"
                }`}
              >
                {isParsing ? "Processing..." : "Analyze Resume"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};