import React, { useState, useRef } from "react";
import { sendAudioToGuidanceChat } from "../api/aiService";

const AIInterview = ({ sessionId, language = "English", skill = "" }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState([]);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  //  START RECORDING
  const handleStartRecording = async () => {
    try {
      console.log("🎤 Start Recording");

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = handleStopRecording;

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Mic error:", err);
    }
  };

  const handleStopRecording = async () => {
    try {
      console.log(" Stop Recording");

      const audioBlob = new Blob(audioChunksRef.current, {
        type: "audio/webm",
      });

      console.log("Audio Blob:", audioBlob);
      console.log("Session ID:", sessionId);

      if (!audioBlob || audioBlob.size === 0) {
        console.error("Empty audio blob ");
        return;
      }

      //  Add user message
      setMessages((prev) => [
        ...prev,
        { sender: "user", audio: URL.createObjectURL(audioBlob) },
      ]);

      //  CALL API
      const response = await sendAudioToGuidanceChat(
        audioBlob,
        sessionId,
        language,
        skill,
      );

      console.log("AI RESPONSE:", response);

      if (response.error) {
        alert("AI is having trouble connecting.");
        return;
      }

      //  Add AI response
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: response.text,
          audio: response.audioUrl,
        },
      ]);
    } catch (err) {
      console.error("Error sending audio:", err);
    } finally {
      setIsRecording(false);
    }
  };

  // TOGGLE BUTTON
  const handleMicClick = () => {
    if (isRecording) {
      mediaRecorderRef.current.stop();
    } else {
      handleStartRecording();
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>AI Career Coach 🎯</h2>

      {/*  CHAT UI */}
      <div>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            <strong>{msg.sender === "ai" ? "AI" : "You"}:</strong>

            {msg.text && <p>{msg.text}</p>}

            {msg.audio && (
              <audio controls src={msg.audio} style={{ display: "block" }} />
            )}
          </div>
        ))}
      </div>

      {/* MIC BUTTON */}
      <button onClick={handleMicClick} style={{ marginTop: "20px" }}>
        {isRecording ? "Stop 🎤" : "Start 🎤"}
      </button>
    </div>
  );
};

export default AIInterview;
