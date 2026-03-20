import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useUser, useClerk, UserButton } from "@clerk/clerk-react"; 
import { Wallet, LayoutDashboard, UserCheck, FileText, Bot, BarChart3 } from "lucide-react"; 

export default function Navbar() {
  const navigate = useNavigate();
  const { isSignedIn, isLoaded } = useUser();
  const { signOut } = useClerk();
  const role = localStorage.getItem("role");

  const handleLogout = async () => {
    // Clear the role from local storage
    localStorage.removeItem("role");
    // Sign out of Clerk and redirect home
    await signOut();
    navigate("/");
  };

  if (!isLoaded) return null; // Prevent flicker

  return (
    <nav className="flex justify-between items-center px-8 py-4 bg-slate-900 shadow-lg border-b border-slate-800 sticky top-0 z-50">
      
      {/* Logo with Golden Gradient */}
      <h1
        className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500 cursor-pointer tracking-tight"
        onClick={() => navigate("/")}
      >
        SkillSetu
      </h1>

      <div className="flex gap-4 md:gap-8 items-center">
        {isSignedIn ? (
          <>
            {/* GOVERNMENT ROLE LINKS */}
            {role === "government" && (
              <>
                <button
                  onClick={() => navigate("/dashboard")}
                  className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
                >
                  <LayoutDashboard size={18} />
                  <span className="hidden sm:inline">Dashboard</span>
                </button>
                
                {/* NEW: Regional Reports Link */}
                <button
                  onClick={() => navigate("/regional-reports")}
                  className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
                >
                  <BarChart3 size={18} />
                  <span className="hidden sm:inline">Regional Reports</span>
                </button>
              </>
            )}

            {/* STANDARD USER LINKS */}
            {role !== "government" && (
              <>
                {/* AI Coach Link */}
                <button
                  onClick={() => navigate("/choose-coach")}
                  className="flex items-center gap-2 text-slate-300 hover:text-blue-400 font-medium transition-colors"
                >
                  <Bot size={18} />
                  <span className="hidden lg:inline">AI Coach</span>
                </button>

                {/* Resume Scan Link */}
                <button
                  onClick={() => navigate("/resume-parser")}
                  className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
                >
                  <FileText size={18} />
                  <span className="hidden lg:inline">Resume Scan</span>
                </button>

                {/* Existing Assessment Link */}
                <button
                  onClick={() => navigate("/chooseskill")}
                  className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
                >
                  <UserCheck size={18} />
                  <span className="hidden lg:inline">Assessments</span>
                </button>
                
                {/* Existing Wallet Link */}
                <button
                  onClick={() => navigate("/wallet")}
                  className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
                >
                  <Wallet size={18} />
                  <span className="hidden lg:inline">Skill Wallet</span>
                </button>
              </>
            )}

            <div className="flex items-center gap-4 pl-2 md:pl-4 border-l border-slate-700">
              <UserButton 
                afterSignOutUrl="/" 
                appearance={{
                  elements: {
                    userButtonAvatarBox: "w-10 h-10 border border-yellow-500/50"
                  }
                }}
              />
              <button
                onClick={handleLogout}
                className="hidden sm:block text-xs text-slate-500 hover:text-red-400 transition-colors uppercase tracking-widest font-bold"
              >
                Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <button
              onClick={() => navigate("/login")}
              className="text-slate-300 hover:text-yellow-500 font-medium transition-colors"
            >
              Login
            </button>

            <button
              onClick={() => navigate("/signup")}
              className="bg-yellow-500 hover:bg-yellow-400 text-slate-900 px-6 py-2 rounded-lg font-bold transition-all shadow-[0_0_15px_rgba(234,179,8,0.2)]"
            >
              Signup
            </button>
          </>
        )}
      </div>
    </nav>
  );
}