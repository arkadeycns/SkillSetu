import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  const handleLogin = (role) => {
    if (!email) {
      alert("Please enter your email!");
      return;
    }

    localStorage.setItem("userEmail", email);
    localStorage.setItem("role", role);

    if (role === "worker") {
      navigate("/");
    } else {
      navigate("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-xl">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Welcome to SkillSetu
        </h1>

        <p className="text-gray-500 text-center mb-6">Login to continue</p>

        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-gray-300 rounded px-4 py-3 mb-6"
        />

        <div className="flex flex-col gap-4">
          <button
            onClick={() => handleLogin("worker")}
            className="bg-blue-600 hover:bg-blue-700 text-white py-3 rounded font-semibold"
          >
            Login as Worker
          </button>

          <button
            onClick={() => handleLogin("government")}
            className="bg-green-600 hover:bg-green-700 text-white py-3 rounded font-semibold"
          >
            Login as Govt Official
          </button>
        </div>
      </div>
    </div>
  );
}
