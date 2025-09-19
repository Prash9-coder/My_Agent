import React, { useState, useEffect } from 'react';
import { useWebSpeechRecognition, useEnhancedTextToSpeech } from '../hooks/useWebSpeechAPI';

const VoiceInteraction = ({ onTranscriptReceived, onError, disabled = false }) => {
  const {
    isListening,
    transcript,
    interimTranscript,
    error: speechError,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  } = useWebSpeechRecognition();

  const {
    isSpeaking,
    error: ttsError,
    speak,
    stopSpeaking,
  } = useEnhancedTextToSpeech();

  const [language, setLanguage] = useState('en-US');

  // Handle transcript changes
  useEffect(() => {
    if (transcript && onTranscriptReceived) {
      onTranscriptReceived(transcript);
      resetTranscript();
    }
  }, [transcript, onTranscriptReceived, resetTranscript]);

  // Handle errors
  useEffect(() => {
    const error = speechError || ttsError;
    if (error && onError) {
      onError(error);
    }
  }, [speechError, ttsError, onError]);

  const handleStartListening = () => {
    if (!isSupported) {
      onError && onError('Speech recognition not supported in this browser');
      return;
    }
    startListening(language);
  };

  const handleStopListening = () => {
    stopListening();
  };

  const speakText = (text, languageCode = language) => {
    speak(text, { languageCode, rate: 0.8, useBackend: true });
  };

  if (!isSupported) {
    return (
      <div className="voice-interaction bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center text-red-600">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">Voice features not available</span>
        </div>
        <p className="text-sm text-red-500 mt-1">
          Please use Chrome, Edge, or Safari for voice recognition features.
        </p>
      </div>
    );
  }

  return (
    <div className="voice-interaction">
      {/* Voice Control Panel */}
      <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg border">
        {/* Microphone Button */}
        <button
          onClick={isListening ? handleStopListening : handleStartListening}
          disabled={disabled || isSpeaking}
          className={`
            flex items-center justify-center w-12 h-12 rounded-full transition-all duration-200
            ${isListening 
              ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
              : 'bg-blue-500 hover:bg-blue-600 text-white'
            }
            ${(disabled || isSpeaking) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
          title={isListening ? 'Stop listening' : 'Start voice input'}
        >
          {isListening ? (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
          )}
        </button>

        {/* Status and Controls */}
        <div className="flex-1">
          {/* Language Selector */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isListening || isSpeaking}
            className="text-xs border border-gray-300 rounded px-2 py-1 mb-1"
          >
            <option value="en-US">English (US)</option>
            <option value="en-IN">English (India)</option>
            <option value="te-IN">Telugu</option>
          </select>

          {/* Status Display */}
          <div className="text-sm">
            {isListening && (
              <div className="flex items-center text-blue-600">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-2"></div>
                <span>Listening... {interimTranscript && `"${interimTranscript}"`}</span>
              </div>
            )}
            
            {isSpeaking && (
              <div className="flex items-center text-green-600">
                <svg className="w-4 h-4 mr-2 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.813L4.146 13.146a1 1 0 00-.707-.293H2a1 1 0 01-1-1V8a1 1 0 011-1h1.439a1 1 0 00.707-.293l4.237-3.667a1 1 0 011.617.813zM11 5.414V8a1 1 0 102 0V5.414a2 2 0 00-2 0z" clipRule="evenodd" />
                </svg>
                <span>Speaking...</span>
              </div>
            )}

            {!isListening && !isSpeaking && (
              <span className="text-gray-500">
                Click microphone to start voice input
              </span>
            )}
          </div>
        </div>

        {/* Stop Speaking Button */}
        {isSpeaking && (
          <button
            onClick={stopSpeaking}
            className="p-2 text-gray-600 hover:text-gray-800 rounded-full hover:bg-gray-200"
            title="Stop speaking"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>

      {/* Voice Feedback Display */}
      {interimTranscript && (
        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-sm">
          <span className="text-blue-600">Hearing: </span>
          <span className="italic text-gray-700">"{interimTranscript}"</span>
        </div>
      )}

      {/* Error Display */}
      {(speechError || ttsError) && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm">
          <div className="flex items-center text-red-600">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{speechError || ttsError}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceInteraction;

// Export utility function for speaking text from other components
export const useSpeakText = () => {
  const { speak, isSpeaking, stopSpeaking } = useEnhancedTextToSpeech();
  
  return {
    speakText: (text, options = {}) => {
      speak(text, {
        languageCode: 'en-US',
        rate: 0.8,
        useBackend: true,
        ...options
      });
    },
    isSpeaking,
    stopSpeaking,
  };
};