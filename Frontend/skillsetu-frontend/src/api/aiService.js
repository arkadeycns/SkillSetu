// ================= BASE CONFIG =================
const API_BASE_URL = "http://127.0.0.1:8000";

const ASSESS_VOICE_ENDPOINT = `${API_BASE_URL}/api/assessment/assess-voice`;
const START_SESSION_ENDPOINT = `${API_BASE_URL}/api/assessment/start-session`;
const RESUME_PARSE_ENDPOINT = `${API_BASE_URL}/api/resume/parse`;

// ================= LANGUAGE FIX =================
const mapLanguage = (language) => {
  const langMap = {
    English: "en",
    Hindi: "hi",
    Hinglish: "Hinglish",
  };
  return langMap[language] || "en";
};

// ------------------------------------------------------------------
// 1. START SESSION
// ------------------------------------------------------------------
export const startInterviewSession = async (skill, language) => {
  try {
    console.log("START SESSION API:", START_SESSION_ENDPOINT);

    const formData = new FormData();
    formData.append("skill", skill);
    formData.append("language", mapLanguage(language)); // ✅ FIX

    const response = await fetch(START_SESSION_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed: ${response.status}`);
    }

    const data = await response.json();

    return {
      sessionId: data.session_id,
      initialQuestionText: data.question,
      initialAudioUrl: data.audio
        ? `data:audio/mpeg;base64,${data.audio}`
        : null,
    };
  } catch (error) {
    console.error("Error starting session:", error);
    throw error;
  }
};

// ------------------------------------------------------------------
// 2. SEND AUDIO TO AI
// ------------------------------------------------------------------
export const sendAudioToAI = async (audioBlob, sessionId) => {
  try {
    const formData = new FormData();
    const extension = audioBlob?.type?.includes("mp4") ? "m4a" : "webm";

    formData.append("audio", audioBlob, `audio.${extension}`);
    formData.append("session_id", sessionId);

    const response = await fetch(ASSESS_VOICE_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();

    return {
      audioUrl: data.audio ? `data:audio/mpeg;base64,${data.audio}` : null,
      text: data.interviewer_text || data.question,
    };
  } catch (error) {
    console.error("Voice API Error:", error);
    return { error: "Voice processing failed" };
  }
};

// ------------------------------------------------------------------
// 3. GET SUMMARY
// ------------------------------------------------------------------
export const getInterviewSummary = async (sessionId) => {
  try {
    const url = `${API_BASE_URL}/api/assessment/${sessionId}/summary`;

    const response = await fetch(url);

    if (!response.ok) throw new Error("Failed summary");

    return await response.json();
  } catch (error) {
    console.error("Summary error:", error);
    return null;
  }
};

// ------------------------------------------------------------------
// 4. PARSE RESUME
// ------------------------------------------------------------------
export const parseResume = async (resumeFile) => {
  try {
    console.log("RESUME API:", RESUME_PARSE_ENDPOINT);

    const formData = new FormData();
    formData.append("resume", resumeFile);

    const response = await fetch(RESUME_PARSE_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Resume parse failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Resume parse error:", error);
    throw error;
  }
};

// ------------------------------------------------------------------
// 5. TRAINING RECOMMENDATIONS
// ------------------------------------------------------------------
export const getTrainingRecommendations = async (
  sessionId,
  contextData = {},
) => {
  try {
    const payload = {
      user_id: sessionId,
      role: contextData.role || null,
      skills: contextData.skills || [],
      language: mapLanguage(contextData.language), // ✅ FIX
      strengths: contextData.strengths || [],
      gaps: contextData.gaps || [],
    };

    const response = await fetch(`${API_BASE_URL}/api/training/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error("Training failed");

    const result = await response.json();
    return result.success ? result.data : null;
  } catch (error) {
    console.error("Training error:", error);
    return null;
  }
};

// ------------------------------------------------------------------
// 6. START GUIDANCE CHAT
// ------------------------------------------------------------------
export const startGuidanceChat = async (
  sessionId,
  language = "English",
  skill = "",
) => {
  try {
    const url = `${API_BASE_URL}/api/chat/start`;

    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("language", mapLanguage(language)); // ✅ FIX
    if (skill) formData.append("skill", skill);

    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Chat start failed");

    const data = await response.json();

    return {
      text: data.greeting,
      audioUrl: data.audio ? `data:audio/mpeg;base64,${data.audio}` : null,
    };
  } catch (error) {
    console.error("Chat start error:", error);
    return { error: "Failed to start chat" };
  }
};

// ------------------------------------------------------------------
// 7. SEND AUDIO TO CHAT
// ------------------------------------------------------------------
export const sendAudioToGuidanceChat = async (
  audioBlob,
  sessionId,
  language = "English",
  skill = "",
) => {
  try {
    const url = `${API_BASE_URL}/api/chat/`;

    const formData = new FormData();
    const extension = audioBlob?.type?.includes("mp4") ? "m4a" : "webm";

    formData.append("audio", audioBlob, `chat.${extension}`);
    formData.append("session_id", sessionId);
    formData.append("language", mapLanguage(language)); // ✅ FIX
    if (skill) formData.append("skill", skill);

    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Chat failed");

    const data = await response.json();

    return {
      text: data.reply,
      audioUrl: data.audio ? `data:audio/mpeg;base64,${data.audio}` : null,
    };
  } catch (error) {
    console.error("Chat error:", error);
    return { error: "Chat failed" };
  }
};

// ------------------------------------------------------------------
// 8. SAVE RESULT
// ------------------------------------------------------------------
export const saveInterviewResult = async (payload) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/assessment/save-result`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error("Save failed");

    return await response.json();
  } catch (error) {
    console.error("Save result error:", error);
  }
};

// ------------------------------------------------------------------
// 9. GET USER SKILLS
// ------------------------------------------------------------------
export const getUserSkills = async (userId) => {
  try {
    const res = await fetch(
      `${API_BASE_URL}/api/assessment/my-skills/${userId}`,
    );

    if (!res.ok) throw new Error("Failed skills");

    return await res.json();
  } catch (error) {
    console.error("Skills error:", error);
    return null;
  }
};
