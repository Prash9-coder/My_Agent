import React, { useState, useEffect } from 'react';
import { TrendingUp, Target, Calendar, Award, AlertTriangle, BookOpen, Clock } from 'lucide-react';
import { apiService } from '../services/api';

const ProgressPanel = ({ studentId, progress }) => {
  const [commonMistakes, setCommonMistakes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (studentId) {
      loadCommonMistakes();
    }
  }, [studentId]);

  const loadCommonMistakes = async () => {
    try {
      setLoading(true);
      const mistakes = await apiService.getCommonMistakes(studentId);
      setCommonMistakes(mistakes);
    } catch (error) {
      console.error('Error loading common mistakes:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getLevelBadgeColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'advanced':
        return 'bg-purple-100 text-purple-800';
      case 'intermediate':
        return 'bg-blue-100 text-blue-800';
      case 'beginner':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getMistakeTypeIcon = (type) => {
    switch (type) {
      case 'grammar':
        return '📝';
      case 'tense':
        return '⏰';
      case 'vocabulary':
        return '📚';
      case 'pronunciation':
        return '🗣️';
      case 'preposition':
        return '🔗';
      default:
        return '❓';
    }
  };

  if (!progress) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your progress...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Learning Progress</h1>
          <p className="text-gray-600 telugu-text">మీ నేర్చుకునే పురోగతి</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Accuracy Card */}
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Accuracy</p>
                <p className={`text-2xl font-bold ${getProgressColor(progress.accuracy_percentage)}`}>
                  {progress.accuracy_percentage.toFixed(1)}%
                </p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <Target className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    progress.accuracy_percentage >= 80 ? 'bg-green-500' : 
                    progress.accuracy_percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${progress.accuracy_percentage}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Total Sentences Card */}
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Sentences Spoken</p>
                <p className="text-2xl font-bold text-gray-900">{progress.total_sentences}</p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <p className="text-sm text-green-600 mt-2">
              {progress.correct_sentences} correct sentences
            </p>
          </div>

          {/* Current Level Card */}
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Level</p>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mt-2 ${getLevelBadgeColor(progress.current_level)}`}>
                  {progress.current_level?.charAt(0).toUpperCase() + progress.current_level?.slice(1)}
                </span>
              </div>
              <div className="bg-purple-100 rounded-full p-3">
                <Award className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          {/* Streak Card */}
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Practice Streak</p>
                <p className="text-2xl font-bold text-gray-900">{progress.streak_days}</p>
                <p className="text-sm text-gray-500">days</p>
              </div>
              <div className="bg-orange-100 rounded-full p-3">
                <Calendar className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Strengths and Weaknesses */}
          <div className="space-y-6">
            {/* Strengths */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Award className="w-5 h-5 text-green-600 mr-2" />
                Your Strengths
              </h2>
              <div className="space-y-3">
                {progress.strengths.map((strength, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                    <span className="text-gray-700">{strength}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Areas for Improvement */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 text-blue-600 mr-2" />
                Areas for Improvement
              </h2>
              <div className="space-y-3">
                {progress.areas_for_improvement.map((area, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <span className="text-gray-700">{area}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Common Mistakes */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
              Common Mistakes
            </h2>

            {loading ? (
              <div className="flex justify-center">
                <div className="spinner w-6 h-6"></div>
              </div>
            ) : commonMistakes.length > 0 ? (
              <div className="space-y-4">
                {commonMistakes.slice(0, 5).map((mistake, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{getMistakeTypeIcon(mistake.mistake_type)}</span>
                        <span className="font-medium text-gray-900 capitalize">
                          {mistake.mistake_type}
                        </span>
                      </div>
                      <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                        {mistake.count} times
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{mistake.description}</p>
                    
                    {mistake.recent_examples.length > 0 && (
                      <div className="bg-gray-50 rounded p-3 mb-3">
                        <p className="text-xs text-gray-500 mb-2">Recent examples:</p>
                        <div className="space-y-1">
                          {mistake.recent_examples.slice(0, 2).map((example, exIndex) => (
                            <p key={exIndex} className="text-sm text-gray-700 italic">
                              "{example}"
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="bg-blue-50 rounded p-3">
                      <p className="text-xs text-blue-600 font-medium mb-1">Suggested Practice:</p>
                      <p className="text-sm text-blue-700">{mistake.suggested_practice}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>No common mistakes found yet.</p>
                <p className="text-sm">Keep practicing to get personalized feedback!</p>
              </div>
            )}
          </div>
        </div>

        {/* Last Activity */}
        <div className="card p-6 mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Clock className="w-5 h-5 text-gray-600 mr-2" />
            Activity Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-600">{progress.total_conversations}</p>
              <p className="text-sm text-gray-600">Total Conversations</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{progress.correct_sentences}</p>
              <p className="text-sm text-gray-600">Correct Sentences</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Last Active</p>
              <p className="font-medium">{new Date(progress.last_activity).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressPanel;