const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const ASSESS_VOICE_ENDPOINT = `${API_BASE_URL}/api/assessment/assess-voice`;
const START_SESSION_ENDPOINT = `${API_BASE_URL}/api/assessment/start-session`; // Updated path

// ------------------------------------------------------------------
// 1. START SESSION (The Handshake)
// ------------------------------------------------------------------
export const startInterviewSession = async (skill, language) => {
  try {
    // Backend expects Form data, not JSON
    const formData = new FormData();
    formData.append("skill", skill);
    formData.append("language", language);

    const response = await fetch(START_SESSION_ENDPOINT, {
      method: "POST",
      body: formData, // Browser sets multipart/form-data automatically
    });

    if (!response.ok) throw new Error("Failed to start AI session");

    // Backend returns: { session_id, question, audio_base64 }
    const data = await response.json();

    // Magic trick: Convert the Base64 audio string into a playable URL
    const audioRes = await fetch(`data:audio/mpeg;base64,${data.audio_base64}`);
    const audioBlob = await audioRes.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    return { 
      sessionId: data.session_id, 
      initialQuestionText: data.question, // The translated text
      initialAudioUrl: audioUrl       // The real AI voice file!
    };

  } catch (error) {
    console.error("Error starting session:", error);
    throw error;
  }
};

// ------------------------------------------------------------------
// 2. THE INTERVIEW LOOP (Send Audio + Session ID)
// ------------------------------------------------------------------
export const sendAudioToAI = async (audioBlob, sessionId) => {
  const formData = new FormData();
  const extension = audioBlob?.type?.includes("mp4") ? "m4a" : "webm";
  
  // 1. Attach the user's voice
  formData.append("audio", audioBlob, `interview_audio.${extension}`);
  
  // 2. Attach the Session ID so the backend knows who is talking
  formData.append("session_id", sessionId);

  try {
    const response = await fetch(ASSESS_VOICE_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let detail = response.statusText;
      try {
        const errJson = await response.json();
        if (errJson?.detail) detail = errJson.detail;
      } catch (_) {}
      throw new Error(`Backend error: ${detail}`);
    }

    // Backend returns raw audio bytes
    const aiResponseBlob = await response.blob();
    const aiAudioUrl = URL.createObjectURL(aiResponseBlob);
    
    return { audioUrl: aiAudioUrl };

  } catch (error) {
    console.error("API Error connecting to Backend:", error);
    return { error: error?.message || "Unable to process voice response." };
  }
};