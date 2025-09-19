import { useState, useRef, useCallback } from 'react';
import { apiService } from '../services/api';

export const useSpeechRecognition = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = useCallback(async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);

    } catch (error) {
      console.error('Error starting recording:', error);
      throw new Error('Could not access microphone. Please check permissions.');
    }
  }, []);

  const stopRecording = useCallback(async () => {
    return new Promise((resolve, reject) => {
      if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
        reject(new Error('No active recording found'));
        return;
      }

      mediaRecorderRef.current.onstop = async () => {
        try {
          setIsRecording(false);
          setIsProcessing(true);

          // Create audio blob from chunks
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          
          // Send to backend for speech-to-text conversion
          const result = await apiService.speechToText(audioBlob);
          
          setIsProcessing(false);
          
          // Stop all audio tracks
          const stream = mediaRecorderRef.current.stream;
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
          }

          resolve(result.text || '');
        } catch (error) {
          setIsProcessing(false);
          console.error('Error processing audio:', error);
          reject(new Error('Failed to convert speech to text'));
        }
      };

      mediaRecorderRef.current.stop();
    });
  }, []);

  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      
      // Stop all audio tracks
      const stream = mediaRecorderRef.current.stream;
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    }
    
    setIsRecording(false);
    setIsProcessing(false);
    audioChunksRef.current = [];
  }, []);

  return {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording,
    cancelRecording,
  };
};

export const useTextToSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const audioRef = useRef(null);

  const speak = useCallback(async (text, languageCode = 'en-US') => {
    try {
      setIsSpeaking(true);

      // Get audio from backend
      const result = await apiService.textToSpeech(text, languageCode);
      
      if (result.audio_content) {
        // Create audio element and play
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
          console.error('Error playing audio');
        };

        await audio.play();
      } else {
        // Fallback to browser TTS if backend doesn't provide audio
        if ('speechSynthesis' in window) {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = languageCode;
          utterance.rate = 0.8; // Slower for learning
          
          utterance.onend = () => setIsSpeaking(false);
          utterance.onerror = () => setIsSpeaking(false);
          
          speechSynthesis.speak(utterance);
        } else {
          setIsSpeaking(false);
        }
      }
    } catch (error) {
      console.error('Error with text-to-speech:', error);
      setIsSpeaking(false);
      
      // Fallback to browser TTS
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = languageCode;
        utterance.rate = 0.8;
        utterance.onend = () => setIsSpeaking(false);
        speechSynthesis.speak(utterance);
      }
    }
  }, []);

  const stopSpeaking = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }
    
    setIsSpeaking(false);
  }, []);

  return {
    isSpeaking,
    speak,
    stopSpeaking,
  };
};