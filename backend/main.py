"""
AI English Tutor - FastAPI Backend
Main application entry point
"""

import os
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import our services
from services.ai_tutor import AITutorService
from services.speech_service import SpeechService
from services.progress_tracker import ProgressTracker
from models.schemas import (
    ChatMessage, ChatResponse, StudentProgress, 
    VocabularyWord, Lesson, Exercise
)
from models.database import get_db_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services (will be initialized in lifespan)
ai_tutor = None
speech_service = None
progress_tracker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting AI English Tutor API...")
    
    global ai_tutor, speech_service, progress_tracker
    
    # Initialize database
    logger.info("📊 Initializing database...")
    # Database initialization would go here
    
    # Initialize services
    logger.info("🧠 Initializing AI services...")
    ai_tutor = AITutorService()
    await ai_tutor.initialize()
    
    logger.info("🎤 Initializing speech services...")
    speech_service = SpeechService()
    await speech_service.initialize()
    
    logger.info("📊 Initializing progress tracker...")
    progress_tracker = ProgressTracker()
    
    logger.info("✅ AI English Tutor API started successfully!")
    
    yield  # Server is running
    
    # Shutdown
    logger.info("👋 Shutting down AI English Tutor API...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AI English Tutor API",
    description="Backend API for AI English Tutor - helping Telugu speakers learn English",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services are now initialized in the lifespan function above

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    student_id: str
    is_voice: bool = False

class SpeechToTextResponse(BaseModel):
    text: str
    confidence: float
    language: str

class TextToSpeechRequest(BaseModel):
    text: str
    language_code: str = "en-US"

class TextToSpeechResponse(BaseModel):
    audio_content: Optional[str] = None
    message: str

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI English Tutor API is running!",
        "version": "1.0.0"
    }

# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """
    Main chat endpoint - processes student messages and returns tutor responses
    """
    try:
        logger.info(f"Chat request from student {request.student_id}: {request.message}")
        
        # Process the message with AI tutor
        response = await ai_tutor.process_message(
            message=request.message,
            student_id=request.student_id,
            is_voice=request.is_voice
        )
        
        # Update student progress
        await progress_tracker.update_progress(
            student_id=request.student_id,
            message=request.message,
            corrections=response.corrections,
            is_correct=response.is_correct
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")

# Speech endpoints
@app.post("/api/speech-to-text", response_model=SpeechToTextResponse)
async def convert_speech_to_text(audio: UploadFile = File(...)):
    """
    Speech-to-text endpoint - Web Speech API should be used on frontend
    This endpoint serves as fallback/server-side processing if needed
    """
    try:
        logger.info(f"STT fallback request: {audio.filename}")
        
        # Read audio file (for validation)
        audio_content = await audio.read()
        
        # Note: STT is primarily handled by Web Speech API on frontend
        result = await speech_service.speech_to_text(audio_content)
        
        return SpeechToTextResponse(
            text=result.get("text", ""),
            confidence=result.get("confidence", 0.0),
            language=result.get("language", "en-US")
        )
        
    except Exception as e:
        logger.error(f"Error in STT endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Use Web Speech API on frontend for better STT")

@app.post("/api/text-to-speech", response_model=TextToSpeechResponse)
async def convert_text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using gTTS (Google Text-to-Speech) - Free and no credentials required
    """
    try:
        logger.info(f"Text-to-speech request: {request.text[:50]}...")
        
        # Convert to speech
        audio_content = await speech_service.text_to_speech(
            text=request.text,
            language_code=request.language_code
        )
        
        return TextToSpeechResponse(
            audio_content=audio_content,
            message="Audio generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in text-to-speech endpoint: {str(e)}")
        return TextToSpeechResponse(
            audio_content=None,
            message="Text-to-speech service unavailable, using browser fallback"
        )

# Student progress endpoints
@app.get("/api/student/{student_id}/progress", response_model=StudentProgress)
async def get_student_progress(student_id: str):
    """
    Get comprehensive progress data for a student
    """
    try:
        progress = await progress_tracker.get_student_progress(student_id)
        return progress
    except Exception as e:
        logger.error(f"Error getting student progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving progress")

@app.get("/api/student/{student_id}/mistakes")
async def get_common_mistakes(student_id: str):
    """
    Get common mistakes for a student
    """
    try:
        mistakes = await progress_tracker.get_common_mistakes(student_id)
        return mistakes
    except Exception as e:
        logger.error(f"Error getting common mistakes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving mistakes")

# Request models for lessons and exercises
class LessonRequest(BaseModel):
    lesson_type: str
    duration_minutes: int = 15

class ExerciseRequest(BaseModel):
    exercise_type: str
    difficulty: str

# Lesson endpoints
@app.post("/api/student/{student_id}/lesson")
async def get_personalized_lesson(
    student_id: str,
    request: LessonRequest
):
    """
    Generate a personalized lesson for the student
    """
    try:
        lesson = await ai_tutor.generate_lesson(
            student_id=student_id,
            lesson_type=request.lesson_type,
            duration_minutes=request.duration_minutes
        )
        return lesson
    except Exception as e:
        logger.error(f"Error generating lesson: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating lesson")

@app.post("/api/student/{student_id}/exercise")
async def generate_exercise(
    student_id: str,
    request: ExerciseRequest
):
    """
    Generate exercises for practice
    """
    try:
        exercise = await ai_tutor.generate_exercise(
            student_id=student_id,
            exercise_type=request.exercise_type,
            difficulty=request.difficulty
        )
        return exercise
    except Exception as e:
        logger.error(f"Error generating exercise: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating exercise")

# Vocabulary endpoints
@app.get("/api/vocabulary/daily")
async def get_daily_vocabulary():
    """
    Get daily vocabulary words
    """
    try:
        vocabulary = await ai_tutor.get_daily_vocabulary()
        return vocabulary
    except Exception as e:
        logger.error(f"Error getting daily vocabulary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving vocabulary")

# Translation endpoint
@app.post("/api/translate")
async def translate_text(
    text: str,
    source_language: str,
    target_language: str
):
    """
    Translate text between languages with explanations
    """
    try:
        translation = await ai_tutor.translate_with_explanation(
            text=text,
            source_language=source_language,
            target_language=target_language
        )
        return translation
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise HTTPException(status_code=500, detail="Error translating text")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup and shutdown events are now handled by the lifespan function above

if __name__ == "__main__":
    # This is for development only
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )