const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const ASSESS_VOICE_ENDPOINT = `${API_BASE_URL}/api/assessment/assess-voice`;
const START_SESSION_ENDPOINT = `${API_BASE_URL}/api/assessment/start-session`;

// ------------------------------------------------------------------
// 1. START SESSION (The Handshake)
// ------------------------------------------------------------------
export const startInterviewSession = async (skill, language) => {
  try {
    const formData = new FormData();
    formData.append("skill", skill);
    formData.append("language", language);

    const response = await fetch(START_SESSION_ENDPOINT, {
      method: "POST",
      body: formData, 
    });

    if (!response.ok) throw new Error("Failed to start AI session");

    const data = await response.json();

    // FIXED: Catch the new "audio" key your friend used!
    const audioUrl = `data:audio/mpeg;base64,${data.audio}`;

    return { 
      sessionId: data.session_id, 
      initialQuestionText: data.question, 
      initialAudioUrl: audioUrl       
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
  
  formData.append("audio", audioBlob, `interview_audio.${extension}`);
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

    // FIXED: The backend now returns JSON, not a raw file!
    const data = await response.json();
    
    // Convert the base64 string directly into a playable URL
    const aiAudioUrl = `data:audio/mpeg;base64,${data.audio}`;
    
    // We now return BOTH the audio and the new "interviewer_text" 
    return { 
      audioUrl: aiAudioUrl,
      text: data.interviewer_text 
    };

  } catch (error) {
    console.error("API Error connecting to Backend:", error);
    return { error: error?.message || "Unable to process voice response." };
  }
};

// ------------------------------------------------------------------
// 3. GET INTERVIEW SUMMARY & RESULT
// ------------------------------------------------------------------
export const getInterviewSummary = async (sessionId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/assessment/${sessionId}/summary`);
    
    if (!response.ok) {
      throw new Error("Failed to fetch summary from backend.");
    }
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error("API Error fetching summary:", error);
    return null; 
  }
};