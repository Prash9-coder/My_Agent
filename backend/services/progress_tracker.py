"""
Progress Tracker Service
Tracks student learning progress, mistakes, and improvements
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
from models.schemas import StudentProgress, Correction

logger = logging.getLogger(__name__)

class ProgressTracker:
    """
    Service for tracking student learning progress and analytics
    """
    
    def __init__(self):
        # In-memory storage for development - in production use database
        self.student_data = defaultdict(lambda: {
            'conversations': [],
            'mistakes': [],
            'corrections': [],
            'daily_stats': defaultdict(lambda: {
                'sentences': 0,
                'correct_sentences': 0,
                'mistakes': 0,
                'topics_covered': set(),
                'session_time': 0
            }),
            'weekly_stats': defaultdict(lambda: {
                'total_sentences': 0,
                'accuracy': 0.0,
                'improvement_areas': [],
                'achievements': []
            }),
            'overall_stats': {
                'total_conversations': 0,
                'total_sentences': 0,
                'correct_sentences': 0,
                'start_date': None,
                'last_activity': None,
                'current_level': 'beginner',
                'streak_days': 0
            }
        })
        
    async def update_progress(
        self, 
        student_id: str, 
        message: str, 
        corrections: List[Correction], 
        is_correct: bool
    ):
        """Update student progress with new conversation data"""
        try:
            current_date = datetime.now().date()
            current_time = datetime.now()
            
            student = self.student_data[student_id]
            
            # Update overall stats
            if student['overall_stats']['start_date'] is None:
                student['overall_stats']['start_date'] = current_time
            
            student['overall_stats']['last_activity'] = current_time
            student['overall_stats']['total_sentences'] += 1
            student['overall_stats']['total_conversations'] += 1
            
            if is_correct:
                student['overall_stats']['correct_sentences'] += 1
            
            # Update daily stats
            daily_key = current_date.isoformat()
            daily_stats = student['daily_stats'][daily_key]
            daily_stats['sentences'] += 1
            
            if is_correct:
                daily_stats['correct_sentences'] += 1
            else:
                daily_stats['mistakes'] += len(corrections)
                
                # Store mistake details
                for correction in corrections:
                    mistake_record = {
                        'date': current_time,
                        'original_text': correction.original_text,
                        'corrected_text': correction.corrected_text,
                        'mistake_type': correction.mistake_type,
                        'explanation_english': correction.explanation_english,
                        'explanation_telugu': correction.explanation_telugu,
                        'message_context': message
                    }
                    student['mistakes'].append(mistake_record)
            
            # Store conversation record
            conversation_record = {
                'timestamp': current_time,
                'message': message,
                'is_correct': is_correct,
                'corrections': [c.dict() for c in corrections],
                'word_count': len(message.split()),
                'complexity_estimated': self._estimate_complexity(message)
            }
            student['conversations'].append(conversation_record)
            
            # Update streak
            await self._update_streak(student_id, current_date)
            
            # Update level assessment
            await self._update_level_assessment(student_id)
            
            logger.info(f"Updated progress for student {student_id}")
            
        except Exception as e:
            logger.error(f"Error updating progress for {student_id}: {e}")
    
    async def get_student_progress(self, student_id: str) -> StudentProgress:
        """Get comprehensive progress data for a student"""
        try:
            student = self.student_data[student_id]
            overall = student['overall_stats']
            
            # Calculate accuracy
            accuracy = 0.0
            if overall['total_sentences'] > 0:
                accuracy = (overall['correct_sentences'] / overall['total_sentences']) * 100
            
            # Get recent performance
            recent_conversations = student['conversations'][-20:]  # Last 20 conversations
            recent_accuracy = 0.0
            if recent_conversations:
                recent_correct = sum(1 for conv in recent_conversations if conv['is_correct'])
                recent_accuracy = (recent_correct / len(recent_conversations)) * 100
            
            # Analyze strengths and weaknesses
            strengths = await self._analyze_strengths(student_id)
            areas_for_improvement = await self._analyze_areas_for_improvement(student_id)
            
            # Get learning insights
            insights = await self._generate_learning_insights(student_id)
            
            return StudentProgress(
                student_id=student_id,
                total_conversations=overall['total_conversations'],
                total_sentences=overall['total_sentences'],
                correct_sentences=overall['correct_sentences'],
                accuracy_percentage=accuracy,
                recent_accuracy_percentage=recent_accuracy,
                current_level=overall['current_level'],
                streak_days=overall['streak_days'],
                strengths=strengths,
                areas_for_improvement=areas_for_improvement,
                last_activity=overall['last_activity'].isoformat() if overall['last_activity'] else None,
                learning_insights=insights,
                weekly_goal_progress=await self._get_weekly_goal_progress(student_id),
                achievements=await self._get_achievements(student_id)
            )
            
        except Exception as e:
            logger.error(f"Error getting progress for {student_id}: {e}")
            return self._get_default_progress(student_id)
    
    async def get_common_mistakes(self, student_id: str) -> List[Dict]:
        """Get analysis of common mistakes made by the student"""
        try:
            student = self.student_data[student_id]
            mistakes = student['mistakes']
            
            if not mistakes:
                return []
            
            # Group mistakes by type
            mistake_groups = defaultdict(list)
            for mistake in mistakes:
                mistake_groups[mistake['mistake_type']].append(mistake)
            
            common_mistakes = []
            
            for mistake_type, mistake_list in mistake_groups.items():
                # Count occurrences
                count = len(mistake_list)
                
                if count >= 2:  # Only include mistakes that occurred multiple times
                    # Get recent examples
                    recent_examples = [m['original_text'] for m in mistake_list[-3:]]
                    
                    # Generate description and practice suggestion
                    description = self._get_mistake_description(mistake_type)
                    practice_suggestion = self._get_practice_suggestion(mistake_type)
                    
                    common_mistakes.append({
                        'mistake_type': mistake_type,
                        'count': count,
                        'description': description,
                        'recent_examples': recent_examples,
                        'suggested_practice': practice_suggestion,
                        'last_occurrence': mistake_list[-1]['date'].isoformat(),
                        'improvement_trend': self._calculate_improvement_trend(mistake_type, mistake_list)
                    })
            
            # Sort by frequency
            common_mistakes.sort(key=lambda x: x['count'], reverse=True)
            
            return common_mistakes
            
        except Exception as e:
            logger.error(f"Error analyzing common mistakes for {student_id}: {e}")
            return []
    
    async def get_daily_summary(self, student_id: str, date: Optional[str] = None) -> Dict:
        """Get daily learning summary"""
        try:
            if date is None:
                date = datetime.now().date().isoformat()
            
            student = self.student_data[student_id]
            daily_stats = student['daily_stats'][date]
            
            if daily_stats['sentences'] == 0:
                return {
                    'date': date,
                    'activity': False,
                    'message': 'No practice session today'
                }
            
            accuracy = 0.0
            if daily_stats['sentences'] > 0:
                accuracy = (daily_stats['correct_sentences'] / daily_stats['sentences']) * 100
            
            return {
                'date': date,
                'activity': True,
                'sentences_practiced': daily_stats['sentences'],
                'correct_sentences': daily_stats['correct_sentences'],
                'accuracy': accuracy,
                'mistakes_made': daily_stats['mistakes'],
                'topics_covered': list(daily_stats['topics_covered']),
                'session_time_minutes': daily_stats['session_time'],
                'achievement_message': self._generate_daily_achievement_message(daily_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary for {student_id}: {e}")
            return {'date': date, 'activity': False, 'error': 'Could not load summary'}
    
    async def get_weekly_report(self, student_id: str) -> Dict:
        """Generate comprehensive weekly learning report"""
        try:
            # Get data for the last 7 days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            student = self.student_data[student_id]
            
            weekly_data = {
                'total_sentences': 0,
                'correct_sentences': 0,
                'total_mistakes': 0,
                'active_days': 0,
                'topics_covered': set(),
                'improvement_areas': []
            }
            
            # Aggregate weekly data
            current_date = start_date
            daily_accuracies = []
            
            while current_date <= end_date:
                date_key = current_date.isoformat()
                daily_stats = student['daily_stats'][date_key]
                
                if daily_stats['sentences'] > 0:
                    weekly_data['active_days'] += 1
                    weekly_data['total_sentences'] += daily_stats['sentences']
                    weekly_data['correct_sentences'] += daily_stats['correct_sentences']
                    weekly_data['total_mistakes'] += daily_stats['mistakes']
                    weekly_data['topics_covered'].update(daily_stats['topics_covered'])
                    
                    daily_accuracy = (daily_stats['correct_sentences'] / daily_stats['sentences']) * 100
                    daily_accuracies.append(daily_accuracy)
                
                current_date += timedelta(days=1)
            
            # Calculate overall weekly accuracy
            overall_accuracy = 0.0
            if weekly_data['total_sentences'] > 0:
                overall_accuracy = (weekly_data['correct_sentences'] / weekly_data['total_sentences']) * 100
            
            # Calculate improvement trend
            improvement_trend = 'stable'
            if len(daily_accuracies) >= 2:
                if daily_accuracies[-1] > daily_accuracies[0] + 10:
                    improvement_trend = 'improving'
                elif daily_accuracies[-1] < daily_accuracies[0] - 10:
                    improvement_trend = 'needs_attention'
            
            return {
                'week_period': f"{start_date} to {end_date}",
                'active_days': weekly_data['active_days'],
                'total_sentences': weekly_data['total_sentences'],
                'accuracy_percentage': overall_accuracy,
                'improvement_trend': improvement_trend,
                'topics_covered': list(weekly_data['topics_covered']),
                'achievements': await self._get_weekly_achievements(student_id, weekly_data),
                'recommendations': await self._get_weekly_recommendations(student_id, weekly_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly report for {student_id}: {e}")
            return {'error': 'Could not generate weekly report'}
    
    def _estimate_complexity(self, message: str) -> float:
        """Estimate message complexity (0.0 to 1.0)"""
        word_count = len(message.split())
        avg_word_length = sum(len(word) for word in message.split()) / max(word_count, 1)
        
        # Simple complexity calculation
        complexity = min(1.0, (word_count * 0.1) + (avg_word_length * 0.05))
        return complexity
    
    async def _update_streak(self, student_id: str, current_date):
        """Update student's practice streak"""
        student = self.student_data[student_id]
        
        # Check if student practiced yesterday
        yesterday = current_date - timedelta(days=1)
        yesterday_key = yesterday.isoformat()
        
        if student['daily_stats'][yesterday_key]['sentences'] > 0:
            # Continue streak
            student['overall_stats']['streak_days'] += 1
        else:
            # Reset streak if there was a gap
            student['overall_stats']['streak_days'] = 1
    
    async def _update_level_assessment(self, student_id: str):
        """Update student's proficiency level based on recent performance"""
        student = self.student_data[student_id]
        overall = student['overall_stats']
        
        if overall['total_sentences'] < 10:
            overall['current_level'] = 'beginner'
            return
        
        # Get recent conversations for assessment
        recent_conversations = student['conversations'][-20:]
        
        if not recent_conversations:
            return
        
        # Calculate metrics
        recent_accuracy = sum(1 for conv in recent_conversations if conv['is_correct']) / len(recent_conversations)
        avg_complexity = sum(conv['complexity_estimated'] for conv in recent_conversations) / len(recent_conversations)
        avg_word_count = sum(conv['word_count'] for conv in recent_conversations) / len(recent_conversations)
        
        # Level assessment logic
        if recent_accuracy >= 0.8 and avg_complexity >= 0.6 and avg_word_count >= 15:
            overall['current_level'] = 'advanced'
        elif recent_accuracy >= 0.6 and avg_complexity >= 0.4 and avg_word_count >= 8:
            overall['current_level'] = 'intermediate'
        else:
            overall['current_level'] = 'beginner'
    
    async def _analyze_strengths(self, student_id: str) -> List[str]:
        """Analyze student's strengths based on performance data"""
        student = self.student_data[student_id]
        strengths = []
        
        # Analyze mistake patterns to identify areas student is good at
        mistake_types = Counter()
        for mistake in student['mistakes']:
            mistake_types[mistake['mistake_type']] += 1
        
        # If student makes few mistakes in certain areas, those are strengths
        all_error_types = ['grammar', 'tense', 'vocabulary', 'pronunciation', 'preposition']
        
        for error_type in all_error_types:
            if mistake_types[error_type] <= 2:  # Very few mistakes
                strength_descriptions = {
                    'grammar': 'Good grasp of basic grammar rules',
                    'tense': 'Proper use of verb tenses',
                    'vocabulary': 'Strong vocabulary knowledge',
                    'pronunciation': 'Clear pronunciation',
                    'preposition': 'Correct use of prepositions'
                }
                strengths.append(strength_descriptions.get(error_type, f'Good {error_type} skills'))
        
        # Add general strengths based on overall performance
        overall = student['overall_stats']
        if overall['streak_days'] >= 3:
            strengths.append('Consistent practice habit')
        
        if overall['total_sentences'] >= 50:
            strengths.append('Active participation in learning')
        
        return strengths[:5]  # Return top 5 strengths
    
    async def _analyze_areas_for_improvement(self, student_id: str) -> List[str]:
        """Analyze areas where student needs improvement"""
        student = self.student_data[student_id]
        improvements = []
        
        # Analyze mistake patterns
        mistake_types = Counter()
        for mistake in student['mistakes'][-20:]:  # Recent mistakes
            mistake_types[mistake['mistake_type']] += 1
        
        # Sort by frequency
        for error_type, count in mistake_types.most_common(3):
            if count >= 3:  # Significant number of mistakes
                improvement_descriptions = {
                    'grammar': 'Focus on basic grammar rules and sentence structure',
                    'tense': 'Practice verb tenses - past, present, and future forms',
                    'vocabulary': 'Expand vocabulary with daily word learning',
                    'pronunciation': 'Work on pronunciation and speaking clarity',
                    'preposition': 'Learn proper preposition usage (in, on, at, etc.)'
                }
                improvements.append(improvement_descriptions.get(error_type, f'Improve {error_type} skills'))
        
        return improvements
    
    async def _generate_learning_insights(self, student_id: str) -> List[str]:
        """Generate personalized learning insights"""
        student = self.student_data[student_id]
        insights = []
        
        overall = student['overall_stats']
        
        if overall['total_sentences'] >= 100:
            insights.append("🎉 You've practiced over 100 sentences! Great dedication!")
        
        if overall['streak_days'] >= 7:
            insights.append(f"🔥 Amazing! You have a {overall['streak_days']}-day practice streak!")
        
        # Analyze recent performance
        recent_conversations = student['conversations'][-10:]
        if recent_conversations:
            recent_accuracy = sum(1 for conv in recent_conversations if conv['is_correct']) / len(recent_conversations)
            
            if recent_accuracy >= 0.8:
                insights.append("📈 Your accuracy has improved significantly! Keep it up!")
            elif recent_accuracy < 0.5:
                insights.append("💪 Don't worry about mistakes - they help you learn faster!")
        
        return insights
    
    def _get_mistake_description(self, mistake_type: str) -> str:
        """Get description for mistake type"""
        descriptions = {
            'grammar': 'Basic grammar and sentence structure errors',
            'tense': 'Incorrect use of past, present, or future tenses',
            'vocabulary': 'Wrong word choice or usage',
            'pronunciation': 'Pronunciation and speaking clarity issues',
            'preposition': 'Incorrect use of prepositions (in, on, at, etc.)',
            'article': 'Incorrect use of articles (a, an, the)',
            'subject_verb_agreement': 'Subject and verb do not agree in number',
            'capitalization': 'Incorrect capitalization of words',
            'punctuation': 'Missing or incorrect punctuation marks'
        }
        return descriptions.get(mistake_type, 'Common English language error')
    
    def _get_practice_suggestion(self, mistake_type: str) -> str:
        """Get practice suggestion for mistake type"""
        suggestions = {
            'grammar': 'Practice basic sentence structures: Subject + Verb + Object',
            'tense': 'Practice verb forms: I go (present), I went (past), I will go (future)',
            'vocabulary': 'Learn 5 new words daily and use them in sentences',
            'pronunciation': 'Practice speaking slowly and clearly, listen to native speakers',
            'preposition': 'Learn preposition rules: at (time), in (places), on (surfaces)',
            'article': 'Practice: a/an for singular countable nouns, the for specific items',
            'subject_verb_agreement': 'Remember: I am, you are, he/she is, we/they are',
            'capitalization': 'Always start sentences with capital letters, capitalize "I"',
            'punctuation': 'End sentences with periods (.), questions with (?)'
        }
        return suggestions.get(mistake_type, 'Keep practicing and focus on this area')
    
    def _calculate_improvement_trend(self, mistake_type: str, mistake_list: List[Dict]) -> str:
        """Calculate if student is improving in this mistake type"""
        if len(mistake_list) < 4:
            return 'not_enough_data'
        
        # Check recent vs older mistakes
        recent_mistakes = len([m for m in mistake_list[-5:] if m['mistake_type'] == mistake_type])
        older_mistakes = len([m for m in mistake_list[-10:-5] if m['mistake_type'] == mistake_type])
        
        if recent_mistakes < older_mistakes:
            return 'improving'
        elif recent_mistakes > older_mistakes:
            return 'needs_attention'
        else:
            return 'stable'
    
    async def _get_weekly_goal_progress(self, student_id: str) -> Dict:
        """Get weekly goal progress"""
        # This would typically be customizable per student
        goal_sentences_per_week = 50
        
        student = self.student_data[student_id]
        
        # Count sentences this week
        current_date = datetime.now().date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        
        weekly_sentences = 0
        for i in range(7):
            date_key = (start_of_week + timedelta(days=i)).isoformat()
            daily_stats = student['daily_stats'][date_key]
            weekly_sentences += daily_stats['sentences']
        
        progress_percentage = min(100, (weekly_sentences / goal_sentences_per_week) * 100)
        
        return {
            'goal_sentences': goal_sentences_per_week,
            'completed_sentences': weekly_sentences,
            'progress_percentage': progress_percentage,
            'is_goal_achieved': weekly_sentences >= goal_sentences_per_week
        }
    
    async def _get_achievements(self, student_id: str) -> List[Dict]:
        """Get student achievements and badges"""
        student = self.student_data[student_id]
        overall = student['overall_stats']
        achievements = []
        
        # Sentence milestones
        if overall['total_sentences'] >= 10:
            achievements.append({'title': 'First Steps', 'description': 'Completed 10 sentences', 'icon': '👶'})
        if overall['total_sentences'] >= 50:
            achievements.append({'title': 'Getting Started', 'description': 'Practiced 50 sentences', 'icon': '🌱'})
        if overall['total_sentences'] >= 100:
            achievements.append({'title': 'Dedicated Learner', 'description': 'Reached 100 sentences', 'icon': '🎯'})
        
        # Streak achievements
        if overall['streak_days'] >= 3:
            achievements.append({'title': 'Consistent', 'description': '3-day practice streak', 'icon': '🔥'})
        if overall['streak_days'] >= 7:
            achievements.append({'title': 'Committed', 'description': '1-week streak', 'icon': '⭐'})
        if overall['streak_days'] >= 30:
            achievements.append({'title': 'Dedicated', 'description': '1-month streak', 'icon': '🏆'})
        
        # Accuracy achievements
        if overall['total_sentences'] >= 20:
            recent_accuracy = 0
            if overall['total_sentences'] > 0:
                recent_accuracy = (overall['correct_sentences'] / overall['total_sentences']) * 100
                
            if recent_accuracy >= 80:
                achievements.append({'title': 'Accurate Speaker', 'description': '80%+ accuracy', 'icon': '🎯'})
            if recent_accuracy >= 90:
                achievements.append({'title': 'Precision Master', 'description': '90%+ accuracy', 'icon': '💎'})
        
        return achievements
    
    async def _get_weekly_achievements(self, student_id: str, weekly_data: Dict) -> List[str]:
        """Get achievements for the week"""
        achievements = []
        
        if weekly_data['active_days'] >= 5:
            achievements.append("🏆 Practiced 5+ days this week!")
        if weekly_data['total_sentences'] >= 30:
            achievements.append("📈 Completed 30+ sentences this week!")
        if weekly_data['total_sentences'] > 0 and (weekly_data['correct_sentences'] / weekly_data['total_sentences']) >= 0.8:
            achievements.append("🎯 Achieved 80%+ accuracy this week!")
        
        return achievements
    
    async def _get_weekly_recommendations(self, student_id: str, weekly_data: Dict) -> List[str]:
        """Get recommendations for next week"""
        recommendations = []
        
        if weekly_data['active_days'] < 3:
            recommendations.append("Try to practice at least 3 days next week")
        if weekly_data['total_sentences'] < 20:
            recommendations.append("Aim for 20+ sentences next week")
        
        # Add specific recommendations based on common mistakes
        common_mistakes = await self.get_common_mistakes(student_id)
        if common_mistakes:
            top_mistake = common_mistakes[0]
            recommendations.append(f"Focus on {top_mistake['mistake_type']} practice")
        
        return recommendations
    
    def _generate_daily_achievement_message(self, daily_stats: Dict) -> str:
        """Generate encouraging daily achievement message"""
        sentences = daily_stats['sentences']
        correct = daily_stats['correct_sentences']
        
        if sentences == 0:
            return ""
        
        accuracy = (correct / sentences) * 100
        
        if accuracy >= 90:
            return f"🌟 Excellent! {accuracy:.0f}% accuracy today!"
        elif accuracy >= 70:
            return f"👍 Good work! {accuracy:.0f}% accuracy today!"
        else:
            return f"💪 Keep practicing! You completed {sentences} sentences today!"
    
    def _get_default_progress(self, student_id: str) -> StudentProgress:
        """Get default progress for new students"""
        return StudentProgress(
            student_id=student_id,
            total_conversations=0,
            total_sentences=0,
            correct_sentences=0,
            accuracy_percentage=0.0,
            recent_accuracy_percentage=0.0,
            current_level='beginner',
            streak_days=0,
            strengths=['Ready to learn!'],
            areas_for_improvement=['Start with basic sentences'],
            last_activity=None,
            learning_insights=['Welcome to your English learning journey! 🚀'],
            weekly_goal_progress={
                'goal_sentences': 50,
                'completed_sentences': 0,
                'progress_percentage': 0,
                'is_goal_achieved': False
            },
            achievements=[]
        )