import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Web Speech API Hook for Speech-to-Text
 * Uses browser's built-in speech recognition (no server processing needed)
 */
export const useWebSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef('');

  // Initialize Web Speech API
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        setIsSupported(true);
        recognitionRef.current = new SpeechRecognition();
        
        // Configure recognition
        const recognition = recognitionRef.current;
        recognition.continuous = false; // Stop after user stops speaking
        recognition.interimResults = true; // Show interim results while speaking
        recognition.maxAlternatives = 1;
        recognition.lang = 'en-US'; // Default language
        
        // Event handlers
        recognition.onstart = () => {
          setIsListening(true);
          setError(null);
          console.log('🎤 Voice recognition started');
        };
        
        recognition.onend = () => {
          setIsListening(false);
          console.log('🎤 Voice recognition ended');
        };
        
        recognition.onresult = (event) => {
          let interimTranscript = '';
          let finalTranscript = finalTranscriptRef.current;
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
              console.log('✅ Final transcript:', transcript);
            } else {
              interimTranscript += transcript;
            }
          }
          
          finalTranscriptRef.current = finalTranscript;
          setTranscript(finalTranscript);
          setInterimTranscript(interimTranscript);
        };
        
        recognition.onerror = (event) => {
          console.error('❌ Speech recognition error:', event.error);
          setError(event.error);
          setIsListening(false);
          
          // Provide user-friendly error messages
          switch (event.error) {
            case 'no-speech':
              setError('No speech detected. Please try again.');
              break;
            case 'audio-capture':
              setError('Microphone access denied or not available.');
              break;
            case 'not-allowed':
              setError('Microphone permission denied. Please allow microphone access.');
              break;
            case 'network':
              setError('Network error. Please check your internet connection.');
              break;
            default:
              setError(`Speech recognition error: ${event.error}`);
          }
        };
        
        recognition.onnomatch = () => {
          console.warn('⚠️ No recognition match found');
          setError('Could not understand the speech. Please try again.');
        };
      } else {
        setIsSupported(false);
        setError('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      }
    }
  }, []);

  const startListening = useCallback((language = 'en-US') => {
    if (!isSupported) {
      setError('Speech recognition not supported');
      return;
    }

    if (isListening) {
      console.warn('Already listening...');
      return;
    }

    try {
      // Reset previous results
      finalTranscriptRef.current = '';
      setTranscript('');
      setInterimTranscript('');
      setError(null);
      
      // Set language
      if (recognitionRef.current) {
        recognitionRef.current.lang = language;
        recognitionRef.current.start();
      }
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      setError('Failed to start speech recognition');
    }
  }, [isSupported, isListening]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  const resetTranscript = useCallback(() => {
    finalTranscriptRef.current = '';
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  };
};

/**
 * Enhanced TTS Hook using both backend (gTTS) and browser fallback
 */
export const useEnhancedTextToSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  const speak = useCallback(async (text, options = {}) => {
    const {
      languageCode = 'en-US',
      rate = 0.8,
      pitch = 1.0,
      volume = 1.0,
      useBackend = true
    } = options;

    try {
      setIsSpeaking(true);
      setError(null);

      // Try backend TTS first (gTTS)
      if (useBackend) {
        try {
          const response = await fetch('/api/text-to-speech', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: text,
              language_code: languageCode
            })
          });

          if (response.ok) {
            const result = await response.json();
            
            if (result.audio_content) {
              // Play backend-generated audio
              const audioBlob = new Blob(
                [Uint8Array.from(atob(result.audio_content), c => c.charCodeAt(0))],
                { type: 'audio/mp3' }
              );
              
              const audioUrl = URL.createObjectURL(audioBlob);
              const audio = new Audio(audioUrl);
              audioRef.current = audio;

              audio.onended = () => {
                setIsSpeaking(false);
                URL.revokeObjectURL(audioUrl);
              };

              audio.onerror = () => {
                setIsSpeaking(false);
                URL.revokeObjectURL(audioUrl);
                throw new Error('Failed to play backend audio');
              };

              await audio.play();
              return; // Success with backend TTS
            }
          }
        } catch (backendError) {
          console.warn('Backend TTS failed, using browser fallback:', backendError);
        }
      }

      // Fallback to browser Speech Synthesis API
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = languageCode;
        utterance.rate = rate;
        utterance.pitch = pitch;
        utterance.volume = volume;
        
        utterance.onstart = () => {
          console.log('🔊 Browser TTS started');
        };
        
        utterance.onend = () => {
          setIsSpeaking(false);
          console.log('🔊 Browser TTS ended');
        };
        
        utterance.onerror = (event) => {
          setIsSpeaking(false);
          setError(`TTS Error: ${event.error}`);
          console.error('Browser TTS error:', event.error);
        };
        
        // Get available voices for better quality
        const voices = speechSynthesis.getVoices();
        const preferredVoice = voices.find(voice => 
          voice.lang.startsWith(languageCode.substring(0, 2)) && voice.name.includes('Google')
        ) || voices.find(voice => voice.lang.startsWith(languageCode.substring(0, 2)));
        
        if (preferredVoice) {
          utterance.voice = preferredVoice;
        }
        
        speechSynthesis.speak(utterance);
      } else {
        throw new Error('Text-to-speech not supported in this browser');
      }
      
    } catch (error) {
      console.error('TTS Error:', error);
      setError(error.message);
      setIsSpeaking(false);
    }
  }, []);

  const stopSpeaking = useCallback(() => {
    // Stop backend audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    
    // Stop browser TTS
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }
    
    setIsSpeaking(false);
  }, []);

  const getAvailableVoices = useCallback(() => {
    if ('speechSynthesis' in window) {
      return speechSynthesis.getVoices();
    }
    return [];
  }, []);

  return {
    isSpeaking,
    error,
    speak,
    stopSpeaking,
    getAvailableVoices,
  };
};

/**
 * Combined Speech Hook for complete voice interaction
 */
export const useVoiceInteraction = () => {
  const speechRecognition = useWebSpeechRecognition();
  const textToSpeech = useEnhancedTextToSpeech();
  
  const [isVoiceMode, setIsVoiceMode] = useState(false);

  const startVoiceConversation = useCallback(() => {
    setIsVoiceMode(true);
    speechRecognition.startListening();
  }, [speechRecognition]);

  const endVoiceConversation = useCallback(() => {
    setIsVoiceMode(false);
    speechRecognition.stopListening();
    textToSpeech.stopSpeaking();
  }, [speechRecognition, textToSpeech]);

  const processVoiceMessage = useCallback(async (transcript) => {
    // This can be connected to the chat API
    console.log('Processing voice message:', transcript);
    return transcript;
  }, []);

  return {
    ...speechRecognition,
    ...textToSpeech,
    isVoiceMode,
    startVoiceConversation,
    endVoiceConversation,
    processVoiceMessage,
  };
};