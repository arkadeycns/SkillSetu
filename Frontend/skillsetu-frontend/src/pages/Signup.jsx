import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Mail, ShieldCheck } from "lucide-react";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("worker"); 
  const navigate = useNavigate();

  const handleSignup = (e) => {
    e.preventDefault();
    if (!email.trim()) {
      alert("Please enter your email");
      return;
    }

    // Save user info
    localStorage.setItem("userEmail", email);
    localStorage.setItem("role", role);

    // Redirect based on role
    if (role === "worker") {
      navigate("/");
    } else {
      navigate("/dashboard");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-blue-600 mb-2">Create Account</h1>
          <p className="text-gray-500">Join SkillSetu today</p>
        </div>

        <form onSubmit={handleSignup} className="space-y-6">
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

          {/* Role Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Select your role</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <ShieldCheck className="h-5 w-5 text-gray-400" />
              </div>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all appearance-none bg-white"
              >
                <option value="worker">Worker / Candidate</option>
                <option value="government">Government / NGO Official</option>
              </select>
            </div>
          </div>

          {/* Signup Button */}
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-sm mt-4"
          >
            Create Account
          </button>
        </form>

        {/* Footer Link */}
        <p className="mt-8 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:text-blue-800 font-semibold transition-colors">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}