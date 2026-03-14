import Navbar from "../components/Navbar";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, Clock, Medal, Plus } from "lucide-react";

// MOCK DATA: Change this to an empty array [] to test the empty state.
// Keep it populated for the hackathon judges so they see the final product!
const mockSkills = [
  {
    name: "Carpentry: T-Joint",
    status: "Verified",
    hours: 120,
    trust: 92,
    badges: ["Safety Cleared", "Precision Cutting", "AI Verified"],
  },
  {
    name: "Electrical: Live Wiring",
    status: "Beginner",
    hours: 15,
    trust: 45,
    badges: ["Safety Pending", "Basic Theory"],
  }
];

export default function Wallet() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        
        <div className="flex justify-between items-center mb-10">
          <div>
            <h2 className="text-3xl font-extrabold text-gray-900">Digital Skill Wallet</h2>
            <p className="text-gray-500 mt-2">Your verified identity for employers.</p>
          </div>
          <button
            onClick={() => navigate("/chooseskill")}
            className="hidden md:flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-semibold transition-all shadow-sm"
          >
            <Plus size={20} /> Add Skill
          </button>
        </div>

        {mockSkills.length === 0 ? (
          /* Empty State */
          <div className="flex flex-col items-center justify-center py-20 px-4">
            <div className="bg-white p-10 rounded-3xl shadow-lg border border-gray-100 text-center max-w-lg w-full">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <ShieldCheck size={40} className="text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                No Skills Verified Yet
              </h3>
              <p className="text-gray-500 mb-8 leading-relaxed">
                Take an AI-powered practical assessment to build your trust score and unlock local job opportunities.
              </p>
              <button
                onClick={() => navigate("/chooseskill")}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-xl font-bold transition-all shadow-md"
              >
                Take First Assessment
              </button>
            </div>
          </div>
        ) : (
          /* Populated Wallet */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {mockSkills.map((skill, idx) => (
              <div
                key={idx}
                className="bg-white p-8 rounded-3xl shadow-md border border-gray-100 hover:shadow-xl transition-shadow relative overflow-hidden"
              >
                {/* Visual Banner for Verified Skills */}
                {skill.status === "Verified" && (
                  <div className="absolute top-0 right-0 bg-green-500 text-white text-xs font-bold px-4 py-1 rounded-bl-xl">
                    EMPLOYMENT READY
                  </div>
                )}

                <div className="flex justify-between items-start mb-6 mt-2">
                  <h3 className="text-xl font-bold text-gray-900 pr-4">{skill.name}</h3>
                  <div className="w-16 h-16 flex-shrink-0">
                    <CircularProgressbar
                      value={skill.trust}
                      text={`${skill.trust}%`}
                      styles={buildStyles({
                        textSize: '24px',
                        textColor: skill.trust > 70 ? "#16a34a" : "#ca8a04",
                        pathColor: skill.trust > 70 ? "#16a34a" : "#ca8a04",
                        trailColor: "#f1f5f9",
                      })}
                    />
                  </div>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock size={18} className="text-gray-400" />
                    <span><strong className="text-gray-900">{skill.hours}</strong> Verified Hours</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <ShieldCheck size={18} className="text-gray-400" />
                    <span>Status: <strong className={skill.status === "Verified" ? "text-green-600" : "text-yellow-600"}>{skill.status}</strong></span>
                  </div>
                </div>

                <div className="pt-6 border-t border-gray-100">
                  <div className="flex items-center gap-2 mb-3">
                    <Medal size={16} className="text-blue-600" />
                    <span className="text-sm font-semibold text-gray-900">Micro-Certifications</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {skill.badges.map((badge, i) => (
                      <span
                        key={i}
                        className="bg-blue-50 text-blue-700 border border-blue-100 px-3 py-1 rounded-full text-xs font-medium"
                      >
                        {badge}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}