import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ClerkProvider } from "@clerk/clerk-react";

import Home from "./pages/Home";
import { ResumeParser } from "./pages/ResumeParser";
import ChooseSkill from "./pages/ChooseSkill";
import AIInterview from "./pages/AIInterview";
import Result from "./pages/Result";
import Wallet from "./pages/Wallet";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/DashBoard";
import RegionalReports from "./pages/RegionalReports";

// Import your publishable key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Publishable Key");
}

function App() {
  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/resume-parser" element={<ResumeParser />} />
          
          <Route path="/login/*" element={<Login />} />
          <Route path="/signup/*" element={<Signup />} /> 
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chooseskill" element={<ChooseSkill />} />
          <Route path="/interview" element={<AIInterview />} />
          <Route path="/wallet" element={<Wallet />} /> 
          <Route path="/regional-reports" element={<RegionalReports />} />
          <Route path="/result" element={<Result />} />
        </Routes>
      </BrowserRouter>
    </ClerkProvider>
  );
}

export default App;