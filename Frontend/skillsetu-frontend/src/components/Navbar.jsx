import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  const isLoggedIn = !!localStorage.getItem("userEmail");
  const role = localStorage.getItem("role");

  const logout = () => {
    localStorage.removeItem("userEmail");
    navigate("/");
  };

  return (
    <nav className="flex justify-between items-center px-8 py-4 bg-white dark:bg-slate-900 shadow">
      <h1
        className="text-2xl font-bold text-blue-600 cursor-pointer"
        onClick={() => navigate("/")}
      >
        SkillSetu
      </h1>

      <div className="flex gap-6 items-center">
        {/* NGO Dashboard */}
        {isLoggedIn && role === "government" && (
          <button
            onClick={() => navigate("/dashboard")}
            className="text-gray-700 dark:text-gray-200 hover:text-blue-600"
          >
            Dashboard
          </button>
        )}

        {!isLoggedIn ? (
          <>
            <button
              onClick={() => navigate("/login")}
              className="text-gray-700 dark:text-gray-200"
            >
              Login
            </button>

            <button
              onClick={() => navigate("/signup")}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg"
            >
              Signup
            </button>
          </>
        ) : (
          <button
            onClick={logout}
            className="bg-red-500 text-white px-4 py-2 rounded-lg"
          >
            Logout
          </button>
        )}
      </div>
    </nav>
  );
}
