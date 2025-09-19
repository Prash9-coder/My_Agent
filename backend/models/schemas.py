"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Base models
class Example(BaseModel):
    """Example sentence with Telugu translation"""
    english: str = Field(..., description="English sentence")
    telugu: str = Field(..., description="Telugu translation")

class Correction(BaseModel):
    """Grammar/language correction details"""
    original_text: str = Field(..., description="Original incorrect text")
    corrected_text: str = Field(..., description="Corrected text")
    mistake_type: str = Field(..., description="Type of mistake (grammar, tense, etc.)")
    explanation_english: str = Field(..., description="Explanation in English")
    explanation_telugu: str = Field(..., description="Explanation in Telugu")
    position_start: int = Field(default=0, description="Start position of error in text")
    position_end: int = Field(default=0, description="End position of error in text")

class VerbForms(BaseModel):
    """Five forms of a verb"""
    base_form: str = Field(..., description="Base form (go)")
    past_simple: str = Field(..., description="Past simple (went)")
    past_participle: str = Field(..., description="Past participle (gone)")
    present_participle: str = Field(..., description="Present participle (going)")
    third_person: str = Field(..., description="Third person singular (goes)")

# Chat models
class ChatMessage(BaseModel):
    """Student message to the tutor"""
    message: str = Field(..., description="Student's message")
    student_id: str = Field(..., description="Unique student identifier")
    is_voice: bool = Field(default=False, description="Whether message came from voice input")

class ChatResponse(BaseModel):
    """AI Tutor's response to student"""
    is_correct: bool = Field(..., description="Whether student's message was correct")
    corrections: List[Correction] = Field(default=[], description="List of corrections if any")
    examples: List[Example] = Field(default=[], description="Example sentences")
    verb_forms: Optional[VerbForms] = Field(default=None, description="Verb forms if applicable")
    encouragement: str = Field(..., description="Encouraging message for student")
    next_suggestion: Optional[str] = Field(default=None, description="Suggestion for next practice")
    grammar_tip: Optional[str] = Field(default=None, description="Relevant grammar tip")
    pronunciation_guide: Optional[str] = Field(default=None, description="Pronunciation guidance for speaking")
    student_level: str = Field(default="beginner", description="Assessed student level")

# Progress tracking models
class StudentProgress(BaseModel):
    """Comprehensive student progress data"""
    student_id: str = Field(..., description="Student identifier")
    total_conversations: int = Field(..., description="Total number of conversations")
    total_sentences: int = Field(..., description="Total sentences practiced")
    correct_sentences: int = Field(..., description="Number of correct sentences")
    accuracy_percentage: float = Field(..., description="Overall accuracy percentage")
    recent_accuracy_percentage: float = Field(..., description="Recent accuracy percentage")
    current_level: str = Field(..., description="Current proficiency level")
    streak_days: int = Field(..., description="Current practice streak in days")
    strengths: List[str] = Field(default=[], description="Student's strengths")
    areas_for_improvement: List[str] = Field(default=[], description="Areas to improve")
    last_activity: Optional[str] = Field(default=None, description="Last activity timestamp")
    learning_insights: List[str] = Field(default=[], description="Personalized learning insights")
    weekly_goal_progress: Dict[str, Any] = Field(default={}, description="Weekly goal progress")
    achievements: List[Dict[str, Any]] = Field(default=[], description="Student achievements")

class MistakeAnalysis(BaseModel):
    """Analysis of a common mistake"""
    mistake_type: str = Field(..., description="Type of mistake")
    count: int = Field(..., description="Number of times this mistake occurred")
    description: str = Field(..., description="Description of the mistake")
    recent_examples: List[str] = Field(default=[], description="Recent examples of this mistake")
    suggested_practice: str = Field(..., description="Suggested practice for improvement")
    last_occurrence: str = Field(..., description="When this mistake last occurred")
    improvement_trend: str = Field(..., description="Whether student is improving")

# Vocabulary models
class VocabularyWord(BaseModel):
    """Daily vocabulary word with details"""
    word: str = Field(..., description="English word")
    meaning_telugu: str = Field(..., description="Telugu meaning")
    part_of_speech: str = Field(..., description="Part of speech (noun, verb, etc.)")
    pronunciation: str = Field(..., description="Phonetic pronunciation")
    examples: List[Example] = Field(default=[], description="Example sentences")

class DailyVocabulary(BaseModel):
    """Daily vocabulary collection"""
    date: str = Field(..., description="Date for this vocabulary set")
    theme: str = Field(..., description="Theme or topic for the day")
    words: List[VocabularyWord] = Field(..., description="List of vocabulary words")

# Lesson models
class LessonContent(BaseModel):
    """Content of a lesson"""
    title: str = Field(..., description="Lesson title")
    explanation_english: str = Field(..., description="Lesson explanation in English")
    explanation_telugu: str = Field(..., description="Lesson explanation in Telugu")
    key_points: List[str] = Field(default=[], description="Key learning points")
    examples: List[Example] = Field(default=[], description="Lesson examples")

