import Layout from "../layout/Layout";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Zap, Wrench, Hammer, Car, Flame, ArrowRight } from "lucide-react";

export default function ChooseSkill() {
  const navigate = useNavigate();
  const [selectedSkill, setSelectedSkill] = useState("");

  const skills = [
    { name: "Electrician", icon: <Zap size={32} /> },
    { name: "Plumber", icon: <Wrench size={32} /> },
    { name: "Carpenter", icon: <Hammer size={32} /> },
    { name: "Mechanic", icon: <Car size={32} /> },
    { name: "Welder", icon: <Flame size={32} /> },
  ];

  const startInterview = () => {
    if (selectedSkill) {
      navigate("/interview", { state: { skill: selectedSkill } });
    } else {
      alert("Please select a profession to continue.");
    }
  };

  return (
    <Layout>
      <div className="flex justify-center items-center min-h-[80vh] bg-gray-50 p-4">
        <div className="w-full max-w-2xl bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-extrabold text-gray-900 mb-3">
              Verify Your Skill
            </h1>
            <p className="text-gray-500">
              Select your trade to begin the AI-powered practical assessment.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-10">
            {skills.map((skill) => (
              <button
                key={skill.name}
                onClick={() => setSelectedSkill(skill.name)}
                className={`flex flex-col items-center justify-center p-6 rounded-2xl border-2 transition-all duration-200 ${
                  selectedSkill === skill.name
                    ? "border-blue-600 bg-blue-50 text-blue-700 shadow-md"
                    : "border-gray-200 bg-white text-gray-600 hover:border-blue-300 hover:bg-blue-50/50"
                }`}
              >
                <div className={`mb-3 ${selectedSkill === skill.name ? "text-blue-600" : "text-gray-500"}`}>
                  {skill.icon}
                </div>
                <span className="font-semibold">{skill.name}</span>
              </button>
            ))}
          </div>

          <button
            onClick={startInterview}
            disabled={!selectedSkill}
            className={`w-full flex items-center justify-center gap-2 p-4 rounded-xl font-bold text-lg transition-all ${
              selectedSkill
                ? "bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-200 hover:-translate-y-1"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            Start AI Interview
            <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </Layout>
  );
}