#!/usr/bin/env python3
"""
Quick test script to verify the voice service fixes
"""

import asyncio
import os
import sys
import tempfile
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from services.speech_service import SpeechService

async def test_tts():
    """Test text-to-speech functionality"""
    print("🧪 Testing Text-to-Speech fixes...")
    
    # Initialize speech service
    speech_service = SpeechService()
    await speech_service.initialize()
    
    # Test cases
    test_cases = [
        {
            "text": "Hello, this is a simple test.",
            "language": "en-US",
            "description": "Simple English text"
        },
        {
            "text": "Ready to start learning? चलो शुरू करते हैं! 🚀",
            "language": "en-US",
            "description": "Mixed script text (the problematic one from logs)"
        },
        {
            "text": "Welcome to English learning! 😊",
            "language": "en-US",
            "description": "Text with emoji"
        },
        {
            "text": "నమస్కారం! Welcome to English tutoring.",
            "language": "en-US",
            "description": "English with Telugu script"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"   Input: '{test_case['text'][:50]}...'")
        
        try:
            # Generate TTS
            audio_b64 = await speech_service.text_to_speech(
                text=test_case["text"],
                language_code=test_case["language"]
            )
            
            if audio_b64:
                print(f"   ✅ Success! Generated {len(audio_b64)} characters of base64 audio")
                
                # Verify it's valid base64 and reasonable size
                try:
                    import base64
                    audio_bytes = base64.b64decode(audio_b64)
                    print(f"   📊 Audio size: {len(audio_bytes)} bytes")
                    
                    if len(audio_bytes) > 1000:  # Reasonable minimum size for audio
                        print(f"   🎵 Audio appears valid")
                    else:
                        print(f"   ⚠️  Audio seems too small")
                        
                except Exception as e:
                    print(f"   ❌ Invalid base64 audio: {e}")
            else:
                print(f"   ❌ Failed to generate audio")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print(f"\n✅ TTS testing complete!")

async def test_service_info():
    """Test service information"""
    print("\n🔧 Testing service configuration...")
    
    speech_service = SpeechService()
    await speech_service.initialize()
    
    # Test service availability
    is_available = speech_service.is_service_available()
    print(f"Service available: {'✅' if is_available else '❌'}")
    
    # Test supported languages
    languages = await speech_service.get_supported_languages()
    print(f"Supported TTS languages: {len(languages.get('text_to_speech', []))}")
    
    # Test service info
    service_info = speech_service.get_service_info()
    print(f"TTS Provider: {service_info['tts_provider']}")
    print(f"STT Provider: {service_info['stt_provider']}")

def test_text_preprocessing():
    """Test text preprocessing function"""
    print("\n🧼 Testing text preprocessing...")
    
    speech_service = SpeechService()
    
    test_texts = [
        "Hello world! 🚀",
        "Ready to start learning? चलो शुरू करते हैं!",
        "Multiple    spaces   and!!!!! punctuation?????",
        "Telugu text: నమస్కారం mixed with English",
        "   Whitespace test   "
    ]
    
    for text in test_texts:
        cleaned = speech_service._preprocess_text_for_tts(text, "en-US")
        print(f"Original: '{text}'")
        print(f"Cleaned:  '{cleaned}'")
        print()

async def main():
    """Run all tests"""
    print("🎤 Voice Service Fix Verification")
    print("=" * 40)
    
    # Test text preprocessing
    test_text_preprocessing()
    
    # Test service info
    await test_service_info()
    
    # Test TTS functionality
    await test_tts()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())