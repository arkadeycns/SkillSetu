// frontend/src/api/aiService.js

export const sendAudioToAI = async (audioBlob) => {
  const formData = new FormData();
  formData.append("audio", audioBlob, "interview_audio.webm");

  try {
    const response = await fetch("http://localhost:8000/api/assessment/assess-voice", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    const aiResponseBlob = await response.blob();
    
    const aiAudioUrl = URL.createObjectURL(aiResponseBlob);
    return aiAudioUrl;
    
  } catch (error) {
    console.error("API Error connecting to Backend:", error);
    return null;
  }
};