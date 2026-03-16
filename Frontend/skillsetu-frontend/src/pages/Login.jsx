import { SignIn } from "@clerk/clerk-react";
import { dark } from "@clerk/themes";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4 font-sans">
      
      {/* Back Button */}
      <div className="w-full max-w-md mb-6">
        <button 
          onClick={() => navigate('/')}
          className="text-slate-400 hover:text-yellow-500 transition-colors flex items-center gap-2 text-sm font-semibold"
        >
          <span>←</span> Back to Home
        </button>
      </div>

      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500 mb-2">
          SkillSetu
        </h1>
        <p className="text-slate-400">Welcome back! Please login to continue.</p>
      </div>

      {/* Clerk Component */}
      <SignIn 
        routing="path" 
        path="/login" 
        signUpUrl="/signup"
        forceRedirectUrl="/"
        appearance={{
          baseTheme: dark,
          variables: {
            colorPrimary: '#eab308', // Tailwind yellow-500
            colorBackground: '#1e293b', // Tailwind slate-800
            colorInputBackground: '#0f172a', // Tailwind slate-900
          },
          elements: {
            card: "shadow-2xl border border-slate-700",
            headerTitle: "hidden",
            headerSubtitle: "hidden",
          }
        }}
      />
    </div>
  );
}