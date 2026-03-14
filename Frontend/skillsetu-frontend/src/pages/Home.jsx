import Layout from "../layout/Layout";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();
  const email = localStorage.getItem("userEmail");

  const startAssessment = () => {
    if (!email) navigate("/login");
    else navigate("/skills");
  };

  const openWallet = () => {
    if (!email) navigate("/login");
    else navigate("/wallet");
  };

  return (
    <Layout>
      <div className="flex justify-center items-center min-h-[70vh]">
        <div className="bg-white dark:bg-slate-800 p-12 rounded-2xl shadow-xl text-center max-w-xl w-full">
          <h1 className="text-4xl font-bold mb-4 text-gray-800 dark:text-white">
            Welcome to SkillSetu
          </h1>

          <p className="text-gray-500 dark:text-gray-300 mb-8">
            Verify your professional skills using AI powered interviews
          </p>

          <div className="flex justify-center gap-4">
            <button
              onClick={startAssessment}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg"
            >
              Start Skill Assessment
            </button>

            <button
              onClick={openWallet}
              className="bg-gray-700 hover:bg-gray-800 text-white px-6 py-3 rounded-lg"
            >
              Skill Wallet
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
