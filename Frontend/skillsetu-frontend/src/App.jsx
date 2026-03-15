import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import ChooseSkill from "./pages/ChooseSkill";
import AIInterview from "./pages/AIInterview";
import Result from "./pages/Result";
import Wallet from "./pages/Wallet";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/DashBoard";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chooseskill" element={<ChooseSkill />} />
        <Route path="/interview" element={<AIInterview />} />
        <Route path="/result" element={<Result />} />
        <Route path="/wallet" element={<Wallet />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
