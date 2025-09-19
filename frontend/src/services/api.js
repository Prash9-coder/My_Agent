import axios from 'axios';

// Create axios instance with base configuration
// In Replit, use relative URLs for same-domain backend communication
const baseURL = import.meta.env.VITE_API_URL || (
  window.location.origin.includes('replit') 
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : 'http://localhost:8000'
);

const api = axios.create({
  baseURL: baseURL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add any authentication headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API endpoints
export const apiService = {
  // Chat endpoints
  async sendMessage(message, studentId, isVoice = false) {
    const response = await api.post('/api/chat', {
      message,
      student_id: studentId,
      is_voice: isVoice,
    });
    return response.data;
  },

  // Speech services
  async speechToText(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.webm');
    
    const response = await api.post('/api/speech-to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async textToSpeech(text, languageCode = 'en-US') {
    const response = await api.post('/api/text-to-speech', {
      text,
      language_code: languageCode,
    });
    return response.data;
  },

  // Student progress
  async getStudentProgress(studentId) {
    const response = await api.get(`/api/student/${studentId}/progress`);
    return response.data;
  },

  async getCommonMistakes(studentId) {
    const response = await api.get(`/api/student/${studentId}/mistakes`);
    return response.data;
  },

  // Lessons and exercises
  async getPersonalizedLesson(studentId, lessonType, duration = 15) {
    const response = await api.post(`/api/student/${studentId}/lesson`, {
      lesson_type: lessonType,
      duration_minutes: duration,
    });
    return response.data;
  },

  async generateExercise(studentId, exerciseType, difficulty) {
    const response = await api.post(`/api/student/${studentId}/exercise`, {
      exercise_type: exerciseType,
      difficulty,
    });
    return response.data;
  },

  // Vocabulary
  async getDailyVocabulary() {
    const response = await api.get('/api/vocabulary/daily');
    return response.data;
  },

  // Translation
  async translateText(text, sourceLanguage, targetLanguage) {
    const response = await api.post('/api/translate', {
      text,
      source_language: sourceLanguage,
      target_language: targetLanguage,
    });
    return response.data;
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/');
    return response.data;
  },
};

export default api;