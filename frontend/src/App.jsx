import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Volume2, VolumeX, BookOpen, BarChart3, Home, Settings } from 'lucide-react';
import { useSpeechRecognition, useTextToSpeech } from './hooks/useSpeechRecognition';
import { apiService } from './services/api';
import ChatMessage from './components/ChatMessage';
import ProgressPanel from './components/ProgressPanel';
import VocabularyPanel from './components/VocabularyPanel';
import LessonPanel from './components/LessonPanel';
import './App.css';

function App() {
  // State management
  const [currentView, setCurrentView] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [studentId] = useState('student_001'); // In real app, this would come from auth
  const [studentProgress, setStudentProgress] = useState(null);
  const [dailyVocabulary, setDailyVocabulary] = useState(null);
  const [currentLesson, setCurrentLesson] = useState(null);

  // Speech hooks
  const { isRecording, isProcessing, startRecording, stopRecording, cancelRecording } = useSpeechRecognition();
  const { isSpeaking, speak, stopSpeaking } = useTextToSpeech();

  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize app
  useEffect(() => {
    initializeApp();
  }, []);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeApp = async () => {
    try {
      // Add welcome message
      const welcomeMessage = {
        id: Date.now(),
        type: 'tutor',
        content: "Hello! I'm your AI English tutor! 🙋‍♀️\n\nనేను మీ ఇంగ్లీష్ టీచర్! మీరు ఏదైనా ఇంగ్లీష్‌లో చెప్పండి, నేను మిమ్మల్ని సరిదిద్దుతాను మరియు నేర్పుతాను.\n\nYou can type a message or click the microphone to speak!",
        timestamp: new Date(),
        isCorrect: true,
        encouragement: "Ready to start learning? चलो शुरू करते हैं! 🚀"
      };
      
      setMessages([welcomeMessage]);

      // Load student progress
      loadStudentProgress();
      
      // Load daily vocabulary
      loadDailyVocabulary();
      
    } catch (error) {
      console.error('Error initializing app:', error);
    }
  };

  const loadStudentProgress = async () => {
    try {
      const progress = await apiService.getStudentProgress(studentId);
      setStudentProgress(progress);
    } catch (error) {
      console.error('Error loading student progress:', error);
    }
  };

  const loadDailyVocabulary = async () => {
    try {
      const vocabulary = await apiService.getDailyVocabulary();
      setDailyVocabulary(vocabulary);
    } catch (error) {
      console.error('Error loading daily vocabulary:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (message, isVoice = false) => {
    if (!message.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      isVoice
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send message to AI tutor
      const response = await apiService.sendMessage(message, studentId, isVoice);

      // Add tutor response
      const tutorMessage = {
        id: Date.now() + 1,
        type: 'tutor',
        content: formatTutorResponse(response),
        timestamp: new Date(),
        isCorrect: response.is_correct,
        corrections: response.corrections,
        examples: response.examples,
        verbForms: response.verb_forms,
        encouragement: response.encouragement,
        nextSuggestion: response.next_suggestion,
        grammarTip: response.grammar_tip
      };

      setMessages(prev => [...prev, tutorMessage]);

      // Auto-speak tutor response if it's a voice conversation
      if (isVoice && response.encouragement) {
        setTimeout(() => {
          speak(response.encouragement);
        }, 500);
      }

      // Update progress
      loadStudentProgress();

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'tutor',
        content: "Sorry, I couldn't process your message. Please try again.\nక్షమించండి, మీ మెసేజ్ ప్రాసెస్ చేయలేకపోయాను. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        timestamp: new Date(),
        isCorrect: false,
        encouragement: "Don't worry, technical issues happen. Keep practicing! 💪"
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTutorResponse = (response) => {
    let content = '';

    if (response.is_correct) {
      content = `✅ **Perfect!** Your sentence is correct!\n\n${response.encouragement}`;
    } else {
      content = `📝 **Let me help you improve:**\n\n`;
      
      response.corrections.forEach((correction, index) => {
        content += `${index + 1}. **Correction:**\n`;
        content += `   ❌ Original: "${correction.original_text}"\n`;
        content += `   ✅ Correct: "${correction.corrected_text}"\n`;
        content += `   💡 Explanation: ${correction.explanation_english}\n`;
        content += `   🎯 Telugu: ${correction.explanation_telugu}\n\n`;
      });

      content += `🌟 ${response.encouragement}`;
    }

    // Add examples if provided
    if (response.examples && response.examples.length > 0) {
      content += '\n\n**📚 Examples:**\n';
      response.examples.forEach((example, index) => {
        content += `${index + 1}. ${example.english}\n   Telugu: ${example.telugu}\n`;
      });
    }

    // Add verb forms if provided
    if (response.verb_forms) {
      const vf = response.verb_forms;
      content += '\n\n**🔤 Verb Forms:**\n';
      content += `Base: ${vf.base_form} | Past: ${vf.past_simple} | Past Participle: ${vf.past_participle}\n`;
      content += `Present Participle: ${vf.present_participle} | 3rd Person: ${vf.third_person}`;
    }

    // Add next suggestion
    if (response.next_suggestion) {
      content += `\n\n**🎯 Next Practice:** ${response.next_suggestion}`;
    }

    return content;
  };

  const handleVoiceRecording = async () => {
    try {
      if (isRecording) {
        const transcribedText = await stopRecording();
        if (transcribedText) {
          handleSendMessage(transcribedText, true);
        }
      } else {
        await startRecording();
      }
    } catch (error) {
      console.error('Voice recording error:', error);
      alert(error.message);
    }
  };

  const handleSpeakMessage = (message) => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      speak(message.encouragement || message.content);
    }
  };

  const renderMainContent = () => {
    switch (currentView) {
      case 'progress':
        return <ProgressPanel studentId={studentId} progress={studentProgress} />;
      case 'vocabulary':
        return <VocabularyPanel dailyVocabulary={dailyVocabulary} onRefresh={loadDailyVocabulary} />;
      case 'lessons':
        return <LessonPanel studentId={studentId} currentLesson={currentLesson} onLessonChange={setCurrentLesson} />;
      default:
        return (
          <div className="flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onSpeak={() => handleSpeakMessage(message)}
                  isSpeaking={isSpeaking}
                />
              ))}
              {isLoading && (
                <div className="flex justify-center">
                  <div className="spinner w-6 h-6"></div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t bg-white p-4">
              <div className="flex items-center space-x-3 max-w-4xl mx-auto">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputMessage)}
                    placeholder="Type your message in English... / ইংরেজীতে মেসেজ টাইপ করুন..."
                    className="input-field pr-12"
                    disabled={isLoading || isRecording || isProcessing}
                  />
                  {(isRecording || isProcessing) && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-yellow-500'}`}></div>
                    </div>
                  )}
                </div>

                {/* Voice Recording Button */}
                <button
                  onClick={handleVoiceRecording}
                  disabled={isLoading}
                  className={`relative p-3 rounded-full transition-all duration-200 ${
                    isRecording
                      ? 'bg-red-500 text-white recording-pulse'
                      : 'bg-primary-600 hover:bg-primary-700 text-white'
                  } disabled:opacity-50`}
                >
                  {isProcessing ? (
                    <div className="spinner w-5 h-5"></div>
                  ) : isRecording ? (
                    <MicOff className="w-5 h-5" />
                  ) : (
                    <Mic className="w-5 h-5" />
                  )}
                </button>

                {/* Send Button */}
                <button
                  onClick={() => handleSendMessage(inputMessage)}
                  disabled={!inputMessage.trim() || isLoading || isRecording || isProcessing}
                  className="btn-primary p-3"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>

              {/* Recording Status */}
              {isRecording && (
                <div className="text-center mt-2 text-red-600 font-medium">
                  🎤 Recording... Click microphone again to stop
                </div>
              )}
              {isProcessing && (
                <div className="text-center mt-2 text-yellow-600 font-medium">
                  ⏳ Processing your speech...
                </div>
              )}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="max-w-6xl mx-auto h-screen flex">
        {/* Sidebar Navigation */}
        <div className="w-64 bg-white shadow-lg border-r border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-primary-700">AI English Tutor</h1>
            <p className="text-sm text-gray-600 mt-1">మీ ఇంగ్లిష్ టీచర్</p>
          </div>

          <nav className="p-4 space-y-2">
            <button
              onClick={() => setCurrentView('chat')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                currentView === 'chat'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Home className="w-5 h-5" />
              <span>Chat & Practice</span>
            </button>

            <button
              onClick={() => setCurrentView('progress')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                currentView === 'progress'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <BarChart3 className="w-5 h-5" />
              <span>Progress</span>
            </button>

            <button
              onClick={() => setCurrentView('vocabulary')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                currentView === 'vocabulary'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <BookOpen className="w-5 h-5" />
              <span>Vocabulary</span>
            </button>

            <button
              onClick={() => setCurrentView('lessons')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                currentView === 'lessons'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Settings className="w-5 h-5" />
              <span>Lessons</span>
            </button>
          </nav>

          {/* Progress Summary */}
          {studentProgress && (
            <div className="p-4 border-t border-gray-200 mt-auto">
              <div className="bg-primary-50 rounded-lg p-3">
                <h3 className="font-medium text-primary-700 mb-2">Today's Progress</h3>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Accuracy:</span>
                    <span className="font-medium">{studentProgress.accuracy_percentage}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Sentences:</span>
                    <span className="font-medium">{studentProgress.total_sentences}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Level:</span>
                    <span className="font-medium capitalize">{studentProgress.current_level}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {renderMainContent()}
        </div>
      </div>
    </div>
  );
}

export default App;