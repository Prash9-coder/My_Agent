"""
Speech Service
Handles text-to-speech conversion using gTTS and supports Web Speech API for STT
"""

import os
import io
import base64
import logging
import tempfile
from typing import Dict, Optional
from gtts import gTTS

logger = logging.getLogger(__name__)

class SpeechService:
    """
    Service for handling speech recognition and synthesis
    - Uses gTTS for Text-to-Speech (free, no credentials needed)
    - Supports Web Speech API for Speech-to-Text (frontend-based)
    """
    
    def __init__(self):
        self.is_initialized = True  # gTTS doesn't require initialization
        
    async def initialize(self):
        """Initialize speech service (gTTS doesn't need special setup)"""
        try:
            # Test gTTS functionality
            test_tts = gTTS("Test", lang='en')
            self.is_initialized = True
            logger.info("✅ gTTS Speech service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing gTTS: {e}")
            self.is_initialized = False
    
    async def speech_to_text(self, audio_content: bytes, language_code: str = "en-US") -> Dict:
        """
        Speech-to-Text is handled by Web Speech API on frontend
        This method provides fallback/mock response
        """
        logger.info("Speech-to-text should be handled by Web Speech API on frontend")
        
        return {
            "text": "",
            "confidence": 0.0,
            "language": language_code,
            "note": "Use Web Speech API on frontend for STT"
        }
    
    async def text_to_speech(self, text: str, language_code: str = "en-US") -> Optional[str]:
        """
        Convert text to speech using gTTS
        Returns base64-encoded MP3 audio content
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided for TTS")
                return None
                
            # Clean and preprocess text for TTS
            cleaned_text = self._preprocess_text_for_tts(text, language_code)
            if not cleaned_text.strip():
                logger.warning("Text became empty after preprocessing")
                return None
                
            # Determine language for gTTS
            gtts_lang = self._map_language_code(language_code)
            
            # Determine speaking speed (slow for learning)
            slow_speech = True if language_code in ['en-US', 'en-IN'] else False
            
            logger.info(f"Generating TTS for: '{cleaned_text[:50]}...' in language: {gtts_lang}")
            
            # Create gTTS object
            tts = gTTS(text=cleaned_text, lang=gtts_lang, slow=slow_speech)
            
            # Save to temporary file with better Windows handling
            temp_file = None
            try:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                temp_file.close()  # Close immediately to avoid Windows file lock issues
                
                # Save TTS to temp file
                tts.save(temp_file.name)
                
                # Read the audio file and encode to base64
                with open(temp_file.name, 'rb') as audio_file:
                    audio_content = audio_file.read()
                    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                
            finally:
                # Clean up temporary file
                if temp_file and os.path.exists(temp_file.name):
                    try:
                        os.unlink(temp_file.name)
                    except PermissionError:
                        # Windows file handling - try again after a short delay
                        import time
                        time.sleep(0.1)
                        try:
                            os.unlink(temp_file.name)
                        except PermissionError:
                            logger.warning(f"Could not delete temporary file: {temp_file.name}")
                
            logger.info(f"Successfully generated TTS audio ({len(audio_content)} bytes)")
            return audio_base64
            
        except Exception as e:
            logger.error(f"Error in gTTS text-to-speech conversion: {e}")
            return None
    
    async def text_to_speech_with_pronunciation(self, text: str, pronunciation_guide: str = "", language_code: str = "en-US") -> Optional[str]:
        """
        Enhanced TTS that includes pronunciation guidance
        """
        try:
            # Combine text with pronunciation guide if provided
            full_text = text
            if pronunciation_guide:
                # Add pronunciation guide as prefix
                full_text = f"Listen carefully. {text}. Pronunciation tip: {pronunciation_guide}"
            
            return await self.text_to_speech(full_text, language_code)
            
        except Exception as e:
            logger.error(f"Error in enhanced TTS: {e}")
            return await self.text_to_speech(text, language_code)
    
    async def create_bilingual_audio(self, english_text: str, telugu_text: str) -> Optional[str]:
        """
        Create bilingual audio (English + Telugu explanation)
        """
        try:
            # Create English audio
            english_audio_b64 = await self.text_to_speech(english_text, "en-US")
            
            # Create Telugu audio
            telugu_audio_b64 = await self.text_to_speech(telugu_text, "te")
            
            if english_audio_b64 and telugu_audio_b64:
                # For now, return English audio (combining audio would require audio processing)
                # TODO: Could implement audio concatenation using libraries like pydub
                combined_text = f"{english_text}. Telugu explanation: {telugu_text}"
                return await self.text_to_speech(combined_text, "en-US")
            
            # Fallback to available audio
            return english_audio_b64 or telugu_audio_b64
            
        except Exception as e:
            logger.error(f"Error creating bilingual audio: {e}")
            return await self.text_to_speech(english_text, "en-US")
    
    def _preprocess_text_for_tts(self, text: str, language_code: str) -> str:
        """
        Clean and preprocess text for better TTS generation
        """
        import re
        
        # Remove or replace emojis and special characters that cause gTTS issues
        # Keep basic punctuation that helps with speech synthesis
        
        # Remove emojis (Unicode ranges for various emoji blocks)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # various symbols
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "]+", flags=re.UNICODE
        )
        cleaned_text = emoji_pattern.sub('', text)
        
        # INTELLIGENT SCRIPT HANDLING - Instead of removing, transliterate common phrases
        if language_code.startswith('en'):
            # Replace common Hindi/Telugu phrases with English phonetic equivalents
            transliterations = {
                # Hindi common phrases
                'चलो': 'Chalo',
                'शुरू': 'Shuru', 
                'करते': 'Karte',
                'हैं': 'Hain',
                'नमस्ते': 'Namaste',
                'नमस्कार': 'Namaskar',
                'धन्यवाद': 'Dhanyawad',
                'अच्छा': 'Accha',
                'हाँ': 'Haan',
                'नहीं': 'Nahin',
                
                # Telugu common phrases  
                'నమస్కారం': 'Namaskar',
                'చలో': 'Chalo',
                'మంచిది': 'Manchidi',
                'ధన్యవాదాలు': 'Dhanyawadalu',
                'అవును': 'Avunu',
                'లేదు': 'Ledu',
                
                # Combined phrases that often appear together
                'चलो शुरू करते हैं': 'Chalo shuru karte hain',
                'शुरू करते हैं': 'shuru karte hain',
            }
            
            # Apply transliterations
            for original, transliterated in transliterations.items():
                cleaned_text = cleaned_text.replace(original, transliterated)
            
            # For remaining non-Latin scripts, remove them but preserve word boundaries
            # This is more conservative than before
            non_latin_pattern = re.compile(r'[^\x00-\x7F\u0080-\u00FF\u0100-\u017F\u0180-\u024F\s.,!?;:()\'"-]+')
            # Replace with space to preserve word boundaries, not empty string
            cleaned_text = non_latin_pattern.sub(' ', cleaned_text)
        
        # Clean up whitespace and punctuation intelligently
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text.strip())
        
        # Normalize punctuation but don't be overly aggressive
        cleaned_text = re.sub(r'[!]{2,}', '!', cleaned_text)
        cleaned_text = re.sub(r'[?]{2,}', '?', cleaned_text)
        cleaned_text = re.sub(r'[.]{3,}', '...', cleaned_text)
        
        # Fix spacing around punctuation
        cleaned_text = re.sub(r'\s+([,.!?;:])', r'\1', cleaned_text)
        cleaned_text = re.sub(r'([.!?])\s*$', r'\1', cleaned_text)
        
        return cleaned_text
    
    def _map_language_code(self, language_code: str) -> str:
        """
        Map standard language codes to gTTS language codes
        """
        mapping = {
            'en-US': 'en',
            'en-IN': 'en',
            'en-GB': 'en',
            'te-IN': 'te',
            'hi-IN': 'hi',
            'ta-IN': 'ta',
            'kn-IN': 'kn',
            'ml-IN': 'ml'
        }
        
        return mapping.get(language_code, 'en')
    
    def is_service_available(self) -> bool:
        """Check if the speech service is available"""
        return self.is_initialized
    
    async def get_supported_languages(self) -> Dict:
        """Get list of supported languages for speech services"""
        return {
            "speech_to_text": [
                {"code": "en-US", "name": "English (US)", "note": "Handled by Web Speech API"},
                {"code": "en-IN", "name": "English (India)", "note": "Handled by Web Speech API"},
                {"code": "te-IN", "name": "Telugu (India)", "note": "Limited support via Web Speech API"}
            ],
            "text_to_speech": [
                {"code": "en-US", "name": "English (US)", "provider": "gTTS"},
                {"code": "en-IN", "name": "English (India)", "provider": "gTTS"},
                {"code": "te-IN", "name": "Telugu (India)", "provider": "gTTS"},
                {"code": "hi-IN", "name": "Hindi (India)", "provider": "gTTS"},
                {"code": "ta-IN", "name": "Tamil (India)", "provider": "gTTS"}
            ]
        }
    
    async def validate_audio_format(self, audio_content: bytes) -> bool:
        """
        Validate audio format (mainly for Web Speech API compatibility)
        """
        try:
            if not audio_content or len(audio_content) < 100:
                return False
            return True
            
        except Exception as e:
            logger.error(f"Error validating audio format: {e}")
            return False
    
    async def get_speech_recognition_hints(self, context: str) -> list:
        """
        Get speech recognition hints for Web Speech API
        These can be used to improve accuracy
        """
        hints = []
        
        if "grammar" in context.lower():
            hints.extend([
                "subject", "verb", "object", "tense", "present", "past", "future",
                "singular", "plural", "article", "preposition", "adjective", "adverb"
            ])
        elif "vocabulary" in context.lower():
            hints.extend([
                "meaning", "definition", "synonym", "antonym", "example", "sentence",
                "word", "phrase", "expression"
            ])
        elif "conversation" in context.lower():
            hints.extend([
                "hello", "goodbye", "please", "thank you", "excuse me", "sorry",
                "how are you", "what is your name", "nice to meet you", "good morning"
            ])
        
        # Add common English learning phrases
        hints.extend([
            "practice", "learn", "study", "English", "Telugu", "correct", "mistake",
            "pronunciation", "speaking", "listening", "reading", "writing"
        ])
        
        return hints
    
    async def get_pronunciation_audio(self, word: str, language_code: str = "en-US") -> Optional[str]:
        """
        Generate pronunciation audio for a specific word
        """
        try:
            # Create slower, clearer pronunciation
            pronunciation_text = f"The word is: {word}. Listen carefully: {word}."
            
            return await self.text_to_speech(pronunciation_text, language_code)
            
        except Exception as e:
            logger.error(f"Error generating pronunciation audio: {e}")
            return None
    
    async def create_practice_audio(self, sentences: list, language_code: str = "en-US") -> Optional[str]:
        """
        Create practice audio with multiple sentences
        """
        try:
            if not sentences:
                return None
            
            # Create practice session text
            practice_text = "Practice session. Listen and repeat after each sentence. "
            
            for i, sentence in enumerate(sentences, 1):
                practice_text += f"Sentence {i}: {sentence}. Repeat. "
            
            practice_text += "Good job! Practice complete."
            
            return await self.text_to_speech(practice_text, language_code)
            
        except Exception as e:
            logger.error(f"Error creating practice audio: {e}")
            return None
    
    def get_service_info(self) -> Dict:
        """Get information about the speech service"""
        return {
            "tts_provider": "gTTS (Google Text-to-Speech)",
            "stt_provider": "Web Speech API (Browser-based)",
            "tts_features": [
                "Multiple languages support",
                "Slow speech for learning",
                "Free and no credentials required",
                "High-quality natural voices"
            ],
            "stt_features": [
                "Real-time recognition",
                "Browser-based (no server processing)",
                "Good accuracy for English",
                "Works offline in some browsers"
            ],
            "limitations": [
                "gTTS requires internet connection",
                "Web Speech API browser support varies",
                "Telugu STT support is limited"
            ]
        }