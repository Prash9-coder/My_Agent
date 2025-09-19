"""
Database models and connection handling
"""

import os
import logging
from datetime import datetime
from typing import Optional, Generator
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Database configuration
# Force SQLite for Replit environment instead of auto-provisioned PostgreSQL
DATABASE_URL = 'sqlite:///./ai_english_tutor.db'

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=os.getenv('SQL_DEBUG', 'False').lower() == 'true'
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Student(Base):
    """Student profile and settings"""
    __tablename__ = "students"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    native_language = Column(String, default="Telugu")
    target_language = Column(String, default="English")
    current_level = Column(String, default="beginner")
    learning_goals = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    """Conversation sessions"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    topic = Column(String, nullable=True)
    total_messages = Column(Integer, default=0)
    correct_messages = Column(Integer, default=0)
    session_duration_minutes = Column(Float, default=0.0)
    session_type = Column(String, default="chat")  # chat, voice, lesson, exercise

class Message(Base):
    """Individual messages in conversations"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    message_text = Column(Text, nullable=False)
    is_student_message = Column(Boolean, default=True)
    is_voice_input = Column(Boolean, default=False)
    is_correct = Column(Boolean, nullable=True)  # Null for tutor messages
    complexity_score = Column(Float, default=0.0)
    word_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Correction(Base):
    """Grammar and language corrections"""
    __tablename__ = "corrections"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    mistake_type = Column(String, nullable=False)
    explanation_english = Column(Text)
    explanation_telugu = Column(Text)
    position_start = Column(Integer, default=0)
    position_end = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentProgress(Base):
    """Student learning progress tracking"""
    __tablename__ = "student_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True, nullable=False)
    date = Column(String, index=True)  # YYYY-MM-DD format
    total_sentences = Column(Integer, default=0)
    correct_sentences = Column(Integer, default=0)
    total_mistakes = Column(Integer, default=0)
    session_time_minutes = Column(Float, default=0.0)
    topics_covered = Column(JSON, default=list)
    level_assessed = Column(String, nullable=True)
    streak_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Lesson(Base):
    """Learning lessons"""
    __tablename__ = "lessons"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    lesson_type = Column(String, nullable=False)  # grammar, vocabulary, conversation, etc.
    target_level = Column(String, nullable=False)
    content = Column(JSON, nullable=False)  # Lesson content structure
    estimated_duration = Column(Integer, default=15)
    prerequisites = Column(JSON, default=list)
    learning_objectives = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Exercise(Base):
    """Practice exercises"""
    __tablename__ = "exercises"
    
    id = Column(String, primary_key=True, index=True)
    lesson_id = Column(String, nullable=True)  # Optional association with lesson
    exercise_type = Column(String, nullable=False)  # fill_blanks, multiple_choice, etc.
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For multiple choice
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    difficulty = Column(String, default="beginner")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentExerciseAttempt(Base):
    """Student attempts at exercises"""
    __tablename__ = "student_exercise_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True, nullable=False)
    exercise_id = Column(String, index=True, nullable=False)
    student_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    attempted_at = Column(DateTime, default=datetime.utcnow)

class Vocabulary(Base):
    """Vocabulary words and their details"""
    __tablename__ = "vocabulary"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    meaning_telugu = Column(Text, nullable=False)
    part_of_speech = Column(String)
    pronunciation = Column(String)
    difficulty_level = Column(String, default="beginner")
    frequency_rank = Column(Integer, default=0)  # How common the word is
    examples = Column(JSON, default=list)  # Example sentences
    synonyms = Column(JSON, default=list)
    antonyms = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyVocabulary(Base):
    """Daily vocabulary assignments"""
    __tablename__ = "daily_vocabulary"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)  # YYYY-MM-DD
    theme = Column(String)
    word_ids = Column(JSON, nullable=False)  # List of vocabulary word IDs
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentVocabularyProgress(Base):
    """Student progress on vocabulary"""
    __tablename__ = "student_vocabulary_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True, nullable=False)
    vocabulary_id = Column(Integer, index=True, nullable=False)
    mastery_level = Column(Float, default=0.0)  # 0.0 to 1.0
    times_seen = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    last_reviewed = Column(DateTime, default=datetime.utcnow)
    next_review = Column(DateTime, default=datetime.utcnow)

class LearningInsight(Base):
    """Personalized learning insights"""
    __tablename__ = "learning_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True, nullable=False)
    insight_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    action_suggestion = Column(Text, nullable=True)
    priority = Column(String, default="medium")
    is_read = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class SystemConfig(Base):
    """System configuration and settings"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String, unique=True, index=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database utility functions
def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

def get_db_session() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with default data"""
    try:
        create_tables()
        
        # Add default system configurations
        db = SessionLocal()
        
        default_configs = [
            {
                "config_key": "daily_vocabulary_count",
                "config_value": 5,
                "description": "Number of vocabulary words to show daily"
            },
            {
                "config_key": "weekly_goal_sentences",
                "config_value": 50,
                "description": "Default weekly sentence practice goal"
            },
            {
                "config_key": "supported_languages",
                "config_value": {
                    "source": ["Telugu", "English"],
                    "target": ["English", "Telugu"]
                },
                "description": "Supported languages for translation"
            },
            {
                "config_key": "difficulty_levels",
                "config_value": ["beginner", "intermediate", "advanced"],
                "description": "Available difficulty levels"
            }
        ]
        
        for config in default_configs:
            existing = db.query(SystemConfig).filter(
                SystemConfig.config_key == config["config_key"]
            ).first()
            
            if not existing:
                db_config = SystemConfig(**config)
                db.add(db_config)
        
        db.commit()
        db.close()
        
        logger.info("✅ Database initialized with default data")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise

def get_system_config(config_key: str, default_value=None):
    """Get system configuration value"""
    try:
        db = SessionLocal()
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_key
        ).first()
        db.close()
        
        if config:
            return config.config_value
        return default_value
        
    except Exception as e:
        logger.error(f"Error getting system config {config_key}: {e}")
        return default_value

def set_system_config(config_key: str, config_value, description: str = None):
    """Set system configuration value"""
    try:
        db = SessionLocal()
        
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_key
        ).first()
        
        if config:
            config.config_value = config_value
            if description:
                config.description = description
            config.updated_at = datetime.utcnow()
        else:
            config = SystemConfig(
                config_key=config_key,
                config_value=config_value,
                description=description
            )
            db.add(config)
        
        db.commit()
        db.close()
        
        logger.info(f"✅ System config updated: {config_key}")
        
    except Exception as e:
        logger.error(f"❌ Error setting system config {config_key}: {e}")
        raise

# Database migration utilities
def check_database_health() -> dict:
    """Check database connectivity and health"""
    try:
        db = SessionLocal()
        
        # Test basic connectivity
        result = db.execute("SELECT 1").fetchone()
        
        # Count records in key tables
        stats = {
            "students": db.query(Student).count(),
            "conversations": db.query(Conversation).count(),
            "messages": db.query(Message).count(),
            "corrections": db.query(Correction).count(),
            "lessons": db.query(Lesson).count(),
            "exercises": db.query(Exercise).count(),
            "vocabulary": db.query(Vocabulary).count()
        }
        
        db.close()
        
        return {
            "status": "healthy",
            "database_url": DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL,
            "connection": "active",
            "table_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection": "failed"
        }

# Initialize database on import
if __name__ != "__main__":
    try:
        init_database()
    except Exception as e:
        logger.warning(f"Could not initialize database automatically: {e}")
        logger.warning("Database will be initialized on first use")