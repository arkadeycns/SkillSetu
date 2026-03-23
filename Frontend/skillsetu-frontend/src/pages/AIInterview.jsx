const API_BASE_URL = "http://127.0.0.1:8000";

// 🔥 LANGUAGE FIX
const mapLanguage = (language) => {
  const langMap = {
    English: "en",
    Hindi: "hi",
    Hinglish: "en",
  };
  return langMap[language] || "en";
};

// ---------------- START CHAT ----------------
export const startGuidanceChat = async (sessionId, language, skill) => {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("language", mapLanguage(language)); // ✅ FIX
  if (skill) formData.append("skill", skill);

  const res = await fetch(`${API_BASE_URL}/api/chat/start`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Chat start failed");

  return await res.json();
};

// ---------------- SEND AUDIO ----------------
export const sendAudioToGuidanceChat = async (
  audioBlob,
  sessionId,
  language,
  skill,
) => {
  const formData = new FormData();

  formData.append("audio", audioBlob, "audio.webm");
  formData.append("session_id", sessionId);
  formData.append("language", mapLanguage(language)); // ✅ FIX
  if (skill) formData.append("skill", skill);

  const res = await fetch(`${API_BASE_URL}/api/chat/`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Chat failed");

  return await res.json();
};
