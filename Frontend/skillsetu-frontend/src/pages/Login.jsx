import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Mail, Briefcase, Building2 } from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e, role) => {
    e.preventDefault();
    if (!email.trim()) {
      alert("Please enter your email!");
      return;
    }

    localStorage.setItem("userEmail", email);
    localStorage.setItem("role", role);

    // Redirect based on role
    if (role === "worker") {
      navigate("/"); // Or navigate("/chooseskill") if you want them to go straight to assessment
    } else {
      navigate("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-blue-600 mb-2">SkillSetu</h1>
          <p className="text-gray-500">Welcome back! Please login to continue.</p>
        </div>

        <form className="space-y-6">
          {/* Email Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                required
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-3 pt-2">
            <button
              onClick={(e) => handleLogin(e, "worker")}
              className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition-colors shadow-sm"
            >
              <Briefcase size={20} />
              Login as Worker
            </button>

            <button
              onClick={(e) => handleLogin(e, "government")}
              className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-900 text-white py-3 rounded-lg font-semibold transition-colors shadow-sm"
            >
              <Building2 size={20} />
              Login as Govt Official
            </button>
          </div>
        </form>

        {/* Footer Link */}
        <p className="mt-8 text-center text-sm text-gray-600">
          Don't have an account?{" "}
          <Link to="/signup" className="text-blue-600 hover:text-blue-800 font-semibold transition-colors">
            Sign up here
          </Link>
        </p>
      </div>
    </div>
  );
}