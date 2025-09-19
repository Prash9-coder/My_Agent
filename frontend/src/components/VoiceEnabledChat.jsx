import React, { useState, useCallback } from 'react';
import VoiceInteraction, { useSpeakText } from './VoiceInteraction';
import { apiService } from '../services/api';

/**
 * Example component showing how to integrate voice features with chat
 * This can be used as a reference or directly integrated into your existing chat component
 */
const VoiceEnabledChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'tutor',
      content: 'Hello! I\'m your AI English tutor. You can type or speak to me. Try saying "Hello, how are you?"',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [studentId] = useState('student_demo_001');

  const { speakText, isSpeaking, stopSpeaking } = useSpeakText();

  // Handle voice input
  const handleVoiceTranscript = useCallback((transcript) => {
    console.log('Voice transcript received:', transcript);
    setInputText(transcript);
    // Auto-send voice messages (optional)
    // sendMessage(transcript, true);
  }, []);

  // Handle voice/speech errors
  const handleVoiceError = useCallback((error) => {
    console.error('Voice error:', error);
    // You can show error notifications here
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'error',
      content: `Voice Error: ${error}`,
      timestamp: new Date()
    }]);
  }, []);

  // Send message to AI tutor
  const sendMessage = useCallback(async (text, isVoice = false) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: text,
      timestamp: new Date(),
      isVoice
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await apiService.chatWithTutor({
        message: text,
        student_id: studentId,
        is_voice: isVoice
      });

      const tutorMessage = {
        id: Date.now() + 1,
        type: 'tutor',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, tutorMessage]);

      // Auto-speak tutor responses (optional)
      if (isVoice && response.encouragement) {
        speakText(response.encouragement, { languageCode: 'en-US' });
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, there was an error processing your message.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  }, [studentId, speakText]);

  // Handle text input submit
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    sendMessage(inputText, false);
  }, [inputText, sendMessage]);

  // Speak any message
  const handleSpeakMessage = useCallback((content) => {
    if (typeof content === 'string') {
      speakText(content);
    } else {
      // Handle complex response object
      const textToSpeak = content.encouragement || 'No content to speak';
      speakText(textToSpeak);
    }
  }, [speakText]);

  return (
    <div className="voice-enabled-chat max-w-4xl mx-auto p-4">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="border-b p-4">
          <h1 className="text-xl font-bold text-gray-800 flex items-center">
            🎤 Voice-Enabled AI English Tutor
            {isSpeaking && <span className="ml-2 text-sm text-green-600 animate-pulse">Speaking...</span>}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            You can type or speak your messages. The tutor can respond with both text and voice.
          </p>
        </div>

        {/* Messages Area */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : message.type === 'error'
                    ? 'bg-red-100 text-red-700 border border-red-300'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {typeof message.content === 'string' ? (
                      <p className="text-sm">{message.content}</p>
                    ) : (
                      // Handle complex tutor response
                      <div>
                        {message.content.encouragement && (
                          <p className="text-sm mb-2">{message.content.encouragement}</p>
                        )}
                        {message.content.corrections && message.content.corrections.length > 0 && (
                          <div className="mt-2 p-2 bg-yellow-50 rounded text-xs">
                            <strong>Corrections:</strong>
                            {message.content.corrections.map((correction, idx) => (
                              <div key={idx} className="mt-1">
                                "{correction.original_text}" → "{correction.corrected_text}"
                                <br />
                                <span className="text-gray-600">{correction.explanation_english}</span>
                              </div>
                            ))}
                          </div>
                        )}
                        {message.content.pronunciation_guide && (
                          <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
                            <strong>🗣️ Pronunciation:</strong> {message.content.pronunciation_guide}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Speak Button for Tutor Messages */}
                  {message.type === 'tutor' && (
                    <button
                      onClick={() => handleSpeakMessage(message.content)}
                      disabled={isSpeaking}
                      className="ml-2 p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                      title="Speak this message"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.813L4.146 13.146a1 1 0 00-.707-.293H2a1 1 0 01-1-1V8a1 1 0 011-1h1.439a1 1 0 00.707-.293l4.237-3.667a1 1 0 011.617.813zM11 5.414V8a1 1 0 102 0V5.414a2 2 0 00-2 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                  )}
                </div>
                
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs opacity-75">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                  {message.isVoice && (
                    <span className="text-xs bg-white bg-opacity-20 px-1 rounded">🎤</span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-gray-600">Tutor is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Voice Interface */}
        <div className="border-t p-4">
          <VoiceInteraction
            onTranscriptReceived={handleVoiceTranscript}
            onError={handleVoiceError}
            disabled={isLoading}
          />
        </div>

        {/* Text Input */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message here... or use voice input above"
              disabled={isLoading}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !inputText.trim()}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
          
          {isSpeaking && (
            <button
              onClick={stopSpeaking}
              className="mt-2 px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
            >
              Stop Speaking
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceEnabledChat;