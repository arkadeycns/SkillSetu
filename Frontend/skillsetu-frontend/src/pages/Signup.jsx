import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("worker"); // default role
  const navigate = useNavigate();

  const handleSignup = () => {
    if (!email) {
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
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow-xl w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">Create Account</h1>

        {/* Email Input */}
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border p-3 rounded mb-4"
        />

        {/* Role Selector */}
        <div className="mb-6">
          <p className="text-gray-600 mb-2 font-medium">Select your role</p>

          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full border p-3 rounded"
          >
            <option value="worker">Worker</option>
            <option value="government">Government Official</option>
          </select>
        </div>

        {/* Signup Button */}
        <button
          onClick={handleSignup}
          className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700"
        >
          Sign Up
        </button>
      </div>
    </div>
  );
}
