# 🎤 Voice Features Setup Guide

Your AI English Tutor now has **real voice capabilities** using **Web Speech API + gTTS**!

## 🎯 **What's New:**

### ✅ **Speech-to-Text (STT)**
- **Technology**: Web Speech API (Browser-based)
- **Benefits**: Real-time recognition, no server processing, free
- **Languages**: English (US/India), Telugu (limited)
- **No credentials needed**

### ✅ **Text-to-Speech (TTS)** 
- **Technology**: gTTS (Google Text-to-Speech) + Browser fallback
- **Benefits**: High-quality voices, multiple languages, free
- **Languages**: English, Telugu, Hindi, Tamil, and more
- **No credentials needed**

---

## 🚀 **Quick Start:**

### **1. Backend Setup (Already Done!)**
```bash
pip install gtts==2.4.0
```

### **2. Frontend Usage**
```jsx
// Import the voice components
import VoiceInteraction from './components/VoiceInteraction';
import { useWebSpeechRecognition, useEnhancedTextToSpeech } from './hooks/useWebSpeechAPI';

// Basic voice input
function MyComponent() {
  const handleTranscript = (text) => {
    console.log("User said:", text);
  };
  
  return (
    <VoiceInteraction 
      onTranscriptReceived={handleTranscript}
      onError={(error) => console.error(error)}
    />
  );
}
```

### **3. Complete Voice Chat Integration**
```jsx
import VoiceEnabledChat from './components/VoiceEnabledChat';

function App() {
  return <VoiceEnabledChat />;
}
```

---

## 🎛️ **API Endpoints:**

### **Text-to-Speech**
```http
POST /api/text-to-speech
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "language_code": "en-US"
}

Response:
{
  "audio_content": "base64_encoded_mp3_data",
  "message": "Audio generated successfully"
}
```

---

## 🌐 **Browser Support:**

| Feature | Chrome | Edge | Safari | Firefox |
|---------|--------|------|--------|---------|
| **Web Speech API** | ✅ | ✅ | ✅ | ❌ |
| **Speech Synthesis** | ✅ | ✅ | ✅ | ✅ |
| **gTTS Playback** | ✅ | ✅ | ✅ | ✅ |

**Note**: Firefox users will use browser TTS fallback (still works!)

---

## 🔧 **Configuration:**

### **Environment Variables (backend/.env):**
```env
# Text-to-Speech Settings (gTTS)
TTS_DEFAULT_LANGUAGE=en-US
TTS_SLOW_SPEECH=true
TTS_SUPPORT_LANGUAGES=en-US,en-IN,te-IN,hi-IN,ta-IN

# Speech Recognition Settings (Web Speech API - Frontend)
STT_DEFAULT_LANGUAGE=en-US
STT_ALTERNATIVE_LANGUAGES=en-IN,te-IN
STT_INTERIM_RESULTS=true
STT_CONTINUOUS_RECOGNITION=false
```

---

## 🎯 **Usage Examples:**

### **1. Basic Voice Recognition**
```jsx
const { isListening, transcript, startListening, stopListening } = useWebSpeechRecognition();

// Start listening
startListening('en-US');

// Use transcript
useEffect(() => {
  if (transcript) {
    console.log("User said:", transcript);
  }
}, [transcript]);
```

### **2. Text-to-Speech**
```jsx
const { speak, isSpeaking, stopSpeaking } = useEnhancedTextToSpeech();

// Speak text using backend gTTS
speak("Hello, this is your AI tutor!", {
  languageCode: 'en-US',
  rate: 0.8,
  useBackend: true
});

// Use browser fallback
speak("Fallback speech", { useBackend: false });
```

### **3. Complete Voice Interaction**
```jsx
const voiceFeatures = useVoiceInteraction();

// Start voice conversation mode
voiceFeatures.startVoiceConversation();

// Process what user said
useEffect(() => {
  if (voiceFeatures.transcript) {
    // Send to AI tutor
    processUserMessage(voiceFeatures.transcript);
  }
}, [voiceFeatures.transcript]);
```

---

## 🛠️ **Integration with Existing Chat:**

