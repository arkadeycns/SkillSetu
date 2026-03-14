// src/api/aiService.js

export const sendAudioToAI = async (audioBlob) => {
  const formData = new FormData();
  formData.append("audio", audioBlob, "interview_audio.webm");

  try {
    const response = await fetch("http://localhost:8000/api/assess-voice", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Backend processing failed");

    const aiResponseBlob = await response.blob();
    
    const aiAudioUrl = URL.createObjectURL(aiResponseBlob);
    return aiAudioUrl;
    
  } catch (error) {
    console.error("API Error:", error);
    return null;
  }
};