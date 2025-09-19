import React, { useState } from 'react';
import { RefreshCw, Volume2, BookOpen, Star, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { useTextToSpeech } from '../hooks/useSpeechRecognition';

const VocabularyPanel = ({ dailyVocabulary, onRefresh }) => {
  const [expandedWords, setExpandedWords] = useState(new Set());
  const { speak, isSpeaking, stopSpeaking } = useTextToSpeech();

  const toggleWordExpansion = (wordIndex) => {
    const newExpanded = new Set(expandedWords);
    if (newExpanded.has(wordIndex)) {
      newExpanded.delete(wordIndex);
    } else {
      newExpanded.add(wordIndex);
    }
    setExpandedWords(newExpanded);
  };

  const handleSpeak = (word, pronunciation = null) => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      // Speak the word with pronunciation guide
      const textToSpeak = pronunciation ? `${word}. Pronunciation: ${pronunciation}` : word;
      speak(textToSpeak);
    }
  };

  const getPartOfSpeechColor = (partOfSpeech) => {
    switch (partOfSpeech?.toLowerCase()) {
      case 'noun':
        return 'bg-blue-100 text-blue-800';
      case 'verb':
        return 'bg-green-100 text-green-800';
      case 'adjective':
        return 'bg-purple-100 text-purple-800';
      case 'adverb':
        return 'bg-orange-100 text-orange-800';
      case 'preposition':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!dailyVocabulary) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-600 mb-2">No Vocabulary Loaded</h2>
          <p className="text-gray-500 mb-4">Click refresh to load today's vocabulary words</p>
          <button
            onClick={onRefresh}
            className="btn-primary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Load Vocabulary</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Daily Vocabulary</h1>
            <p className="text-gray-600 telugu-text">రోజువారీ వచనం</p>
            <div className="flex items-center space-x-4 mt-3">
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>{dailyVocabulary.date}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-primary-600">
                <Star className="w-4 h-4" />
                <span>Theme: {dailyVocabulary.theme}</span>
              </div>
            </div>
          </div>
          <button
            onClick={onRefresh}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="card p-6 text-center">
            <div className="text-2xl font-bold text-primary-600 mb-2">
              {dailyVocabulary.words?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Words to Learn Today</div>
          </div>
          
          <div className="card p-6 text-center">
            <div className="text-2xl font-bold text-green-600 mb-2">
              {dailyVocabulary.words?.filter(word => word.part_of_speech === 'noun').length || 0}
            </div>
            <div className="text-sm text-gray-600">Nouns</div>
          </div>
          
          <div className="card p-6 text-center">
            <div className="text-2xl font-bold text-purple-600 mb-2">
              {dailyVocabulary.words?.filter(word => word.part_of_speech === 'verb').length || 0}
            </div>
            <div className="text-sm text-gray-600">Verbs</div>
          </div>
        </div>

        {/* Vocabulary Words */}
        <div className="space-y-4">
          {dailyVocabulary.words?.map((word, index) => (
            <div key={index} className="card transition-all duration-200">
              <div className="p-6">
                {/* Word Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <h3 className="text-2xl font-bold text-gray-900">{word.word}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPartOfSpeechColor(word.part_of_speech)}`}>
                      {word.part_of_speech}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleSpeak(word.word, word.pronunciation)}
                      className="p-2 text-gray-500 hover:text-primary-600 transition-colors rounded-full hover:bg-primary-50"
                      title="Pronounce word"
                    >
                      <Volume2 className="w-5 h-5" />
                    </button>
                    
                    <button
                      onClick={() => toggleWordExpansion(index)}
                      className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
                    >
                      {expandedWords.has(index) ? (
                        <ChevronUp className="w-5 h-5" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Telugu Meaning</p>
                    <p className="text-lg font-medium telugu-text text-gray-900">{word.meaning_telugu}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Pronunciation</p>
                    <p className="text-lg font-mono text-gray-700">{word.pronunciation}</p>
                  </div>
                </div>

                {/* Quick Examples */}
                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-2">Quick Example</p>
                  {word.examples && word.examples.length > 0 && (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-gray-800 mb-1">{word.examples[0].english}</p>
                      <p className="text-sm telugu-text text-gray-600">{word.examples[0].telugu}</p>
                    </div>
                  )}
                </div>

                {/* Expanded Content */}
                {expandedWords.has(index) && (
                  <div className="border-t border-gray-200 pt-4 animate-slide-up">
                    {/* All Examples */}
                    {word.examples && word.examples.length > 1 && (
                      <div className="mb-6">
                        <h4 className="text-lg font-semibold text-gray-900 mb-3">More Examples</h4>
                        <div className="space-y-3">
                          {word.examples.slice(1).map((example, exIndex) => (
                            <div key={exIndex} className="bg-blue-50 rounded-lg p-4">
                              <div className="flex items-center justify-between mb-2">
                                <p className="text-gray-800 font-medium">{example.english}</p>
                                <button
                                  onClick={() => handleSpeak(example.english)}
                                  className="text-blue-600 hover:text-blue-800 transition-colors"
                                  title="Pronounce example"
                                >
                                  <Volume2 className="w-4 h-4" />
                                </button>
                              </div>
                              <p className="text-sm telugu-text text-gray-600">{example.telugu}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Usage Tips */}
                    <div className="bg-yellow-50 rounded-lg p-4">
                      <h4 className="text-sm font-semibold text-yellow-800 mb-2">💡 Usage Tips</h4>
                      <div className="space-y-2 text-sm text-yellow-700">
                        <p>• Try using this word in your next conversation</p>
                        <p>• Practice pronouncing it slowly: {word.pronunciation}</p>
                        <p>• Remember: It's a {word.part_of_speech}</p>
                        <p className="telugu-text">• అర్థం: {word.meaning_telugu}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Practice Suggestion */}
        <div className="card p-6 mt-8 bg-gradient-to-r from-primary-50 to-blue-50">
          <div className="flex items-center space-x-4">
            <div className="bg-primary-100 rounded-full p-3">
              <BookOpen className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Practice Challenge</h3>
              <p className="text-gray-700">
                Try to use all these words in a conversation today! Go to the Chat section and practice.
              </p>
              <p className="text-sm telugu-text text-gray-600 mt-1">
                ఈ రోజు ఈ పదాలన్నింటినీ సంభాషణలో వాడటానికి ప్రయత్నించండి!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VocabularyPanel;