### **Add Voice to Your Chat Component:**
```jsx
// In your existing chat component
import VoiceInteraction, { useSpeakText } from './VoiceInteraction';

function ExistingChatComponent() {
  const { speakText } = useSpeakText();
  
  const handleVoiceInput = (transcript) => {
    // Use existing message sending logic
    sendMessage(transcript, true); // isVoice = true
  };
  
  const handleTutorResponse = (response) => {
    // Auto-speak tutor responses
    if (response.encouragement) {
      speakText(response.encouragement);
    }
  };
  
  return (
    <div>
      {/* Existing chat UI */}
      
      {/* Add voice interface */}
      <VoiceInteraction 
        onTranscriptReceived={handleVoiceInput}
        onError={console.error}
      />
    </div>
  );
}
```

---

## ✨ **Features:**

### **Voice Input:**
- ✅ Real-time speech recognition
- ✅ Interim results while speaking
- ✅ Multiple language support
- ✅ Automatic error handling
- ✅ Visual feedback (listening indicator)

### **Voice Output:**
- ✅ High-quality gTTS voices
- ✅ Slow speech for learning
- ✅ Multi-language support
- ✅ Browser fallback
- ✅ Pronunciation guides

### **Smart Integration:**
- ✅ Auto-detect voice vs text input
- ✅ Contextual pronunciation help
- ✅ Bilingual support (English + Telugu)
- ✅ Error handling and fallbacks
- ✅ Accessibility features

---

## 🚨 **Troubleshooting:**

### **Voice Input Not Working:**
1. **Check browser support** - Use Chrome/Edge/Safari
2. **Check microphone permissions** - Allow mic access
3. **Check HTTPS** - Web Speech API requires HTTPS in production

### **Voice Output Not Working:**
1. **Backend gTTS fails** → Browser TTS fallback activates automatically
2. **No sound** → Check browser audio settings
3. **Wrong language** → Verify language_code parameter

### **Common Issues:**
```jsx
// Handle permission denied
useEffect(() => {
  if (speechError === 'not-allowed') {
    alert('Please allow microphone access for voice features');
  }
}, [speechError]);

// Handle unsupported browsers
if (!isSupported) {
  return <div>Voice features require Chrome, Edge, or Safari</div>;
}
```

---

## 🎉 **Test Your Voice Setup:**

### **1. Basic Test:**
1. Open your app in Chrome/Edge/Safari
2. Click the microphone button
3. Say "Hello, how are you?"
4. Verify text appears correctly

### **2. TTS Test:**
1. Click the speaker button on any tutor message
2. Verify audio plays with clear pronunciation
3. Test both English and Telugu (if supported)

### **3. Full Conversation Test:**
1. Start voice mode
2. Have a complete conversation using only voice
3. Verify corrections and pronunciation guides work

---

## 📊 **Performance:**

- **STT Latency**: ~100-500ms (browser-dependent)
- **TTS Generation**: ~1-2 seconds (gTTS backend)
- **TTS Fallback**: Instant (browser synthesis)
- **Bandwidth**: Minimal (only TTS audio download)
- **Offline**: STT works offline in some browsers, TTS requires internet

---

## 🔮 **Advanced Features:**

### **Custom Voice Commands:**
```jsx
const handleTranscript = (text) => {
  if (text.toLowerCase().includes('speak slower')) {
    // Adjust TTS speed
    speak(lastMessage, { rate: 0.6 });
  } else if (text.toLowerCase().includes('repeat')) {
    // Repeat last message
    speak(lastMessage);
  }
  // ... handle normal message
};
```

### **Voice-Only Mode:**
```jsx
const [voiceOnlyMode, setVoiceOnlyMode] = useState(false);

// Hide text input when in voice-only mode
{!voiceOnlyMode && <TextInput />}
```

### **Multi-Language Auto-Detection:**
```jsx
// Auto-switch TTS language based on content
const detectLanguage = (text) => {
  // Simple Telugu detection
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te-IN';
  return 'en-US';
};
```

---

## 🎯 **Next Steps:**

1. **Test the voice features** in your browser
2. **Integrate `VoiceInteraction`** into your existing chat
3. **Customize the UI** to match your design
4. **Add voice shortcuts** for common actions
5. **Consider offline fallbacks** for better UX

Your AI English Tutor now has **full voice capabilities** without requiring any Google Cloud credentials! 🎉