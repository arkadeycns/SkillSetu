// frontend/src/api/aiService.js

export const sendAudioToAI = async (audioBlob) => {
  const formData = new FormData();
  const extension = audioBlob?.type?.includes("mp4") ? "m4a" : "webm";
  formData.append("audio", audioBlob, `interview_audio.${extension}`);

  try {
    const response = await fetch("http://localhost:8000/api/assessment/assess-voice", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let detail = response.statusText || "Request failed";
      try {
        const errJson = await response.json();
        if (errJson?.detail) detail = errJson.detail;
      } catch (_) {
        // Keep fallback message if response isn't JSON.
      }
      throw new Error(`Backend error: ${detail}`);
    }

    const aiResponseBlob = await response.blob();

    const aiAudioUrl = URL.createObjectURL(aiResponseBlob);
    return aiAudioUrl;

  } catch (error) {
    console.error("API Error connecting to Backend:", error);
    return { error: error?.message || "Unable to process voice response." };
  }
};