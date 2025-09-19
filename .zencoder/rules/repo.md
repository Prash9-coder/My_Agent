# AI English Tutor - Repository Information

## Project Overview
This is a full-stack web application that serves as an AI English Tutor for Telugu-speaking students. The system provides personalized English learning through voice and text conversations.

## Technology Stack
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Python FastAPI
- **Speech Services**: Google Cloud Speech-to-Text and Text-to-Speech APIs
- **Database**: SQLite (for development), PostgreSQL (for production)

## Key Features
1. Real-time English conversation practice
2. Immediate error correction with Telugu explanations
3. Grammar lessons and vocabulary building
4. Progress tracking and personalized learning paths
5. Voice recognition and speech synthesis
6. Role-play scenarios for practical learning

## Architecture
- Frontend handles user interface and speech integration
- Backend processes language learning logic and AI responses
- Google Cloud APIs handle speech-to-text and text-to-speech conversion
- Database stores user progress, lessons, and conversation history

## Core Components
1. **Speech Module**: Handles voice input/output
2. **Learning Engine**: AI logic for corrections and explanations
3. **Progress Tracker**: Monitors student improvement
4. **Content Manager**: Manages lessons, vocabulary, and exercises
5. **User Interface**: Interactive learning dashboard

## File Structure
```
/frontend - React application
/backend - FastAPI Python server
/shared - Common types and utilities
/docs - Documentation and API specs
```

## Development Setup
- Node.js for frontend development
- Python 3.8+ for backend
- Google Cloud credentials for speech services
- Environment variables for configuration