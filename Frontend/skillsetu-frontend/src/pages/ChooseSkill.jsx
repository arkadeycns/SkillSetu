import Layout from "../layout/Layout";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ChooseSkill() {
  const navigate = useNavigate();
  const [skill, setSkill] = useState("");

  const skills = ["Electrician", "Plumber", "Carpenter", "Mechanic", "Welder"];

  const startInterview = () => {
    if (skill) navigate("/interview");
    else alert("Please select a profession");
  };

  return (
    <Layout>
      <div className="flex justify-center items-center min-h-[70vh]">
        <div className="w-[420px] bg-white dark:bg-gray-900 p-10 rounded-2xl shadow-2xl">
          <h1 className="text-3xl font-bold text-center text-gray-800 dark:text-white mb-6">
            Verify Your Skill
          </h1>

          <p className="text-gray-500 dark:text-gray-400 text-center mb-8">
            Select your profession to begin AI assessment
          </p>

          <label className="block text-sm text-gray-500 dark:text-gray-400 mb-2">
            Profession
          </label>

          <select
            value={skill}
            onChange={(e) => setSkill(e.target.value)}
            className="w-full p-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-white mb-6"
          >
            <option value="">Select profession</option>

            {skills.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>

          <button
            onClick={startInterview}
            className="w-full bg-blue-600 hover:bg-blue-700 p-3 rounded-lg text-white"
          >
            Start AI Interview
          </button>
        </div>
      </div>
    </Layout>
  );
}
