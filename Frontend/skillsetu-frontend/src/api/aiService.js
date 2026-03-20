const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const ASSESS_VOICE_ENDPOINT = `${API_BASE_URL}/api/assessment/assess-voice`;
const START_SESSION_ENDPOINT = `${API_BASE_URL}/api/assessment/start-session`;
const RESUME_PARSE_ENDPOINT = `${API_BASE_URL}/api/v1/resume/parse`;

// ------------------------------------------------------------------
// 1. START SESSION (AI Interview)
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
// 2. SEND AUDIO TO AI (AI Interview)
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

    const contentType = response.headers.get("content-type");
    
    if (contentType && contentType.includes("application/json")) {
      const data = await response.json();
      const aiAudioUrl = `data:audio/mpeg;base64,${data.audio}`;
      return { 
        audioUrl: aiAudioUrl,
        text: data.interviewer_text || data.question 
      };
    } else {
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
// 3. GET INTERVIEW SUMMARY
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
// 4. PARSE RESUME
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
  const TRAINING_ENDPOINT = `${API_BASE_URL}/api/training/recommend`;
  
  try {
    const response = await fetch(TRAINING_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: sessionId }) 
    });

    if (!response.ok) throw new Error("Failed to fetch training plan");
    
    const result = await response.json();
    return result.success ? result.data : null;
  } catch (error) {
    console.error("Training API Error:", error);
    return null;
  }
};

// ------------------------------------------------------------------
// 6. START GUIDANCE CHAT (Initialize Coach Session)
// ------------------------------------------------------------------
export const startGuidanceChat = async (sessionId, language = "en") => {
  const START_ENDPOINT = `${API_BASE_URL}/api/chat/start`;
  
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("language", language);

  try {
    const response = await fetch(START_ENDPOINT, { method: "POST", body: formData });
    if (!response.ok) throw new Error("Failed to start AI Guide session");
    
    const data = await response.json();
    const aiAudioUrl = data.audio ? `data:audio/mpeg;base64,${data.audio}` : null;
    
    return { text: data.greeting, audioUrl: aiAudioUrl };
  } catch (error) {
    console.error("Chat Init Error:", error);
    return { error: "Failed to connect to AI Guide." };
  }
};

// ------------------------------------------------------------------
// 7. SEND AUDIO TO GUIDANCE CHAT (Ongoing Coach Conversation)
// ------------------------------------------------------------------
export const sendAudioToGuidanceChat = async (audioBlob, sessionId, language = "en") => {
  const CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;
  
  const formData = new FormData();
  const extension = audioBlob?.type?.includes("mp4") ? "m4a" : "webm";
  
  formData.append("audio", audioBlob, `chat_audio.${extension}`);
  formData.append("session_id", sessionId);
  formData.append("language", language);

  try {
    const response = await fetch(CHAT_ENDPOINT, { method: "POST", body: formData });
    if (!response.ok) throw new Error("Failed to connect to AI Guide");
    
    const data = await response.json();
    const aiAudioUrl = data.audio ? `data:audio/mpeg;base64,${data.audio}` : null;
    
    return { text: data.reply, audioUrl: aiAudioUrl };
  } catch (error) {
    console.error("Chat API Error:", error);
    return { error: "Failed to connect to AI Guide." };
  }
};