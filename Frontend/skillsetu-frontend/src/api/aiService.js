const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const ASSESS_VOICE_ENDPOINT = `${API_BASE_URL}/api/assessment/assess-voice`;
const START_SESSION_ENDPOINT = `${API_BASE_URL}/api/assessment/start-session`;
// MISSING ENDPOINT RESTORED:
const RESUME_PARSE_ENDPOINT = `${API_BASE_URL}/api/v1/resume/parse`;

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

    // 🛡️ BULLETPROOF CHECK: Is it JSON or a Raw File?
    const contentType = response.headers.get("content-type");
    
    if (contentType && contentType.includes("application/json")) {
      const data = await response.json();
      const audioUrl = `data:audio/mpeg;base64,${data.audio || data.audio_base64}`;
      return { 
        sessionId: data.session_id, 
        initialQuestionText: data.question, 
        initialAudioUrl: audioUrl       
      };
    } else {
      // If it's a raw audio file (FileResponse)
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const sessionId = response.headers.get("X-Session-ID") || `sess_${Date.now()}`;
      
      return { 
        sessionId: sessionId, 
        initialQuestionText: "Let's begin the assessment.", 
        initialAudioUrl: audioUrl       
      };
    }

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
        if (response.headers.get("content-type")?.includes("application/json")) {
          const errJson = await response.json();
          if (errJson?.detail) detail = errJson.detail;
        }
      } catch (_) {}
      throw new Error(`Backend error: ${detail}`);
    }

    // 🛡️ BULLETPROOF CHECK: Is it JSON or a Raw File?
    const contentType = response.headers.get("content-type");
    
    if (contentType && contentType.includes("application/json")) {
      const data = await response.json();
      const aiAudioUrl = `data:audio/mpeg;base64,${data.audio}`;
      return { 
        audioUrl: aiAudioUrl,
        text: data.interviewer_text || data.question 
      };
    } else {
      // It's a raw audio file (FileResponse)
      const aiResponseBlob = await response.blob();
      const aiAudioUrl = URL.createObjectURL(aiResponseBlob);
      return { 
        audioUrl: aiAudioUrl,
        text: null 
      };
    }

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

// ------------------------------------------------------------------
// 4. PARSE RESUME (The Missing Export Restored!)
// ------------------------------------------------------------------
export const parseResume = async (resumeFile) => {
  const formData = new FormData();
  formData.append("resume", resumeFile);

  try {
    const response = await fetch(RESUME_PARSE_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let detail = response.statusText;
      try {
        const errJson = await response.json();
        if (errJson?.detail) detail = errJson.detail;
      } catch (_) {}
      throw new Error(`Resume parse failed: ${detail}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Resume parse error:", error);
    throw error;
  }
};

// ------------------------------------------------------------------
// 5. GET TRAINING RECOMMENDATIONS
// ------------------------------------------------------------------
export const getTrainingRecommendations = async (sessionId) => {
  const TRAINING_ENDPOINT = `${(import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')}/api/training/recommend`;
  
  try {
    const response = await fetch(TRAINING_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: sessionId }) // Backend expects { user_id: "..." }
    });

    if (!response.ok) throw new Error("Failed to fetch training plan");
    
    const result = await response.json();
    return result.success ? result.data : null;
  } catch (error) {
    console.error("Training API Error:", error);
    return null;
  }
};