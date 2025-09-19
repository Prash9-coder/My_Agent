import React from 'react';
import { Volume2, VolumeX, User, GraduationCap, CheckCircle, AlertCircle } from 'lucide-react';

const ChatMessage = ({ message, onSpeak, isSpeaking }) => {
  const isUser = message.type === 'user';

  const formatContent = (content) => {
    // Convert markdown-like formatting to JSX
    return content.split('\n').map((line, index) => {
      // Handle bold text
      line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Handle emoji and special formatting
      if (line.startsWith('✅') || line.startsWith('❌') || line.startsWith('💡')) {
        return (
          <div key={index} className="flex items-start space-x-2 mb-2">
            <span dangerouslySetInnerHTML={{ __html: line }} />
          </div>
        );
      }
      
      return line ? (
        <div key={index} dangerouslySetInnerHTML={{ __html: line }} className="mb-1" />
      ) : (
        <br key={index} />
      );
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`flex max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? 'flex-row-reverse' : 'flex-row'} space-x-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-500 ml-3' : 'bg-green-500 mr-3'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <GraduationCap className="w-5 h-5 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-2xl px-4 py-3 shadow-sm ${
          isUser 
            ? 'bg-primary-500 text-white' 
            : 'bg-white border border-gray-200'
        }`}>
          {/* Main Content */}
          <div className={`text-sm ${isUser ? 'text-white' : 'text-gray-800'}`}>
            {typeof message.content === 'string' ? (
              <div className="whitespace-pre-wrap">
                {formatContent(message.content)}
              </div>
            ) : (
              message.content
            )}
          </div>

          {/* Corrections Display */}
          {!isUser && message.corrections && message.corrections.length > 0 && (
            <div className="mt-3 space-y-2">
              {message.corrections.map((correction, index) => (
                <div key={index} className="bg-yellow-50 rounded-lg p-3 border-l-4 border-yellow-400">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-yellow-600" />
                    <span className="text-sm font-medium text-yellow-800">
                      {correction.mistake_type} Error
                    </span>
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-700">
                    <div>
                      <span className="text-red-600 line-through">{correction.original_text}</span>
                      {' → '}
                      <span className="text-green-600 font-medium">{correction.corrected_text}</span>
                    </div>
                    
                    <div className="bg-white rounded p-2 mt-2">
                      <div className="text-gray-800 mb-1">
                        💡 {correction.explanation_english}
                      </div>
                      <div className="telugu-text text-gray-600 text-xs">
                        {correction.explanation_telugu}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Examples */}
          {!isUser && message.examples && message.examples.length > 0 && (
            <div className="mt-3 bg-blue-50 rounded-lg p-3">
              <h4 className="text-sm font-medium text-blue-800 mb-2">📚 Examples:</h4>
              <div className="space-y-2">
                {message.examples.map((example, index) => (
                  <div key={index} className="text-sm">
                    <div className="text-gray-800">{example.english}</div>
                    <div className="telugu-text text-gray-600 text-xs">{example.telugu}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Verb Forms */}
          {!isUser && message.verbForms && (
            <div className="mt-3 bg-purple-50 rounded-lg p-3">
              <h4 className="text-sm font-medium text-purple-800 mb-2">🔤 Verb Forms:</h4>
              <div className="grid grid-cols-1 gap-1 text-sm text-gray-700">
                <div><span className="font-medium">Base:</span> {message.verbForms.base_form}</div>
                <div><span className="font-medium">Past:</span> {message.verbForms.past_simple}</div>
                <div><span className="font-medium">Past Participle:</span> {message.verbForms.past_participle}</div>
                <div><span className="font-medium">Present Participle:</span> {message.verbForms.present_participle}</div>
                <div><span className="font-medium">3rd Person:</span> {message.verbForms.third_person}</div>
              </div>
            </div>
          )}

          {/* Encouragement */}
          {!isUser && message.encouragement && (
            <div className="mt-3 bg-green-50 rounded-lg p-3 border-l-4 border-green-400">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-800">Encouragement</span>
              </div>
              <div className="text-sm text-green-700 mt-1 whitespace-pre-wrap">
                {message.encouragement}
              </div>
            </div>
          )}

          {/* Next Suggestion */}
          {!isUser && message.nextSuggestion && (
            <div className="mt-3 bg-indigo-50 rounded-lg p-3">
              <h4 className="text-sm font-medium text-indigo-800 mb-1">🎯 Next Practice:</h4>
              <div className="text-sm text-indigo-700 whitespace-pre-wrap">
                {message.nextSuggestion}
              </div>
            </div>
          )}

          {/* Message Actions */}
          {!isUser && (message.encouragement || message.content) && (
            <div className="mt-3 flex justify-end">
              <button
                onClick={onSpeak}
                className="flex items-center space-x-1 px-2 py-1 text-xs text-gray-500 hover:text-primary-600 transition-colors"
                title="Listen to pronunciation"
              >
                {isSpeaking ? (
                  <>
                    <VolumeX className="w-3 h-3" />
                    <span>Stop</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-3 h-3" />
                    <span>Listen</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Timestamp */}
          <div className={`text-xs mt-2 ${isUser ? 'text-primary-100' : 'text-gray-400'}`}>
            {message.timestamp.toLocaleTimeString()}
            {message.isVoice && (
              <span className="ml-1">🎤</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;