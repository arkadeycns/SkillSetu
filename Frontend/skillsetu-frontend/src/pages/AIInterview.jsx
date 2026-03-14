import Layout from "../layout/Layout";
import { useNavigate } from "react-router-dom";
import { useState, useRef } from "react";

export default function AIInterview() {
  const navigate = useNavigate();
  const [answer, setAnswer] = useState("");
  const recognitionRef = useRef(null);

  // Voice to text
  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.start();

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setAnswer((prev) => prev + " " + text);
    };

    recognitionRef.current = recognition;
  };

  return (
    <Layout>
      <div className="flex justify-center items-center min-h-[70vh]">
        <div className="w-[750px] bg-white dark:bg-slate-800 rounded-xl shadow-xl p-8">
          <h2 className="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white">
            AI Skill Interview
          </h2>

          {/* Question */}
          <div className="bg-gray-200 dark:bg-slate-700 p-4 rounded-lg mb-6">
            <p className="text-gray-800 dark:text-gray-200">
              What safety precautions should be followed while handling live
              electrical wires?
            </p>
          </div>

          {/* Answer box */}
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here..."
            className="w-full h-32 p-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-slate-900 text-gray-800 dark:text-white focus:outline-none"
          />

          {/* Buttons */}
          <div className="flex justify-between items-center mt-6">
            <button
              onClick={startListening}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
            >
              🎤 Speak
            </button>

            <button
              onClick={() => navigate("/result")}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              Submit Answer
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
