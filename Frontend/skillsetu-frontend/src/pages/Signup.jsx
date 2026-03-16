import { useState, useEffect } from "react";
import { SignUp } from "@clerk/clerk-react";
import { dark } from "@clerk/themes";
import { useNavigate } from "react-router-dom";
import { Briefcase, Building2 } from "lucide-react";

export default function Signup() {
  const navigate = useNavigate();
  // Default to worker, save to local storage immediately so it's ready post-signup
  const [role, setRole] = useState(localStorage.getItem("role") || "worker");

  useEffect(() => {
    localStorage.setItem("role", role);
  }, [role]);

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4 font-sans py-12">
      
      {/* Back Button */}
      <div className="w-full max-w-md mb-6">
        <button 
          onClick={() => navigate('/')}
          className="text-slate-400 hover:text-yellow-500 transition-colors flex items-center gap-2 text-sm font-semibold"
        >
          <span>←</span> Back to Home
        </button>
      </div>

      {/* Header */}
      <div className="text-center mb-6">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500 mb-2">
          Create Account
        </h1>
        <p className="text-slate-400">Join the SkillSetu network today.</p>
      </div>

      {/* Custom Role Selector Wrapper */}
      <div className="w-full max-w-md mb-6 bg-slate-800 p-2 rounded-xl border border-slate-700 flex gap-2">
        <button
          onClick={() => setRole("worker")}
          className={`flex-1 py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            role === "worker" 
              ? "bg-yellow-500 text-slate-900 shadow-md" 
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-700"
          }`}
        >
          <Briefcase size={18} />
          Worker
        </button>
        <button
          onClick={() => setRole("government")}
          className={`flex-1 py-3 px-4 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
            role === "government" 
              ? "bg-yellow-500 text-slate-900 shadow-md" 
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-700"
          }`}
        >
          <Building2 size={18} />
          Official
        </button>
      </div>

      {/* Clerk Component */}
      <SignUp 
        routing="path" 
        path="/signup" 
        signInUrl="/login"
        forceRedirectUrl={role === "government" ? "/dashboard" : "/"}
        appearance={{
          baseTheme: dark,
          variables: {
            colorPrimary: '#eab308',
            colorBackground: '#1e293b',
            colorInputBackground: '#0f172a',
          },
          elements: {
            card: "shadow-2xl border border-slate-700",
            headerTitle: "hidden",
            headerSubtitle: "hidden",
          }
        }}
      />
    </div>
  );
}