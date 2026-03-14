import Layout from "../layout/Layout";
import { useNavigate } from "react-router-dom";
import { Mic, ShieldCheck, Globe, ArrowRight, Activity } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();
  const email = localStorage.getItem("userEmail");
  const role = localStorage.getItem("role");

  const handlePrimaryClick = () => {
    if (!email) {
      navigate("/signup");
    } else if (role === "government") {
      navigate("/dashboard");
    } else {
      navigate("/chooseskill");
    }
  };

  const handleSecondaryClick = () => {
    if (!email) {
      navigate("/login");
    } else if (role === "government") {
      navigate("/dashboard");
    } else {
      navigate("/wallet");
    }
  };

  return (
    <Layout>
      <div className="bg-slate-50 min-h-screen">
        
        <section className="relative px-6 py-20 md:py-32 max-w-7xl mx-auto flex flex-col items-center text-center">
          <div className="absolute top-0 w-full h-full bg-blue-50/50 -z-10 rounded-b-[3rem] blur-3xl"></div>
          
          <div className="inline-block bg-blue-100 text-blue-700 px-4 py-1.5 rounded-full text-sm font-bold tracking-wide mb-6">
            SkillSetu AI-Powered Competency Verification
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900 tracking-tight mb-8 leading-tight max-w-4xl">
            Prove your practical skills. <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-emerald-500">
              Speak your way to a job.
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-600 mb-10 max-w-2xl leading-relaxed">
            Bypass the resume barrier. SkillSetu is an AI mentor that verifies what you can actually do through natural voice conversations in your native language.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <button
              onClick={handlePrimaryClick}
              className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-xl hover:-translate-y-1"
            >
              {email ? (role === "government" ? "Open Command Center" : "Take an Assessment") : "Get Started for Free"}
              <ArrowRight size={20} />
            </button>
            
            <button
              onClick={handleSecondaryClick}
              className="flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-800 border-2 border-slate-200 px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-sm"
            >
              {email ? (role === "government" ? "View Analytics" : "Open Skill Wallet") : "Login to Account"}
            </button>
          </div>
        </section>


        <section className="px-6 py-20 bg-white">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-extrabold text-slate-900">Built for the Vernacular Workforce</h2>
              <p className="text-slate-500 mt-4 max-w-2xl mx-auto">We've replaced theory-heavy written exams with a platform that tests applied knowledge.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              
              {/* Feature 1 */}
              <div className="bg-slate-50 p-8 rounded-3xl border border-slate-100 hover:border-blue-200 transition-colors">
                <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
                  <Globe className="text-blue-600" size={28} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Multilingual Voice AI</h3>
                <p className="text-slate-600 leading-relaxed">
                  No typing required. Complete scenario-based tests by verbally explaining step-by-step processes in Hindi, Hinglish, or your native dialect.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="bg-slate-50 p-8 rounded-3xl border border-slate-100 hover:border-emerald-200 transition-colors">
                <div className="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center mb-6">
                  <ShieldCheck className="text-emerald-600" size={28} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Dynamic Skill Wallet</h3>
                <p className="text-slate-600 leading-relaxed">
                  Every successful assessment builds your dynamic trust score. Generate verified micro-certifications that employers can instantly authenticate.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="bg-slate-50 p-8 rounded-3xl border border-slate-100 hover:border-purple-200 transition-colors">
                <div className="w-14 h-14 bg-purple-100 rounded-2xl flex items-center justify-center mb-6">
                  <Activity className="text-purple-600" size={28} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Policy Intelligence</h3>
                <p className="text-slate-600 leading-relaxed">
                  Empowering NGOs and policymakers with district-level demand heatmaps to deploy targeted training exactly where skill gaps exist.
                </p>
              </div>

            </div>
          </div>
        </section>

      </div>
    </Layout>
  );
}