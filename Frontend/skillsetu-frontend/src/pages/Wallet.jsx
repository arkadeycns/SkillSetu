import Navbar from "../components/Navbar";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import { useNavigate } from "react-router-dom";

// Example: empty array for first-time login
const skills = [];

export default function Wallet() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar />

      <div className="max-w-5xl mx-auto py-12 px-6">
        <h2 className="text-3xl font-bold mb-8 text-center">My Skill Wallet</h2>

        {skills.length === 0 ? (
          // Modern empty state
          <div className="flex flex-col items-center justify-center mt-16">
            <div className="bg-gray-800 p-10 rounded-2xl shadow-2xl text-center max-w-md">
              <h3 className="text-2xl font-semibold mb-4">
                No Skills Added Yet
              </h3>
              <p className="text-gray-400 mb-6">
                Start adding your skills to build your trust score and earn
                micro-certifications!
              </p>
              <button
                onClick={() => navigate("/")}
                className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-semibold transition-all transform hover:scale-105"
              >
                Add Skill
              </button>
            </div>
          </div>
        ) : (
          // Skill cards if skills exist
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {skills.map((skill, idx) => (
              <div
                key={idx}
                className={`p-6 rounded-2xl shadow-2xl transition-transform transform hover:scale-105 ${
                  skill.status === "Verified" ? "bg-green-800" : "bg-gray-800"
                }`}
              >
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">{skill.name}</h3>
                  <span
                    className={`font-bold ${
                      skill.status === "Verified"
                        ? "text-green-400"
                        : skill.status === "Beginner"
                          ? "text-yellow-400"
                          : "text-red-400"
                    }`}
                  >
                    {skill.status === "Verified"
                      ? "✔"
                      : skill.status === "Beginner"
                        ? "⚡"
                        : "❌"}
                  </span>
                </div>

                <p className="text-gray-300 mb-2">
                  Hours: <span className="font-semibold">{skill.hours}</span>
                </p>

                <div className="w-20 h-20 mb-4 mx-auto">
                  <CircularProgressbar
                    value={skill.trust}
                    text={`${skill.trust}%`}
                    styles={buildStyles({
                      textColor: "#fff",
                      pathColor: skill.trust > 70 ? "#22c55e" : "#f59e0b",
                      trailColor: "#334155",
                    })}
                  />
                </div>

                <div className="flex flex-wrap gap-2 mt-2">
                  {skill.badges.map((badge, i) => (
                    <span
                      key={i}
                      className="bg-blue-600 text-white px-2 py-1 rounded-full text-xs"
                    >
                      {badge}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
