// src/pages/AIInterview.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Mic, Square, Loader2, User, Bot, Trash2, Send } from 'lucide-react';
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';
import { sendAudioToAI } from '../api/aiService';

export default function AIInterview() {
  const { isRecording, startRecording, stopRecording } = useVoiceRecorder();
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // NEW STATES: To hold the audio for review before sending
  const [stagedAudioBlob, setStagedAudioBlob] = useState(null);
  const [stagedAudioUrl, setStagedAudioUrl] = useState(null);
  
  const chatEndRef = useRef(null);

  // Initial greeting
  useEffect(() => {
    setMessages([
      { 
        sender: 'ai', 
        text: "Namaste! Main apka AI mentor hoon. T-Joint banane ke steps detail mein batayein.", 
        audioUrl: null // If you have a static intro mp3, you can add the URL here later!
      }
    ]);
  }, []);

  // Auto-scroll to the bottom when new messages or previews appear
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isProcessing, stagedAudioUrl]);

  // 1. Handle Recording (Start / Stop and Stage)
  const handleRecordToggle = async () => {
    if (isRecording) {
      const audioBlob = await stopRecording();
      if (!audioBlob) return;

      // Stage the audio for review instead of sending immediately
      setStagedAudioBlob(audioBlob);
      setStagedAudioUrl(URL.createObjectURL(audioBlob));
    } else {
      await startRecording();
    }
  };

  // 2. Handle Canceling the Audio
  const handleCancelAudio = () => {
    setStagedAudioBlob(null);
    setStagedAudioUrl(null);
  };

  // 3. Handle Sending the Audio
  const handleSendAudio = async () => {
    if (!stagedAudioBlob) return;

    // Add user's audio to the chat visually
    setMessages(prev => [...prev, { sender: 'user', audioUrl: stagedAudioUrl }]);
    
    // Save the blob to send and clear the staging area immediately
    const blobToSend = stagedAudioBlob;
    setStagedAudioBlob(null);
    setStagedAudioUrl(null);
    
    // Send to backend
    setIsProcessing(true);
    const aiResponseAudioUrl = await sendAudioToAI(blobToSend);
    setIsProcessing(false);

    // Add AI response to the chat
    if (aiResponseAudioUrl) {
      setMessages(prev => [...prev, { sender: 'ai', audioUrl: aiResponseAudioUrl }]);
    } else {
      alert("Network error. Could not reach the AI.");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white shadow-sm p-4 text-center">
        <h1 className="text-xl font-bold text-gray-800">Practical Skill Assessment</h1>
        <p className="text-sm text-gray-500">Speak naturally in your own language</p>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            
            {/* AI Avatar */}
            {msg.sender === 'ai' && (
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3 flex-shrink-0">
                <Bot className="text-blue-600" size={20} />
              </div>
            )}

            {/* Chat Bubble */}
            <div className={`max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm'
            }`}>
              
              {/* Text rendering */}
              {msg.text && <p className="mb-2">{msg.text}</p>}
              
              {/* Playable Audio in Chat */}
              {msg.audioUrl && (
                <audio 
                  src={msg.audioUrl} 
                  controls 
                  // Only auto-play if it's a brand new message from the AI
                  autoPlay={msg.sender === 'ai' && index === messages.length - 1}
                  className="h-10 w-full rounded-md"
                />
              )}
            </div>

            {/* User Avatar */}
            {msg.sender === 'user' && (
              <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center ml-3 flex-shrink-0">
                <User className="text-gray-600" size={20} />
              </div>
            )}
          </div>
        ))}

        {/* Loading Indicator */}
        {isProcessing && (
          <div className="flex justify-start items-center space-x-2 text-gray-500">
            <Loader2 className="animate-spin" size={20} />
            <span className="text-sm animate-pulse">AI is analyzing your response...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Action Bar (Mic / Preview / Send) */}
      <div className="bg-white border-t border-gray-200 p-4 sm:p-6 flex justify-center items-center min-h-[100px]">
        
        {/* If audio is recorded but not sent yet, show PREVIEW bar */}
        {stagedAudioUrl ? (
          <div className="flex items-center gap-3 w-full max-w-md bg-gray-100 p-2 pl-4 rounded-full shadow-inner border border-gray-200">
            <button 
              onClick={handleCancelAudio}
              className="p-2 text-red-500 hover:bg-red-100 rounded-full transition-colors"
              title="Cancel Recording"
            >
              <Trash2 size={24} />
            </button>
            
            <audio src={stagedAudioUrl} controls className="flex-1 h-10" />
            
            <button 
              onClick={handleSendAudio}
              className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors shadow-md"
              title="Send to AI"
            >
              <Send size={20} className="ml-0.5" />
            </button>
          </div>
        ) : (
          /* Otherwise, show the standard MIC button */
          <button 
            onClick={handleRecordToggle}
            disabled={isProcessing}
            className={`relative flex items-center justify-center w-20 h-20 rounded-full transition-all duration-300 shadow-lg ${
              isRecording 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                : 'bg-blue-600 hover:bg-blue-700'
            } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isRecording ? (
              <Square className="text-white fill-current" size={32} />
            ) : (
              <Mic className="text-white" size={36} />
            )}
            
            {/* Ripple effect when recording */}
            {isRecording && (
              <span className="absolute w-full h-full rounded-full border-4 border-red-500 animate-ping opacity-75"></span>
            )}
          </button>
        )}
      </div>
    </div>
  );
}