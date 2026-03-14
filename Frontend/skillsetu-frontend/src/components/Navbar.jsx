import { useNavigate, useLocation } from "react-router-dom";
import { LogOut, Wallet, LayoutDashboard, UserCheck } from "lucide-react"; 

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation(); // This forces the Navbar to re-render when routes change!

  // Derive state from localStorage
  const userEmail = localStorage.getItem("userEmail");
  const role = localStorage.getItem("role");
  const isLoggedIn = !!userEmail;

  const logout = () => {
    // FIX: Clear ALL user data on logout to prevent state bleeding
    localStorage.removeItem("userEmail");
    localStorage.removeItem("role");
    navigate("/");
  };

  return (
    <nav className="flex justify-between items-center px-8 py-4 bg-white dark:bg-slate-900 shadow-sm border-b border-gray-100 sticky top-0 z-50">
      
      {/* Logo */}
      <h1
        className="text-2xl font-extrabold text-blue-600 cursor-pointer tracking-tight"
        onClick={() => navigate("/")}
      >
        SkillSetu
      </h1>

      <div className="flex gap-6 items-center">
        {isLoggedIn ? (
          <>
            {/* 1. Government / NGO View */}
            {role === "government" && (
              <button
                onClick={() => navigate("/dashboard")}
                className="flex items-center gap-2 text-gray-700 dark:text-gray-200 hover:text-blue-600 font-medium transition-colors"
              >
                <LayoutDashboard size={18} />
                Dashboard
              </button>
            )}

            {/* 2. Worker / Candidate View */}
            {role !== "government" && (
              <>
                <button
                  onClick={() => navigate("/chooseskill")}
                  className="flex items-center gap-2 text-gray-700 dark:text-gray-200 hover:text-blue-600 font-medium transition-colors"
                >
                  <UserCheck size={18} />
                  Assessments
                </button>
                <button
                  onClick={() => navigate("/wallet")}
                  className="flex items-center gap-2 text-gray-700 dark:text-gray-200 hover:text-blue-600 font-medium transition-colors"
                >
                  <Wallet size={18} />
                  My Wallet
                </button>
              </>
            )}

            {/* Logout Button */}
            <button
              onClick={logout}
              className="flex items-center gap-2 bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700 px-4 py-2 rounded-lg font-medium transition-all"
            >
              <LogOut size={18} />
              Logout
            </button>
          </>
        ) : (
          <>
            {/* Logged Out View */}
            <button
              onClick={() => navigate("/login")}
              className="text-gray-700 dark:text-gray-200 hover:text-blue-600 font-medium transition-colors"
            >
              Login
            </button>

            <button
              onClick={() => navigate("/signup")}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-all shadow-sm hover:shadow-md"
            >
              Signup
            </button>
          </>
        )}
      </div>
    </nav>
  );
}