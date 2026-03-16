import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export const ResumeParser = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [parseStep, setParseStep] = useState("");
  const [parsedResult, setParsedResult] = useState(null);

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
    if (droppedFile && droppedFile.type === "application/pdf") {
      setFile(droppedFile);
    } else {
      alert("Please upload a valid PDF file.");
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) setFile(selectedFile);
  };

  // Mock AI Parsing Sequence
  const handleParse = () => {
    if (!file) return;
    setIsParsing(true);
    setParseStep("Extracting document text...");

    // Simulate API pipeline delays for a realistic UX
    setTimeout(() => setParseStep("Analyzing work experience..."), 1500);
    setTimeout(() => setParseStep("Mapping technical skills..."), 3000);
    setTimeout(() => setParseStep("Generating career heatmap..."), 4500);
    
    setTimeout(() => {
      setIsParsing(false);
      setParsedResult({
        name: "Extracted from Resume",
        role: "Full-Stack Developer (MERN)",
        confidence: "94%",
        skills: ["React.js", "Node.js", "MongoDB", "Python", "SQL", "Machine Learning"],
        experience: "Mid-Level (3+ Years equivalent)",
      });
    }, 6000);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 font-sans p-6 md:p-12 flex flex-col items-center">
      
      {/* Navigation & Header */}
      <div className="w-full max-w-4xl flex justify-between items-center mb-12">
        <button 
          onClick={() => navigate('/')}
          className="text-slate-400 hover:text-yellow-500 transition-colors flex items-center gap-2 text-sm font-semibold"
        >
          <span>←</span> Back to Home
        </button>
        <div className="px-3 py-1 bg-slate-800 border border-yellow-500/30 rounded-full text-xs text-yellow-500 tracking-widest uppercase">
          Enterprise Portal
        </div>
      </div>

      <div className="w-full max-w-3xl text-center space-y-4 mb-10">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500">
          AI Resume Intelligence
        </h1>
        <p className="text-slate-400 text-lg">
          Upload your resume in PDF format. Our NLP engine will extract your core competencies and benchmark them against industry standards.
        </p>
      </div>

      {/* Main Interface */}
      <div className="w-full max-w-2xl bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 shadow-2xl">
        
        {/* State 1: Upload Zone */}
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
              accept=".pdf" 
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
                <p className="text-sm text-slate-400">or click to browse (PDF only)</p>
              </div>
            )}
          </div>
        )}

        {/* State 2: Parsing Animation */}
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

        {/* State 3: Parsed Results */}
        {parsedResult && !isParsing && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="flex items-center justify-between border-b border-slate-700 pb-4">
              <div>
                <h3 className="text-2xl font-bold text-white">{parsedResult.role}</h3>
                <p className="text-slate-400">{parsedResult.experience}</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-slate-400">Match Confidence</div>
                <div className="text-2xl font-bold text-yellow-500">{parsedResult.confidence}</div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Extracted Skills</h4>
              <div className="flex flex-wrap gap-2">
                {parsedResult.skills.map((skill, index) => (
                  <span key={index} className="px-3 py-1 bg-slate-700 border border-slate-600 rounded-md text-sm text-yellow-50">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-8 pt-6 border-t border-slate-700 flex justify-end gap-4">
          {parsedResult ? (
            <>
              <button 
                onClick={() => { setParsedResult(null); setFile(null); }}
                className="px-6 py-2 rounded-md text-slate-300 hover:text-white transition-colors"
              >
                Scan Another
              </button>
              <button 
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 bg-yellow-500 hover:bg-yellow-400 text-slate-900 font-bold rounded-md shadow-[0_0_10px_rgba(234,179,8,0.2)] transition-all"
              >
                View Skill Dashboard →
              </button>
            </>
          ) : (
            <button 
              onClick={handleParse}
              disabled={!file || isParsing}
              className={`w-full px-6 py-3 font-bold rounded-md transition-all ${
                !file || isParsing
                  ? "bg-slate-700 text-slate-500 cursor-not-allowed" 
                  : "bg-yellow-500 hover:bg-yellow-400 text-slate-900 shadow-[0_0_15px_rgba(234,179,8,0.3)]"
              }`}
            >
              {isParsing ? "Processing..." : "Analyze Resume"}
            </button>
          )}
        </div>
      </div>

    </div>
  );
};
