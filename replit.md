# AI English Tutor - Replit Configuration

## Overview

An AI-powered English tutoring application designed specifically for Telugu-speaking students. The system provides personalized English learning through interactive conversations, real-time error correction, and voice-enabled practice sessions. Built as a full-stack web application with React frontend and FastAPI backend, featuring Google AI integration for intelligent tutoring and voice capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with Vite build tool
- **Styling**: Tailwind CSS with custom component library
- **State Management**: React hooks for local state, context for global state
- **Routing**: React Router DOM for navigation
- **Voice Integration**: Web Speech API for browser-based speech recognition
- **HTTP Client**: Axios for API communication with interceptors for error handling

### Backend Architecture
- **Framework**: FastAPI with async/await support
- **Language**: Python 3.8+ with type hints
- **Database**: SQLite for development (designed for PostgreSQL in production)
- **ORM**: SQLAlchemy with declarative models
- **AI Service**: Google Gemini for intelligent tutoring responses
- **Speech Service**: gTTS (Google Text-to-Speech) for audio generation
- **Authentication**: Designed for JWT-based auth (not fully implemented)

### Core Services
- **AI Tutor Service**: Processes student messages, provides corrections, explanations in Telugu
- **Speech Service**: Handles text-to-speech conversion using gTTS
- **Progress Tracker**: Monitors learning progress, tracks mistakes and improvements
- **Database Models**: Student profiles, conversations, progress tracking

### Design Patterns
- **Service Layer Pattern**: Separate services for AI, speech, and progress tracking
- **Repository Pattern**: Database access abstraction through SQLAlchemy models
- **Dependency Injection**: FastAPI's dependency system for service initialization
- **Event-Driven**: Lifespan events for service startup/shutdown

### Voice Features
- **Speech-to-Text**: Browser Web Speech API (no server processing)
- **Text-to-Speech**: gTTS library for server-side audio generation
- **Language Support**: English primary, Telugu explanations
- **Fallback System**: Mock responses when services unavailable

### Database Schema
- **Students**: Profile, language preferences, learning level
- **Conversations**: Chat sessions with AI tutor
- **Progress**: Learning analytics, mistake tracking, improvements
- **Content**: Vocabulary, lessons, exercises (expandable)

## External Dependencies

### AI and Language Services
- **Google Gemini API**: Core AI tutoring intelligence and response generation
- **gTTS (Google Text-to-Speech)**: Audio generation for pronunciation practice
- **TextBlob**: Basic text processing and language detection
- **NLTK**: Natural language processing utilities

### Frontend Libraries
- **Axios**: HTTP client for API communication
- **Lucide React**: Icon library for UI components
- **Headless UI**: Accessible UI components
- **Tailwind CSS**: Utility-first CSS framework

### Backend Libraries
- **FastAPI**: Modern Python web framework with automatic API documentation
- **SQLAlchemy**: Database ORM with support for multiple database backends
- **Pydantic**: Data validation and serialization
- **Python-Jose**: JWT token handling for authentication
- **Python-Multipart**: File upload support
- **Uvicorn**: ASGI server for FastAPI applications

### Development Tools
- **Vite**: Frontend build tool and development server
- **ESLint**: JavaScript/React code linting
- **PostCSS**: CSS processing with Tailwind
- **Python-dotenv**: Environment variable management

### Browser APIs
- **Web Speech API**: Browser-native speech recognition
- **MediaRecorder API**: Audio recording capabilities
- **Geolocation API**: Potential for location-based features