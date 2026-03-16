import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useUser, useClerk, UserButton } from "@clerk/clerk-react"; 
import { Wallet, LayoutDashboard, UserCheck } from "lucide-react"; 

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

      <div className="flex gap-8 items-center">
        {isSignedIn ? (
          <>
            {role === "government" && (
              <button
                onClick={() => navigate("/dashboard")}
                className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
              >
                <LayoutDashboard size={18} />
                Dashboard
              </button>
            )}

            {role !== "government" && (
              <>
                <button
                  onClick={() => navigate("/chooseskill")}
                  className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
                >
                  <UserCheck size={18} />
                  Assessments
                </button>
                <button
                  onClick={() => navigate("/wallet")}
                  className="flex items-center gap-2 text-slate-300 hover:text-yellow-500 font-medium transition-colors"
                >
                  <Wallet size={18} />
                  My Wallet
                </button>
              </>
            )}

            <div className="flex items-center gap-4 pl-4 border-l border-slate-700">
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
                className="text-xs text-slate-500 hover:text-red-400 transition-colors uppercase tracking-widest font-bold"
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