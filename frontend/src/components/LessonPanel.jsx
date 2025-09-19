import React, { useState, useEffect } from 'react';
import { BookOpen, Play, CheckCircle, Clock, Star, ArrowRight, Lightbulb } from 'lucide-react';
import { apiService } from '../services/api';

const LessonPanel = ({ studentId, currentLesson, onLessonChange }) => {
  const [availableLessons, setAvailableLessons] = useState([]);
  const [selectedLessonType, setSelectedLessonType] = useState('grammar');
  const [exercises, setExercises] = useState([]);
  const [currentExercise, setCurrentExercise] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const lessonTypes = [
    { id: 'grammar', name: 'Grammar', icon: '📝', description: 'Learn grammar rules and sentence structure' },
    { id: 'vocabulary', name: 'Vocabulary', icon: '📚', description: 'Expand your word knowledge' },
    { id: 'conversation', name: 'Conversation', icon: '💬', description: 'Practice real-life conversations' },
    { id: 'pronunciation', name: 'Pronunciation', icon: '🗣️', description: 'Improve your speaking skills' },
    { id: 'writing', name: 'Writing', icon: '✍️', description: 'Enhance your writing abilities' },
  ];

  useEffect(() => {
    setAvailableLessons(lessonTypes);
  }, []);

  const startLesson = async (lessonType) => {
    try {
      setLoading(true);
      const lesson = await apiService.getPersonalizedLesson(studentId, lessonType);
      onLessonChange(lesson);
      
      // Generate exercises for this lesson
      const exerciseResponse = await apiService.generateExercise(studentId, 'fill_blanks', 'beginner');
      setExercises(exerciseResponse.exercises || []);
      setCurrentExercise(0);
      setUserAnswers({});
      setShowResults(false);
    } catch (error) {
      console.error('Error starting lesson:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (exerciseId, answer) => {
    setUserAnswers(prev => ({
      ...prev,
      [exerciseId]: answer
    }));
  };

  const submitExercise = () => {
    setShowResults(true);
  };

  const nextExercise = () => {
    if (currentExercise < exercises.length - 1) {
      setCurrentExercise(currentExercise + 1);
      setShowResults(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const calculateScore = () => {
    const currentEx = exercises[currentExercise];
    if (!currentEx) return 0;
    
    const userAnswer = userAnswers[currentEx.exercise_id];
    return userAnswer === currentEx.correct_answer ? 100 : 0;
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (currentLesson && exercises.length > 0) {
    const currentEx = exercises[currentExercise];
    const score = calculateScore();
    
    return (
      <div className="flex-1 overflow-y-auto bg-gray-50">
        <div className="max-w-4xl mx-auto p-6">
          {/* Lesson Header */}
          <div className="card p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{currentLesson.content.title}</h1>
                <div className="flex items-center space-x-4 mt-2">
                  <span className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium">
                    {currentLesson.lesson_type}
                  </span>
                  <div className="flex items-center space-x-1 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>{currentLesson.estimated_duration} minutes</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => onLessonChange(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ← Back to Lessons
              </button>
            </div>

            {/* Lesson Content */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Explanation</h3>
                <p className="text-gray-700 mb-3">{currentLesson.content.explanation_english}</p>
                <p className="text-sm telugu-text text-gray-600">{currentLesson.content.explanation_telugu}</p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-3">Key Points</h3>
                <ul className="space-y-2">
                  {currentLesson.content.key_points.map((point, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Star className="w-4 h-4 text-yellow-500 mt-0.5" />
                      <span className="text-gray-700">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Examples */}
            {currentLesson.content.examples && currentLesson.content.examples.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3">Examples</h3>
                <div className="space-y-3">
                  {currentLesson.content.examples.map((example, index) => (
                    <div key={index} className="bg-blue-50 rounded-lg p-3">
                      <p className="text-gray-800">{example.english}</p>
                      <p className="text-sm telugu-text text-gray-600">{example.telugu}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Exercise Section */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Practice Exercise</h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  Question {currentExercise + 1} of {exercises.length}
                </span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentExercise + 1) / exercises.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Current Exercise */}
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-4">{currentEx.question}</h3>
              
              {currentEx.options ? (
                <div className="space-y-3">
                  {currentEx.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerChange(currentEx.exercise_id, option)}
                      className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                        userAnswers[currentEx.exercise_id] === option
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              ) : (
                <input
                  type="text"
                  value={userAnswers[currentEx.exercise_id] || ''}
                  onChange={(e) => handleAnswerChange(currentEx.exercise_id, e.target.value)}
                  className="input-field"
                  placeholder="Type your answer here..."
                />
              )}
            </div>

            {/* Results */}
            {showResults && (
              <div className={`mb-6 p-4 rounded-lg ${score === 100 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                <div className="flex items-center space-x-2 mb-3">
                  <CheckCircle className={`w-5 h-5 ${score === 100 ? 'text-green-600' : 'text-red-600'}`} />
                  <span className={`font-semibold ${getScoreColor(score)}`}>
                    {score === 100 ? 'Correct!' : 'Incorrect'}
                  </span>
                </div>
                
                {score !== 100 && (
                  <div className="mb-3">
                    <p className="text-sm text-gray-700">
                      <strong>Correct answer:</strong> {currentEx.correct_answer}
                    </p>
                  </div>
                )}
                
                <div className="bg-white rounded p-3">
                  <div className="flex items-start space-x-2">
                    <Lightbulb className="w-4 h-4 text-yellow-600 mt-0.5" />
                    <p className="text-sm text-gray-700">{currentEx.explanation}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-between">
              <button
                onClick={() => onLessonChange(null)}
                className="btn-secondary"
              >
                Back to Lessons
              </button>
              
              <div className="space-x-3">
                {!showResults ? (
                  <button
                    onClick={submitExercise}
                    disabled={!userAnswers[currentEx.exercise_id]}
                    className="btn-primary"
                  >
                    Submit Answer
                  </button>
                ) : currentExercise < exercises.length - 1 ? (
                  <button
                    onClick={nextExercise}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <span>Next Question</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => onLessonChange(null)}
                    className="btn-primary"
                  >
                    Complete Lesson
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Lesson Selection View
  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Choose a Lesson</h1>
          <p className="text-gray-600 telugu-text">పాఠం ఎంచుకోండి</p>
        </div>

        {/* Lesson Categories */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableLessons.map((lesson) => (
            <div key={lesson.id} className="card transition-all duration-200 hover:shadow-xl">
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <span className="text-3xl">{lesson.icon}</span>
                  <h3 className="text-xl font-semibold text-gray-900">{lesson.name}</h3>
                </div>
                
                <p className="text-gray-600 mb-6">{lesson.description}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>15-20 minutes</span>
                  </div>
                  
                  <button
                    onClick={() => startLesson(lesson.id)}
                    className="btn-primary flex items-center space-x-2"
                    disabled={loading}
                  >
                    <Play className="w-4 h-4" />
                    <span>Start</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recommendation */}
        <div className="card p-6 mt-8 bg-gradient-to-r from-primary-50 to-blue-50">
          <div className="flex items-center space-x-4">
            <div className="bg-primary-100 rounded-full p-3">
              <Lightbulb className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Recommended for You</h3>
              <p className="text-gray-700">
                Based on your progress, we recommend starting with <strong>Grammar</strong> lessons 
                to build a strong foundation.
              </p>
              <p className="text-sm telugu-text text-gray-600 mt-1">
                మీ పురోగతి ఆధారంగా, మంచి పునాది నిర్మించడానికి గ్రామర్ పాఠాలతో ప్రారంభించాలని సిఫార్సు చేస్తున్నాము.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LessonPanel;