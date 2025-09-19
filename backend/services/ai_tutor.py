"""
AI English Tutor Service
Core teaching logic implementation
"""

import os
import re
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import google.generativeai as genai
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from models.schemas import (
    ChatResponse, Correction, Example, VerbForms, 
    VocabularyWord, Lesson, Exercise
)

logger = logging.getLogger(__name__)

class AITutorService:
    """
    AI English Tutor Service - Acts as a friendly human teacher
    for Telugu-speaking students learning English
    """
    
    def __init__(self):
        self.model = None
        self.student_contexts = {}  # Store conversation context per student
        self.grammar_rules = self._load_grammar_rules()
        self.common_mistakes = self._load_common_mistakes()
        self.vocabulary_bank = self._load_vocabulary_bank()
        
    async def initialize(self):
        """Initialize Google Gemini client and download required NLTK data"""
        try:
            # Initialize Gemini client
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
                self.model = genai.GenerativeModel(model_name)
                logger.info("✅ Google Gemini client initialized")
            else:
                logger.warning("⚠️ Gemini API key not found - using rule-based responses")
                
            # Download required NLTK data
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('wordnet', quiet=True)
                logger.info("✅ NLTK data downloaded")
            except Exception as e:
                logger.warning(f"⚠️ Could not download NLTK data: {e}")
                
        except Exception as e:
            logger.error(f"Error initializing AI tutor: {e}")
    
    async def process_message(self, message: str, student_id: str, is_voice: bool = False) -> ChatResponse:
        """
        Main method to process student messages and provide teaching responses
        """
        try:
            logger.info(f"Processing message for student {student_id}: {message}")
            
            # Clean and analyze the message
            cleaned_message = self._clean_message(message)
            analysis = await self._analyze_message(cleaned_message, student_id)
            
            # Determine if correction is needed
            corrections = []
            is_correct = analysis['is_correct']
            
            if not is_correct:
                corrections = await self._generate_corrections(
                    original_text=cleaned_message,
                    analysis=analysis,
                    student_id=student_id
                )
            
            # Generate examples
            examples = await self._generate_examples(
                message=cleaned_message,
                topic=analysis.get('topic'),
                student_level=analysis.get('student_level', 'beginner')
            )
            
            # Generate verb forms if relevant
            verb_forms = await self._extract_verb_forms(cleaned_message)
            
            # Generate encouragement and next suggestion
            encouragement = await self._generate_encouragement(
                is_correct=is_correct,
                student_id=student_id,
                corrections=corrections
            )
            
            # Generate pronunciation guide if voice-related
            pronunciation_guide = ""
            if is_voice or "pronunciation" in cleaned_message.lower() or "speak" in cleaned_message.lower():
                pronunciation_guide = await self._generate_pronunciation_guide(cleaned_message)
            
            next_suggestion = await self._generate_next_suggestion(
                student_id=student_id,
                current_message=cleaned_message,
                analysis=analysis
            )
            
            # Generate grammar tip if applicable
            grammar_tip = await self._generate_grammar_tip(analysis, corrections)
            
            # Update student context
            self._update_student_context(student_id, {
                'last_message': cleaned_message,
                'is_correct': is_correct,
                'corrections': corrections,
                'timestamp': datetime.now(),
                'is_voice': is_voice
            })
            
            return ChatResponse(
                is_correct=is_correct,
                corrections=corrections,
                examples=examples,
                verb_forms=verb_forms,
                encouragement=encouragement,
                next_suggestion=next_suggestion,
                grammar_tip=grammar_tip,
                pronunciation_guide=pronunciation_guide,
                student_level=analysis.get('student_level', 'beginner')
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._generate_error_response()
    
    async def _analyze_message(self, message: str, student_id: str) -> Dict:
        """Analyze student message for errors, level, and teaching opportunities"""
        try:
            # Basic linguistic analysis using TextBlob
            blob = TextBlob(message)
            
            # Check for common grammar errors
            errors = self._check_grammar_errors(message, blob)
            
            # Determine student level based on complexity and errors
            student_level = self._assess_student_level(message, errors)
            
            # Identify the topic/theme
            topic = self._identify_topic(message)
            
            return {
                'is_correct': len(errors) == 0,
                'errors': errors,
                'student_level': student_level,
                'topic': topic,
                'word_count': len(blob.words),
                'sentence_count': len(blob.sentences),
                'complexity_score': self._calculate_complexity(blob)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return {
                'is_correct': True,
                'errors': [],
                'student_level': 'beginner',
                'topic': 'general',
                'word_count': 0,
                'sentence_count': 0,
                'complexity_score': 0
            }
    
    def _check_grammar_errors(self, message: str, blob: TextBlob) -> List[Dict]:
        """Check for common grammar errors"""
        errors = []
        
        # Subject-verb agreement errors
        errors.extend(self._check_subject_verb_agreement(message, blob))
        
        # Tense errors
        errors.extend(self._check_tense_errors(message, blob))
        
        # Article errors (a, an, the)
        errors.extend(self._check_article_errors(message, blob))
        
        # Preposition errors
        errors.extend(self._check_preposition_errors(message, blob))
        
        # Capitalization errors
        errors.extend(self._check_capitalization_errors(message))
        
        # Punctuation errors
        errors.extend(self._check_punctuation_errors(message))
        
        return errors
    
    def _check_subject_verb_agreement(self, message: str, blob: TextBlob) -> List[Dict]:
        """Check for subject-verb agreement errors"""
        errors = []
        
        # Common patterns that Telugu speakers struggle with
        patterns = [
            (r'\bI am go\b', 'I am going', 'subject_verb_agreement'),
            (r'\bHe are\b', 'He is', 'subject_verb_agreement'),
            (r'\bShe are\b', 'She is', 'subject_verb_agreement'),
            (r'\bThey is\b', 'They are', 'subject_verb_agreement'),
            (r'\bI goes\b', 'I go', 'subject_verb_agreement'),
            (r'\bHe go\b', 'He goes', 'subject_verb_agreement'),
        ]
        
        for pattern, correction, error_type in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                match = re.search(pattern, message, re.IGNORECASE)
                errors.append({
                    'type': error_type,
                    'original': match.group(),
                    'corrected': correction,
                    'position': match.span()
                })
        
        return errors
    
    def _check_tense_errors(self, message: str, blob: TextBlob) -> List[Dict]:
        """Check for tense-related errors"""
        errors = []
        
        # Common tense mistakes by Telugu speakers
        patterns = [
            (r'\bI am went\b', 'I went', 'tense_error'),
            (r'\bI was go\b', 'I went', 'tense_error'),
            (r'\bI will went\b', 'I will go', 'tense_error'),
            (r'\bI have went\b', 'I have gone', 'tense_error'),
            (r'\byesterday I am\b', 'yesterday I was', 'tense_error'),
        ]
        
        for pattern, correction, error_type in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                match = re.search(pattern, message, re.IGNORECASE)
                errors.append({
                    'type': error_type,
                    'original': match.group(),
                    'corrected': correction,
                    'position': match.span()
                })
        
        return errors
    
    def _check_article_errors(self, message: str, blob: TextBlob) -> List[Dict]:
        """Check for article (a, an, the) errors"""
        errors = []
        
        # Basic article rules
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() == 'a' and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word and next_word[0] in 'aeiou':
                    errors.append({
                        'type': 'article_error',
                        'original': f'a {next_word}',
                        'corrected': f'an {next_word}',
                        'position': (i, i + 2)
                    })
        
        return errors
    
    def _check_preposition_errors(self, message: str, blob: TextBlob) -> List[Dict]:
        """Check for preposition errors"""
        errors = []
        
        # Common preposition mistakes
        patterns = [
            (r'\bon the morning\b', 'in the morning', 'preposition_error'),
            (r'\bin the night\b', 'at night', 'preposition_error'),
            (r'\bgo to school by walk\b', 'walk to school', 'preposition_error'),
            (r'\bmarried with\b', 'married to', 'preposition_error'),
        ]
        
        for pattern, correction, error_type in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                match = re.search(pattern, message, re.IGNORECASE)
                errors.append({
                    'type': error_type,
                    'original': match.group(),
                    'corrected': correction,
                    'position': match.span()
                })
        
        return errors
    
    def _check_capitalization_errors(self, message: str) -> List[Dict]:
        """Check for capitalization errors"""
        errors = []
        
        # Check if sentence starts with lowercase
        if message and message[0].islower():
            errors.append({
                'type': 'capitalization_error',
                'original': message[0],
                'corrected': message[0].upper(),
                'position': (0, 1),
                'rule': 'Sentences should start with a capital letter'
            })
        
        # Check for 'i' instead of 'I'
        words = message.split()
        for i, word in enumerate(words):
            if word == 'i':
                errors.append({
                    'type': 'capitalization_error',
                    'original': 'i',
                    'corrected': 'I',
                    'position': (i, i + 1),
                    'rule': 'The pronoun "I" should always be capitalized'
                })
        
        return errors
    
    def _check_punctuation_errors(self, message: str) -> List[Dict]:
        """Check for punctuation errors"""
        errors = []
        
        # Check if sentence ends with punctuation
        if message and message[-1] not in '.!?':
            errors.append({
                'type': 'punctuation_error',
                'original': message,
                'corrected': message + '.',
                'position': (len(message), len(message)),
                'rule': 'Sentences should end with punctuation'
            })
        
        return errors
    
    async def _generate_corrections(self, original_text: str, analysis: Dict, student_id: str) -> List[Correction]:
        """Generate detailed corrections with explanations"""
        corrections = []
        
        for error in analysis.get('errors', []):
            # Generate Telugu explanation
            telugu_explanation = self._get_telugu_explanation(error['type'], error)
            
            # Generate English explanation
            english_explanation = self._get_english_explanation(error['type'], error)
            
            correction = Correction(
                original_text=error['original'],
                corrected_text=error['corrected'],
                mistake_type=error['type'],
                explanation_english=english_explanation,
                explanation_telugu=telugu_explanation,
                position_start=error['position'][0] if 'position' in error else 0,
                position_end=error['position'][1] if 'position' in error else len(error['original'])
            )
            
            corrections.append(correction)
        
        return corrections
    
    def _get_telugu_explanation(self, error_type: str, error: Dict) -> str:
        """Get Telugu explanation for different error types"""
        telugu_explanations = {
            'subject_verb_agreement': f"కర్త మరియు క్రియ మధ్య సరైన అనుసంధానం లేదు. '{error['original']}' బదులు '{error['corrected']}' వాడండి.",
            'tense_error': f"కాలం తప్పుగా ఉంది. '{error['original']}' బదులు '{error['corrected']}' సరైనది.",
            'article_error': f"ఆర్టికల్ తప్పు. స్వర ధ్వనితో మొదలయ్యే పదాల ముందు 'an' వాడండి.",
            'preposition_error': f"ప్రిపోజిషన్ తప్పు. '{error['original']}' బదులు '{error['corrected']}' వాడండి.",
            'capitalization_error': f"పెద్దక్షరం వాడాల్సిన చోట వాడలేదు. '{error['original']}' బదులు '{error['corrected']}' రాయండి.",
            'punctuation_error': "వాక్యం చివర విరామ చిహ్నం ఉండాలి."
        }
        
        return telugu_explanations.get(error_type, "వ్యాకరణ తప్పు ఉంది. దయచేసి సరిచేసుకోండి.")
    
    def _get_english_explanation(self, error_type: str, error: Dict) -> str:
        """Get English explanation for different error types"""
        english_explanations = {
            'subject_verb_agreement': f"The subject and verb don't agree. Use '{error['corrected']}' instead of '{error['original']}'.",
            'tense_error': f"Wrong tense used. The correct form is '{error['corrected']}' instead of '{error['original']}'.",
            'article_error': "Use 'an' before words starting with vowel sounds (a, e, i, o, u).",
            'preposition_error': f"Wrong preposition. Use '{error['corrected']}' instead of '{error['original']}'.",
            'capitalization_error': f"Always capitalize '{error['corrected']}'. It should be '{error['corrected']}' not '{error['original']}'.",
            'punctuation_error': "Every sentence should end with a punctuation mark (. ! ?)."
        }
        
        return english_explanations.get(error_type, f"Grammar error: use '{error['corrected']}' instead of '{error['original']}'.")
    
    async def _generate_examples(self, message: str, topic: str, student_level: str) -> List[Example]:
        """Generate relevant examples for the student with AI enhancement when available"""
        # Try AI-generated examples first
        if self.model and topic and topic != 'general':
            ai_examples = await self._generate_ai_examples(topic, student_level)
            if ai_examples:
                return ai_examples
        
        # Fallback to predefined examples
        examples = []
        
        # Get examples based on topic and level
        if topic == 'greetings':
            examples = [
                Example(english="Hello, how are you?", telugu="హలో, మీరు ఎలా ఉన్నారు?"),
                Example(english="Good morning!", telugu="శుభోదయం!"),
                Example(english="Nice to meet you.", telugu="మిమ్మల్ని కలవడం ఆనందంగా ఉంది.")
            ]
        elif topic == 'time':
            examples = [
                Example(english="What time is it?", telugu="ఇప్పుడు ఎంత సమయం?"),
                Example(english="It's 3 o'clock.", telugu="ఇప్పుడు 3 గంటలు."),
                Example(english="I wake up at 7 AM.", telugu="నేను ఉదయం 7 గంటలకు లేస్తాను.")
            ]
        else:
            # General examples based on student level
            if student_level == 'beginner':
                examples = [
                    Example(english="I like to read books.", telugu="నాకు పుస్తకాలు చదవడం ఇష్టం."),
                    Example(english="She is a good student.", telugu="ఆమె మంచి విద్యార్థి."),
                ]
            else:
                examples = [
                    Example(english="I enjoy learning new languages.", telugu="కొత్త భాషలు నేర్చుకోవడం నాకు ఆనందం."),
                    Example(english="Practice makes perfect.", telugu="అభ్యాసం వల్ల పరిపూర్ణత వస్తుంది."),
                ]
        
        return examples[:3]  # Return max 3 examples
    
    async def _extract_verb_forms(self, message: str) -> Optional[VerbForms]:
        """Extract and provide verb forms if a verb is found in the message"""
        try:
            blob = TextBlob(message)
            
            # Find verbs in the message
            verbs = [word for word, pos in blob.tags if pos.startswith('VB')]
            
            if verbs:
                # Take the first verb and provide its forms
                base_verb = verbs[0].lower()
                
                # Common irregular verbs mapping
                irregular_verbs = {
                    'go': {'past': 'went', 'past_participle': 'gone'},
                    'come': {'past': 'came', 'past_participle': 'come'},
                    'see': {'past': 'saw', 'past_participle': 'seen'},
                    'do': {'past': 'did', 'past_participle': 'done'},
                    'have': {'past': 'had', 'past_participle': 'had'},
                    'be': {'past': 'was/were', 'past_participle': 'been'},
                    'eat': {'past': 'ate', 'past_participle': 'eaten'},
                    'drink': {'past': 'drank', 'past_participle': 'drunk'},
                    'write': {'past': 'wrote', 'past_participle': 'written'},
                    'read': {'past': 'read', 'past_participle': 'read'},
                }
                
                if base_verb in irregular_verbs:
                    return VerbForms(
                        base_form=base_verb,
                        past_simple=irregular_verbs[base_verb]['past'],
                        past_participle=irregular_verbs[base_verb]['past_participle'],
                        present_participle=base_verb + 'ing',
                        third_person=base_verb + 's'
                    )
                else:
                    # Regular verb
                    return VerbForms(
                        base_form=base_verb,
                        past_simple=base_verb + 'ed',
                        past_participle=base_verb + 'ed',
                        present_participle=base_verb + 'ing',
                        third_person=base_verb + 's'
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting verb forms: {e}")
            return None
    
    async def _generate_encouragement(self, is_correct: bool, student_id: str, corrections: List[Correction]) -> str:
        """Generate encouraging messages with AI enhancement when available"""
        # Try AI-generated encouragement first
        if self.model:
            student_context = self.student_contexts.get(student_id, [])
            level = student_context[-1].get('student_level', 'beginner') if student_context else 'beginner'
            context = f"{'Correct' if is_correct else 'Incorrect with ' + str(len(corrections)) + ' errors'}"
            
            ai_encouragement = await self._generate_ai_encouragement(is_correct, level, context)
            if ai_encouragement:
                return ai_encouragement
        
        # Fallback to predefined encouragements
        if is_correct:
            encouragements = [
                "Excellent! Your sentence is perfect! 🌟 మీ వాక్యం చాలా సరిగా ఉంది!",
                "Great job! Keep practicing like this! 👏 ఇలాగే అభ్యాసం కొనసాగించండి!",
                "Perfect grammar! You're improving! ✨ మీ వ్యాకరణం చాలా బాగుంది!",
                "Well done! Your English is getting better! 🎉 మీ ఇంగ్లీష్ మెరుగుపడుతోంది!"
            ]
        else:
            encouragements = [
                "Good try! Mistakes help us learn. 💪 తప్పులు మనల్ని నేర్పుతాయి!",
                "Don't worry, practice makes perfect! 🌱 చింతించకండి, అభ్యాసం వల్ల పరిపూర్ణత వస్తుంది!",
                "Keep trying! You're learning well! 🚀 ప్రయత్నం కొనసాగించండి!",
                "Mistakes are normal when learning! 📚 నేర్చుకునేటప్పుడు తప్పులు సహజం!"
            ]
        
        import random
        return random.choice(encouragements)
    
    async def _generate_next_suggestion(self, student_id: str, current_message: str, analysis: Dict) -> str:
        """Suggest what the student should practice next with AI enhancement when available"""
        # Try AI-generated suggestion first
        if self.model:
            student_level = analysis.get('student_level', 'beginner')
            ai_suggestion = await self._generate_ai_next_suggestion(current_message, student_level)
            if ai_suggestion:
                return ai_suggestion
        
        # Fallback to predefined suggestions
        suggestions = [
            "Try forming a question using 'What', 'Where', or 'How'.",
            "Practice using past tense verbs in your next sentence.",
            "Try describing something you did yesterday.",
            "Make a sentence using 'I am going to...'",
            "Practice introducing yourself to someone new.",
            "Try using 'There is' or 'There are' in a sentence."
        ]
        
        import random
        return random.choice(suggestions)
    
    async def _generate_grammar_tip(self, analysis: Dict, corrections: List[Correction]) -> Optional[str]:
        """Generate relevant grammar tips"""
        if corrections:
            error_types = [c.mistake_type for c in corrections]
            
            if 'subject_verb_agreement' in error_types:
                return "💡 Grammar Tip: Subject and verb must agree. 'I am', 'He is', 'They are'."
            elif 'tense_error' in error_types:
                return "💡 Grammar Tip: Use correct tense - Past: 'I went', Present: 'I go', Future: 'I will go'."
            elif 'article_error' in error_types:
                return "💡 Grammar Tip: Use 'a' before consonants, 'an' before vowels. 'A book', 'An apple'."
        
        return None
    
    async def _generate_pronunciation_guide(self, message: str) -> str:
        """Generate pronunciation guidance using AI"""
        if not self.model:
            # Fallback pronunciation tips
            return "💡 Pronunciation tip: Focus on clear vowel sounds and word stress. Practice slowly first, then increase speed."
        
        try:
            prompt = f"""
            Create a pronunciation guide for Telugu speakers learning English.
            
            Text to help with: "{message}"
            
            Provide:
            1. Key sounds that Telugu speakers find difficult in this text
            2. Simple phonetic spelling (like "THEE-nk" for "think")  
            3. Telugu approximation where helpful
            4. Specific tips for mouth/tongue position
            
            Keep it concise and practical for a beginner.
            """
            
            response = await self.model.generate_content_async(prompt)
            
            if response and response.text:
                return f"🗣️ Pronunciation Guide: {response.text.strip()}"
            else:
                return "💡 Pronunciation tip: Focus on clear vowel sounds and word stress. Practice slowly first!"
                
        except Exception as e:
            logger.warning(f"Could not generate pronunciation guide: {e}")
            return "💡 Pronunciation tip: Focus on clear vowel sounds and word stress. Practice slowly first!"
    
    def _assess_student_level(self, message: str, errors: List[Dict]) -> str:
        """Assess student's English level based on message complexity and errors"""
        word_count = len(message.split())
        error_ratio = len(errors) / max(word_count, 1)
        
        if error_ratio > 0.3 or word_count < 5:
            return 'beginner'
        elif error_ratio > 0.1 or word_count < 15:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _identify_topic(self, message: str) -> str:
        """Identify the topic/theme of the message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'good morning', 'how are you']):
            return 'greetings'
        elif any(word in message_lower for word in ['time', 'clock', 'hour', 'minute']):
            return 'time'
        elif any(word in message_lower for word in ['food', 'eat', 'drink', 'hungry']):
            return 'food'
        elif any(word in message_lower for word in ['school', 'study', 'learn', 'book']):
            return 'education'
        else:
            return 'general'
    
    def _calculate_complexity(self, blob: TextBlob) -> float:
        """Calculate complexity score of the message"""
        avg_word_length = sum(len(word) for word in blob.words) / max(len(blob.words), 1)
        avg_sentence_length = len(blob.words) / max(len(blob.sentences), 1)
        
        return (avg_word_length * 0.3) + (avg_sentence_length * 0.7)
    
    def _clean_message(self, message: str) -> str:
        """Clean and normalize the message"""
        # Remove extra whitespace
        message = ' '.join(message.split())
        
        # Basic cleaning
        message = message.strip()
        
        return message
    
    def _update_student_context(self, student_id: str, context: Dict):
        """Update conversation context for the student"""
        if student_id not in self.student_contexts:
            self.student_contexts[student_id] = []
        
        self.student_contexts[student_id].append(context)
        
        # Keep only last 10 messages
        if len(self.student_contexts[student_id]) > 10:
            self.student_contexts[student_id] = self.student_contexts[student_id][-10:]
    
    def _generate_error_response(self) -> ChatResponse:
        """Generate error response when something goes wrong"""
        return ChatResponse(
            is_correct=True,
            corrections=[],
            examples=[],
            verb_forms=None,
            encouragement="Sorry, I had trouble understanding. Please try again! క్షమించండి, అర్థం చేసుకోవడంలో సమస్య. దయచేసి మళ్ళీ ప్రయత్నించండి!",
            next_suggestion="Try typing a simple sentence about yourself.",
            grammar_tip=None,
            student_level='beginner'
        )
    
    def _load_grammar_rules(self) -> Dict:
        """Load grammar rules and patterns"""
        # This would typically load from a file or database
        return {}
    
    def _load_common_mistakes(self) -> Dict:
        """Load common mistakes made by Telugu speakers"""
        # This would typically load from a file or database
        return {}
    
    def _load_vocabulary_bank(self) -> Dict:
        """Load vocabulary bank with Telugu translations"""
        # This would typically load from a file or database
        return {}
    
    async def generate_lesson(self, student_id: str, lesson_type: str, duration_minutes: int) -> Dict:
        """Generate a personalized lesson using AI and fallback templates"""
        
        # Try to generate dynamic content using Gemini AI first
        if self.model:
            try:
                # Get student context for personalization
                student_context = self.student_contexts.get(student_id, [])
                recent_mistakes = []
                if student_context:
                    recent_mistakes = [ctx.get('corrections', []) for ctx in student_context[-3:]]
                    recent_mistakes = [mistake for sublist in recent_mistakes for mistake in sublist]

                # Create personalized prompt
                prompt = f"""
                Create an English lesson for a Telugu-speaking student. 
                Lesson Type: {lesson_type}
                Duration: {duration_minutes} minutes
                
                Student's Recent Mistakes: {recent_mistakes[:5] if recent_mistakes else "None yet"}
                
                Please create a JSON response with this structure:
                {{
                    "title": "Engaging lesson title",
                    "explanation_english": "Clear explanation in English",
                    "explanation_telugu": "Telugu translation and explanation",
                    "key_points": ["Point 1", "Point 2", "Point 3", "Point 4"],
                    "examples": [
                        {{"english": "Example sentence", "telugu": "Telugu translation"}},
                        {{"english": "Another example", "telugu": "Telugu translation"}}
                    ]
                }}
                
                Focus on:
                - Common mistakes Telugu speakers make in English
                - Practical, everyday usage
                - Clear explanations suitable for beginners
                - Include Telugu script for better understanding
                """

                response = await self.model.generate_content_async(prompt)
                
                if response and response.text:
                    try:
                        # Clean the response and parse JSON
                        response_text = response.text.strip()
                        if response_text.startswith('```json'):
                            response_text = response_text[7:-3]
                        elif response_text.startswith('```'):
                            response_text = response_text[3:-3]
                            
                        import json
                        ai_content = json.loads(response_text)
                        
                        return {
                            "lesson_id": f"{student_id}_{lesson_type}_{datetime.now().timestamp()}",
                            "lesson_type": lesson_type,
                            "estimated_duration": duration_minutes,
                            "content": ai_content,
                            "generated_by": "ai"
                        }
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Could not parse AI response for lesson, using fallback: {e}")
                        
            except Exception as e:
                logger.warning(f"AI lesson generation failed, using fallback: {e}")
        
        # Fallback to static templates if AI fails
        lesson_content = {
            "grammar": {
                "title": "English Grammar Fundamentals",
                "explanation_english": "Learn essential grammar rules including verb tenses, sentence structure, and proper word order. This lesson focuses on present tense and basic sentence construction.",
                "explanation_telugu": "క్రియాపదాల కాలాలు, వాక్య నిర్మాణం మరియు సరైన పద క్రమంతో సహా అవసరమైన వ్యాకరణ నియమాలను నేర్చుకోండి.",
                "key_points": [
                    "Subject-Verb-Object sentence structure",
                    "Present tense verb forms (I am, You are, He/She is)",
                    "Common grammar patterns in English",
                    "Difference between 'a' and 'an' articles"
                ],
                "examples": [
                    {"english": "I am a student.", "telugu": "నేను విద్యార్థిని."},
                    {"english": "She reads books daily.", "telugu": "ఆమె రోజూ పుస్తకాలు చదువుతుంది."},
                    {"english": "They are playing cricket.", "telugu": "వారు క్రికెట్ ఆడుతున్నారు."}
                ]
            },
            "vocabulary": {
                "title": "Daily Life Vocabulary",
                "explanation_english": "Build your vocabulary with commonly used English words in daily life situations. Learn words for family, home, work, and everyday activities.",
                "explanation_telugu": "దైనందిన జీవిత పరిస్థితులలో సాధారణంగా ఉపయోగించే ఇంగ్లీష్ పదాలతో మీ వల్లెభువును పెంచుకోండి.",
                "key_points": [
                    "Family members: mother, father, brother, sister",
                    "Home items: table, chair, bed, kitchen",
                    "Daily activities: eat, sleep, work, study",
                    "Time expressions: morning, afternoon, evening"
                ],
                "examples": [
                    {"english": "My mother cooks delicious food.", "telugu": "మా అమ్మ రుచికరమైన ఆహారం వండుతుంది."},
                    {"english": "I study in the evening.", "telugu": "నేను సాయంత్రం చదువుకుంటాను."},
                    {"english": "The book is on the table.", "telugu": "పుస్తకం టేబుల్ మీద ఉంది."}
                ]
            },
            "conversation": {
                "title": "Basic Conversation Skills",
                "explanation_english": "Learn how to have simple conversations in English. Practice greetings, introductions, and basic questions and answers.",
                "explanation_telugu": "ఇంగ్లీష్‌లో సరళమైన సంభాషణలు ఎలా చేయాలో నేర్చుకోండి. వందనలు, పరిచయాలు మరియు ప్రాథమిక ప్రశ్నలు మరియు సమాధానాలను అభ్యసించండి.",
                "key_points": [
                    "Greetings: Hello, Good morning, How are you?",
                    "Introductions: My name is..., I am from...",
                    "Polite expressions: Please, Thank you, Excuse me",
                    "Basic questions: What, Where, When, How"
                ],
                "examples": [
                    {"english": "Hello, how are you today?", "telugu": "హలో, ఈరోజు మీరు ఎలా ఉన్నారు?"},
                    {"english": "My name is Ravi. Nice to meet you.", "telugu": "నా పేరు రవి. మిమ్మల్ని కలవడం ఆనందంగా ఉంది."},
                    {"english": "Where are you from?", "telugu": "మీరు ఎక్కడినుంచి వచ్చారు?"}
                ]
            },
            "pronunciation": {
                "title": "English Pronunciation Guide",
                "explanation_english": "Improve your English pronunciation with focus on common sounds that Telugu speakers find challenging.",
                "explanation_telugu": "తెలుగు మాట్లాడేవారికి కష్టంగా అనిపించే సాధారణ ధ్వనులపై దృష్టి సారించి మీ ఇంగ్లీష్ ఉచ్చారణను మెరుగుపరచుకోండి.",
                "key_points": [
                    "TH sound: 'th' as in 'think' and 'this'",
                    "W vs V sounds: 'water' vs 'very'",
                    "R sound: 'red', 'right', 'around'",
                    "Silent letters: 'k' in 'know', 'b' in 'lamb'"
                ],
                "examples": [
                    {"english": "Think before you speak.", "telugu": "మాట్లాడే ముందు ఆలోచించండి."},
                    {"english": "Water is very important.", "telugu": "నీరు చాలా ముఖ్యం."},
                    {"english": "I know the right answer.", "telugu": "నాకు సరైన జవాబు తెలుసు."}
                ]
            },
            "writing": {
                "title": "Basic English Writing",
                "explanation_english": "Learn to write simple sentences and paragraphs in English. Focus on proper sentence structure and basic punctuation.",
                "explanation_telugu": "ఇంగ్లీష్‌లో సరళమైన వాక్యాలు మరియు పేరాగ్రాఫ్‌లు ఎలా వ్రాయాలో నేర్చుకోండి. సరైన వాక్య నిర్మాణం మరియు ప్రాథమిక విరామచిహ్నాలపై దృష్టి పెట్టండి.",
                "key_points": [
                    "Start sentences with capital letters",
                    "End sentences with periods (.), questions with (?)",
                    "Use commas (,) to separate items in a list",
                    "Keep sentences simple and clear"
                ],
                "examples": [
                    {"english": "I like apples, oranges, and bananas.", "telugu": "నాకు యాపిల్స్, ఆరెంజ్‌లు మరియు అరటిపండ్లు అంటే ఇష్టం."},
                    {"english": "What is your favorite color?", "telugu": "మీకు ఇష్టమైన రంగు ఏది?"},
                    {"english": "The weather is nice today.", "telugu": "ఈరోజు వాతావరణం బాగుంది."}
                ]
            }
        }
        
        content = lesson_content.get(lesson_type, lesson_content["grammar"])
        
        return {
            "lesson_id": f"{student_id}_{lesson_type}_{datetime.now().timestamp()}",
            "lesson_type": lesson_type,
            "estimated_duration": duration_minutes,
            "content": content,
            "generated_by": "template"
        }
    
    async def generate_exercise(self, student_id: str, exercise_type: str, difficulty: str) -> Dict:
        """Generate practice exercises using AI and fallback templates"""
        
        # Try to generate dynamic exercises using Gemini AI first
        if self.model:
            try:
                # Get student context for personalization
                student_context = self.student_contexts.get(student_id, [])
                recent_mistakes = []
                if student_context:
                    recent_mistakes = [ctx.get('corrections', []) for ctx in student_context[-3:]]
                    recent_mistakes = [mistake for sublist in recent_mistakes for mistake in sublist if mistake]

                # Create personalized prompt for exercises
                prompt = f"""
                Create 3 English practice exercises for a Telugu-speaking student.
                Exercise Type: {exercise_type}
                Difficulty: {difficulty}
                
                Student's Recent Mistakes: {recent_mistakes[:3] if recent_mistakes else "None yet - create general exercises"}
                
                Please create a JSON response with this structure:
                {{
                    "exercises": [
                        {{
                            "exercise_id": "ex_1",
                            "question": "Clear question text",
                            "options": ["option1", "option2", "option3", "option4"],
                            "correct_answer": "correct option",
                            "explanation": "Why this is correct, with Telugu explanation if helpful"
                        }},
                        {{
                            "exercise_id": "ex_2",
                            "question": "Another question",
                            "options": ["option1", "option2", "option3", "option4"],
                            "correct_answer": "correct option",
                            "explanation": "Clear explanation"
                        }},
                        {{
                            "exercise_id": "ex_3",
                            "question": "Third question",
                            "options": ["option1", "option2", "option3", "option4"],
                            "correct_answer": "correct option",
                            "explanation": "Detailed explanation"
                        }}
                    ]
                }}
                
                Focus on:
                - Common errors Telugu speakers make
                - {difficulty} level appropriate content
                - Clear explanations with reasoning
                - Practical, everyday English usage
                """

                response = await self.model.generate_content_async(prompt)
                
                if response and response.text:
                    try:
                        # Clean the response and parse JSON
                        response_text = response.text.strip()
                        if response_text.startswith('```json'):
                            response_text = response_text[7:-3]
                        elif response_text.startswith('```'):
                            response_text = response_text[3:-3]
                            
                        import json
                        ai_exercises = json.loads(response_text)
                        
                        # Add unique IDs and timestamp
                        for i, exercise in enumerate(ai_exercises.get("exercises", [])):
                            exercise["exercise_id"] = f"ai_ex_{datetime.now().timestamp()}_{i}"
                        
                        ai_exercises["generated_by"] = "ai"
                        return ai_exercises
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Could not parse AI response for exercises, using fallback: {e}")
                        
            except Exception as e:
                logger.warning(f"AI exercise generation failed, using fallback: {e}")
        
        # Fallback to static templates if AI fails
        exercise_templates = {
            "fill_blanks": {
                "beginner": [
                    {
                        "question": "Fill in the blank: 'I ___ a student.'",
                        "options": ["am", "is", "are", "be"],
                        "correct_answer": "am",
                        "explanation": "Use 'am' with 'I'. Remember: I am, You are, He/She is."
                    },
                    {
                        "question": "Choose the correct article: 'I have ___ apple.'",
                        "options": ["a", "an", "the", "no article"],
                        "correct_answer": "an",
                        "explanation": "Use 'an' before words that start with vowel sounds (a, e, i, o, u)."
                    },
                    {
                        "question": "Fill in the blank: 'She ___ to school every day.'",
                        "options": ["go", "goes", "going", "went"],
                        "correct_answer": "goes",
                        "explanation": "Use 'goes' with 'She/He/It' in present tense. Add 's' to the verb."
                    }
                ],
                "intermediate": [
                    {
                        "question": "Choose the correct tense: 'I have ___ this book before.'",
                        "options": ["read", "reading", "reads", "to read"],
                        "correct_answer": "read",
                        "explanation": "Present perfect tense: 'have + past participle'. Past participle of 'read' is 'read'."
                    },
                    {
                        "question": "Fill in the blank: 'If I ___ rich, I would help the poor.'",
                        "options": ["am", "was", "were", "will be"],
                        "correct_answer": "were",
                        "explanation": "In conditional sentences (unreal situations), use 'were' with all subjects."
                    }
                ]
            },
            "multiple_choice": {
                "beginner": [
                    {
                        "question": "What is the plural of 'child'?",
                        "options": ["childs", "children", "childes", "child"],
                        "correct_answer": "children",
                        "explanation": "'Child' has an irregular plural form: 'children'."
                    },
                    {
                        "question": "Which sentence is correct?",
                        "options": [
                            "I am going to home",
                            "I am going home", 
                            "I am going to the home",
                            "I going home"
                        ],
                        "correct_answer": "I am going home",
                        "explanation": "Don't use 'to' with 'home'. Simply say 'going home'."
                    }
                ],
                "intermediate": [
                    {
                        "question": "Which preposition is correct: 'I have been waiting ___ you for an hour.'?",
                        "options": ["to", "for", "with", "at"],
                        "correct_answer": "for",
                        "explanation": "Use 'wait for' someone or something. 'For' shows the object of waiting."
                    }
                ]
            },
            "grammar_check": {
                "beginner": [
                    {
                        "question": "Find the mistake: 'He don't like coffee.'",
                        "options": [
                            "He doesn't like coffee.",
                            "He not like coffee.", 
                            "He don't likes coffee.",
                            "No mistake"
                        ],
                        "correct_answer": "He doesn't like coffee.",
                        "explanation": "With 'He/She/It', use 'doesn't' (does not), not 'don't' (do not)."
                    },
                    {
                        "question": "Correct this sentence: 'I am liking this book.'",
                        "options": [
                            "I like this book.",
                            "I am like this book.",
                            "I liked this book.",
                            "No correction needed"
                        ],
                        "correct_answer": "I like this book.",
                        "explanation": "State verbs like 'like, love, hate' are not used in continuous tense."
                    }
                ]
            }
        }
        
        # Get exercises based on type and difficulty
        exercises_pool = exercise_templates.get(exercise_type, exercise_templates["fill_blanks"])
        difficulty_exercises = exercises_pool.get(difficulty, exercises_pool["beginner"])
        
        # Generate unique exercise IDs and return random selection
        import random
        selected_exercises = random.sample(difficulty_exercises, min(3, len(difficulty_exercises)))
        
        for i, exercise in enumerate(selected_exercises):
            exercise["exercise_id"] = f"ex_{datetime.now().timestamp()}_{i}"
        
        return {
            "exercises": selected_exercises,
            "generated_by": "template"
        }
    
    async def get_daily_vocabulary(self) -> Dict:
        """Get daily vocabulary words with Telugu translations"""
        words = [
            VocabularyWord(
                word="practice",
                meaning_telugu="అభ్యాసం",
                part_of_speech="verb",
                pronunciation="/ˈpræktɪs/",
                examples=[
                    Example(english="I practice English every day.", telugu="నేను ప్రతిరోజూ ఇంగ్లీష్ అభ్యసిస్తాను."),
                    Example(english="Practice makes perfect.", telugu="అభ్యాసం వల్ల పరిపూర్ణత వస్తుంది.")
                ]
            ).dict(),
            VocabularyWord(
                word="learn",
                meaning_telugu="నేర్చుకోవడం",
                part_of_speech="verb", 
                pronunciation="/lɜːrn/",
                examples=[
                    Example(english="I want to learn English.", telugu="నాకు ఇంగ్లీష్ నేర్చుకోవాలని ఉంది."),
                    Example(english="Children learn quickly.", telugu="పిల్లలు త్వరగా నేర్చుకుంటారు.")
                ]
            ).dict()
        ]
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "theme": "Learning and Practice",
            "words": words
        }
    
    async def translate_with_explanation(self, text: str, source_language: str, target_language: str) -> Dict:
        """Translate text with detailed explanations"""
        # Placeholder implementation
        if source_language == "telugu" and target_language == "english":
            return {
                "original_text": text,
                "translated_text": "English translation here",
                "explanation": "Grammar structure explanation",
                "word_breakdown": []
            }
        
        return {
            "original_text": text,
            "translated_text": "Translation not available",
            "explanation": "Translation service temporarily unavailable",
            "word_breakdown": []
        }
    
    async def _generate_ai_correction(self, original_text: str, error_type: str) -> Optional[Dict]:
        """Use Gemini AI to generate enhanced corrections"""
        if not self.model:
            return None
            
        try:
            prompt = f"""
            As an English tutor for Telugu-speaking students, help correct this sentence:
            Original: "{original_text}"
            Error type: {error_type}
            
            Please provide:
            1. Corrected sentence
            2. Brief explanation in English
            3. Explanation in Telugu
            4. A simple example
            
            Format as JSON:
            {{
                "corrected": "corrected sentence",
                "explanation_english": "explanation in English",
                "explanation_telugu": "explanation in Telugu script",
                "example": "simple example sentence"
            }}
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI correction: {e}")
            return None
    
    async def _generate_ai_examples(self, topic: str, level: str) -> List[Example]:
        """Use Gemini AI to generate contextual examples"""
        if not self.model:
            return []
            
        try:
            prompt = f"""
            Generate 3 English sentences with Telugu translations for a {level} level student learning about {topic}.
            
            Format as JSON array:
            [
                {{
                    "english": "English sentence",
                    "telugu": "Telugu translation"
                }},
                ...
            ]
            
            Make sentences practical and useful for Telugu speakers learning English.
            """
            
            response = self.model.generate_content(prompt)
            examples_data = json.loads(response.text)
            
            examples = []
            for item in examples_data:
                examples.append(Example(
                    english=item["english"],
                    telugu=item["telugu"]
                ))
            
            return examples[:3]  # Limit to 3 examples
            
        except Exception as e:
            logger.error(f"Error generating AI examples: {e}")
            return []
    
    async def _generate_ai_encouragement(self, is_correct: bool, student_level: str, context: str) -> str:
        """Use Gemini AI to generate personalized encouragement"""
        if not self.model:
            return self._get_default_encouragement(is_correct)
            
        try:
            prompt = f"""
            Generate encouraging feedback for a {student_level} Telugu-speaking English learner.
            Context: {"Correct sentence" if is_correct else "Incorrect sentence with errors"}
            Additional context: {context}
            
            Provide encouragement in both English and Telugu. Be supportive and motivating.
            Keep it brief (1-2 sentences max).
            
            Format: "English encouragement. Telugu encouragement."
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI encouragement: {e}")
            return self._get_default_encouragement(is_correct)
    
    async def _generate_ai_next_suggestion(self, current_message: str, student_level: str) -> str:
        """Use Gemini AI to generate next learning suggestions"""
        if not self.model:
            return "Try making another sentence about your daily routine."
            
        try:
            prompt = f"""
            Based on this student message: "{current_message}"
            Student level: {student_level}
            
            Suggest what the student should practice next. Make it specific and actionable.
            Focus on gradual improvement appropriate for their level.
            
            Keep suggestion brief (1 sentence) and encouraging.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI suggestion: {e}")
            return "Try making another sentence about your daily routine."
    
    def _get_default_encouragement(self, is_correct: bool) -> str:
        """Fallback encouragement when AI is not available"""
        if is_correct:
            return "Great job! Keep practicing! బాగుంది! అభ్యాసం కొనసాగించండి!"
        else:
            return "Good effort! Let's learn from this mistake. మంచి ప్రయత్నం! ఈ తప్పు నుండి నేర్చుకుందాం."