class Lesson(BaseModel):
    """Complete lesson structure"""
    lesson_id: str = Field(..., description="Unique lesson identifier")
    lesson_type: str = Field(..., description="Type of lesson (grammar, vocabulary, etc.)")
    student_level: str = Field(..., description="Target student level")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")
    content: LessonContent = Field(..., description="Lesson content")

class Exercise(BaseModel):
    """Practice exercise"""
    exercise_id: str = Field(..., description="Unique exercise identifier")
    question: str = Field(..., description="Exercise question")
    options: Optional[List[str]] = Field(default=None, description="Multiple choice options")
    correct_answer: str = Field(..., description="Correct answer")
    explanation: str = Field(..., description="Explanation of the answer")
    difficulty: str = Field(..., description="Exercise difficulty level")

class ExerciseSet(BaseModel):
    """Set of exercises"""
    exercise_type: str = Field(..., description="Type of exercises")
    difficulty: str = Field(..., description="Difficulty level")
    exercises: List[Exercise] = Field(..., description="List of exercises")

# Speech models
class SpeechToTextResult(BaseModel):
    """Result of speech-to-text conversion"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    language: str = Field(..., description="Detected language")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")

class TextToSpeechRequest(BaseModel):
    """Request for text-to-speech conversion"""
    text: str = Field(..., description="Text to convert to speech")
    language_code: str = Field(default="en-US", description="Language code for speech")
    voice_gender: Optional[str] = Field(default="FEMALE", description="Voice gender preference")
    speaking_rate: Optional[float] = Field(default=0.85, description="Speaking rate (0.25-4.0)")

# Translation models
class TranslationRequest(BaseModel):
    """Request for text translation"""
    text: str = Field(..., description="Text to translate")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")

class TranslationResponse(BaseModel):
    """Translation result with explanations"""
    original_text: str = Field(..., description="Original text")
    translated_text: str = Field(..., description="Translated text")
    explanation: str = Field(..., description="Grammar and structure explanation")
    word_breakdown: List[Dict[str, str]] = Field(default=[], description="Word-by-word breakdown")
    alternative_translations: List[str] = Field(default=[], description="Alternative ways to say it")

# Analytics models
class LearningInsight(BaseModel):
    """Personalized learning insight"""
    insight_type: str = Field(..., description="Type of insight")
    message: str = Field(..., description="Insight message")
    action_suggestion: Optional[str] = Field(default=None, description="Suggested action")
    priority: str = Field(default="medium", description="Priority level")

class WeeklyReport(BaseModel):
    """Weekly learning progress report"""
    student_id: str = Field(..., description="Student identifier")
    week_start: str = Field(..., description="Week start date")
    week_end: str = Field(..., description="Week end date")
    total_practice_days: int = Field(..., description="Days practiced this week")
    total_sentences: int = Field(..., description="Total sentences practiced")
    accuracy_percentage: float = Field(..., description="Average accuracy for the week")
    improvement_areas: List[str] = Field(default=[], description="Areas that need improvement")
    achievements: List[str] = Field(default=[], description="Weekly achievements")
    next_week_goals: List[str] = Field(default=[], description="Goals for next week")

# Conversation models
class ConversationContext(BaseModel):
    """Context for ongoing conversation"""
    student_id: str = Field(..., description="Student identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    topic: Optional[str] = Field(default=None, description="Current conversation topic")
    difficulty_level: str = Field(default="beginner", description="Current difficulty level")
    recent_messages: List[str] = Field(default=[], description="Recent message history")
    learning_objectives: List[str] = Field(default=[], description="Current learning objectives")

class RolePlaying(BaseModel):
    """Role-playing scenario setup"""
    scenario_id: str = Field(..., description="Scenario identifier")
    title: str = Field(..., description="Scenario title")
    description: str = Field(..., description="Scenario description")
    student_role: str = Field(..., description="Role for the student")
    tutor_role: str = Field(..., description="Role for the AI tutor")
    setting: str = Field(..., description="Setting/location of the scenario")
    objectives: List[str] = Field(..., description="Learning objectives for this scenario")
    starter_phrases: List[str] = Field(default=[], description="Phrases to help student start")

# Assessment models
class LevelAssessment(BaseModel):
    """Student level assessment result"""
    student_id: str = Field(..., description="Student identifier")
    current_level: str = Field(..., description="Current assessed level")
    confidence_score: float = Field(..., description="Confidence in assessment (0.0-1.0)")
    strengths: List[str] = Field(default=[], description="Identified strengths")
    weaknesses: List[str] = Field(default=[], description="Areas needing improvement")
    recommended_focus: List[str] = Field(default=[], description="Recommended focus areas")
    next_milestone: str = Field(..., description="Next learning milestone")

# API Response models
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    errors: Optional[List[str]] = Field(default=None, description="Error messages if any")

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    services: Dict[str, str] = Field(default={}, description="Status of dependent services")