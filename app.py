#!/usr/bin/env python3
"""
QUIZDOM - The Ultimate Knowledge Challenge Platform
Advanced Quiz Backend with Flask, SQLite, and Modern API Design
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import json
import os
import logging
from functools import wraps
import jwt

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'quizdom-ultimate-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizdom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for player management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    
    # Relationships
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'total_score': self.total_score,
            'games_played': self.games_played,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    """Categories for quiz questions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='category', lazy=True)
    quiz_sessions = db.relationship('QuizSession', backref='category', lazy=True)
    leaderboard_entries = db.relationship('Leaderboard', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'icon': self.icon,
            'question_count': len(self.questions)
        }

class Question(db.Model):
    """Quiz questions with multiple choice answers"""
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)  # easy, medium, hard
    correct_answer = db.Column(db.Integer, nullable=False)  # 0-3 index
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self, include_answer=False):
        result = {
            'id': self.id,
            'question': self.question_text,
            'category': self.category.name,
            'difficulty': self.difficulty,
            'options': [self.option_1, self.option_2, self.option_3, self.option_4]
        }
        
        if include_answer:
            result['correct_answer'] = self.correct_answer
            result['explanation'] = self.explanation
            
        return result

class QuizSession(db.Model):
    """Individual quiz game sessions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    current_question = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    time_taken = db.Column(db.Integer, default=0)  # in seconds
    
    # Store question IDs as JSON
    question_ids = db.Column(db.Text)  # JSON array of question IDs
    user_answers = db.Column(db.Text)  # JSON array of user answers
    
    def set_question_ids(self, ids):
        self.question_ids = json.dumps(ids)
    
    def get_question_ids(self):
        return json.loads(self.question_ids) if self.question_ids else []
    
    def set_user_answers(self, answers):
        self.user_answers = json.dumps(answers)
    
    def get_user_answers(self):
        return json.loads(self.user_answers) if self.user_answers else []
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_token': self.session_token,
            'category': self.category.display_name,
            'difficulty': self.difficulty,
            'total_questions': self.total_questions,
            'current_question': self.current_question,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed,
            'time_taken': self.time_taken
        }

class Leaderboard(db.Model):
    """Leaderboard entries for high scores"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    player_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_name': self.player_name,
            'score': self.score,
            'category': self.category.display_name,
            'difficulty': self.difficulty,
            'accuracy': self.accuracy,
            'time_taken': self.time_taken,
            'date': self.created_at.strftime('%Y-%m-%d')
        }

# ==================== UTILITY FUNCTIONS ====================

def generate_session_token():
    """Generate a unique session token"""
    import secrets
    return secrets.token_urlsafe(32)

def get_points_for_difficulty(difficulty):
    """Get points based on difficulty level"""
    points_map = {
        'easy': 5,
        'medium': 10,
        'hard': 15
    }
    return points_map.get(difficulty, 5)

def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove "Bearer "
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# ==================== API ROUTES ====================

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'QUIZDOM API is running',
        'timestamp': datetime.utcnow().isoformat()
    })

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'token': token
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': token
    })

# ==================== CATEGORY ROUTES ====================

@app.route('/api/categories')
def get_categories():
    """Get all active categories"""
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify({
        'categories': [cat.to_dict() for cat in categories]
    })

@app.route('/api/categories/<int:category_id>')
def get_category(category_id):
    """Get a specific category"""
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict())

# ==================== QUIZ ROUTES ====================

@app.route('/api/quiz/start', methods=['POST'])
def start_quiz():
    """Start a new quiz session"""
    data = request.get_json()
    
    if not data or not data.get('category_id') or not data.get('difficulty'):
        return jsonify({'error': 'Missing category_id or difficulty'}), 400
    
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    difficulty = data['difficulty']
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty level'}), 400
    
    questions_count = data.get('questions_count', 10)
    
    # Get random questions for this category and difficulty
    questions = Question.query.filter_by(
        category_id=data['category_id'],
        difficulty=difficulty,
        is_active=True
    ).all()
    
    if len(questions) < questions_count:
        # If not enough questions for specific difficulty, get mixed
        questions = Question.query.filter_by(
            category_id=data['category_id'],
            is_active=True
        ).all()
    
    if len(questions) < questions_count:
        return jsonify({'error': 'Not enough questions available'}), 400
    
    # Randomly select questions
    selected_questions = random.sample(questions, min(questions_count, len(questions)))
    question_ids = [q.id for q in selected_questions]
    
    # Create quiz session
    session = QuizSession(
        session_token=generate_session_token(),
        category_id=data['category_id'],
        difficulty=difficulty,
        total_questions=len(selected_questions),
        current_question=0
    )
    session.set_question_ids(question_ids)
    session.set_user_answers([])
    
    db.session.add(session)
    db.session.commit()
    
    logger.info(f"Quiz session started: {session.session_token}")
    
    return jsonify({
        'session_token': session.session_token,
        'quiz_info': session.to_dict(),
        'message': 'Quiz session started successfully'
    }), 201

@app.route('/api/quiz/<session_token>/question')
def get_current_question(session_token):
    """Get the current question for a quiz session"""
    session = QuizSession.query.filter_by(session_token=session_token).first()
    if not session:
        return jsonify({'error': 'Quiz session not found'}), 404
    
    if session.is_completed:
        return jsonify({'error': 'Quiz already completed'}), 400
    
    question_ids = session.get_question_ids()
    
    if session.current_question >= len(question_ids):
        return jsonify({'error': 'No more questions'}), 400
    
    question_id = question_ids[session.current_question]
    question = Question.query.get(question_id)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    return jsonify({
        'question': question.to_dict(),
        'question_number': session.current_question + 1,
        'total_questions': session.total_questions,
        'current_score': session.score
    })

@app.route('/api/quiz/<session_token>/answer', methods=['POST'])
def submit_answer(session_token):
    """Submit an answer for the current question"""
    session = QuizSession.query.filter_by(session_token=session_token).first()
    if not session:
        return jsonify({'error': 'Quiz session not found'}), 404
    
    if session.is_completed:
        return jsonify({'error': 'Quiz already completed'}), 400
    
    data = request.get_json()
    if not data or 'answer' not in data:
        return jsonify({'error': 'Missing answer'}), 400
    
    user_answer = data['answer']
    if not isinstance(user_answer, int) or user_answer < 0 or user_answer > 3:
        return jsonify({'error': 'Invalid answer format'}), 400
    
    question_ids = session.get_question_ids()
    user_answers = session.get_user_answers()
    
    if session.current_question >= len(question_ids):
        return jsonify({'error': 'No more questions'}), 400
    
    question_id = question_ids[session.current_question]
    question = Question.query.get(question_id)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    # Check if answer is correct
    is_correct = user_answer == question.correct_answer
    points = 0
    
    if is_correct:
        session.correct_answers += 1
        points = get_points_for_difficulty(session.difficulty)
        session.score += points
    
    # Store user answer
    user_answers.append(user_answer)
    session.set_user_answers(user_answers)
    
    # Move to next question
    session.current_question += 1
    
    # Check if quiz is completed
    quiz_completed = session.current_question >= session.total_questions
    if quiz_completed:
        session.is_completed = True
        session.completed_at = datetime.utcnow()
        session.time_taken = int((session.completed_at - session.started_at).total_seconds())
        
        # Add to leaderboard if score is good enough
        player_name = data.get('player_name', 'Anonymous')
        accuracy = (session.correct_answers / session.total_questions) * 100
        
        leaderboard_entry = Leaderboard(
            player_name=player_name,
            score=session.score,
            category_id=session.category_id,
            difficulty=session.difficulty,
            accuracy=accuracy,
            time_taken=session.time_taken
        )
        db.session.add(leaderboard_entry)
    
    db.session.commit()
    
    response_data = {
        'is_correct': is_correct,
        'correct_answer': question.correct_answer,
        'explanation': question.explanation,
        'points_earned': points,
        'current_score': session.score,
        'quiz_completed': quiz_completed
    }
    
    if quiz_completed:
        response_data['final_stats'] = {
            'total_score': session.score,
            'correct_answers': session.correct_answers,
            'total_questions': session.total_questions,
            'accuracy': round((session.correct_answers / session.total_questions) * 100, 1),
            'time_taken': session.time_taken
        }
    
    return jsonify(response_data)

@app.route('/api/quiz/<session_token>/status')
def get_quiz_status(session_token):
    """Get the current status of a quiz session"""
    session = QuizSession.query.filter_by(session_token=session_token).first()
    if not session:
        return jsonify({'error': 'Quiz session not found'}), 404
    
    return jsonify(session.to_dict())

# ==================== LEADERBOARD ROUTES ====================

@app.route('/api/leaderboard')
def get_leaderboard():
    """Get leaderboard entries"""
    category_id = request.args.get('category_id', type=int)
    difficulty = request.args.get('difficulty')
    limit = request.args.get('limit', 50, type=int)
    
    query = Leaderboard.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    entries = query.order_by(Leaderboard.score.desc(), Leaderboard.time_taken.asc()).limit(limit).all()
    
    return jsonify({
        'leaderboard': [entry.to_dict() for entry in entries],
        'total_entries': len(entries)
    })

@app.route('/api/leaderboard/top', methods=['GET'])
def get_top_scores():
    """Get top scores across all categories"""
    limit = request.args.get('limit', 10, type=int)
    
    entries = Leaderboard.query.order_by(
        Leaderboard.score.desc(), 
        Leaderboard.time_taken.asc()
    ).limit(limit).all()
    
    return jsonify({
        'top_scores': [entry.to_dict() for entry in entries]
    })

# ==================== STATISTICS ROUTES ====================

@app.route('/api/stats/general')
def get_general_stats():
    """Get general application statistics"""
    total_users = User.query.count()
    total_questions = Question.query.filter_by(is_active=True).count()
    total_sessions = QuizSession.query.count()
    completed_sessions = QuizSession.query.filter_by(is_completed=True).count()
    
    # Average score
    avg_score = db.session.query(db.func.avg(QuizSession.score)).filter_by(is_completed=True).scalar() or 0
    
    # Most popular category
    popular_category = db.session.query(
        Category.display_name, 
        db.func.count(QuizSession.id).label('session_count')
    ).join(QuizSession).group_by(Category.id).order_by(db.desc('session_count')).first()
    
    return jsonify({
        'total_users': total_users,
        'total_questions': total_questions,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'average_score': round(avg_score, 1),
        'most_popular_category': popular_category[0] if popular_category else 'N/A',
        'completion_rate': round((completed_sessions / total_sessions * 100), 1) if total_sessions > 0 else 0
    })

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/questions', methods=['POST'])
def add_question():
    """Add a new question (admin only)"""
    data = request.get_json()
    
    required_fields = ['question_text', 'category_id', 'difficulty', 'correct_answer', 'option_1', 'option_2', 'option_3', 'option_4']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    if data['difficulty'] not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty level'}), 400
    
    if not (0 <= data['correct_answer'] <= 3):
        return jsonify({'error': 'correct_answer must be between 0 and 3'}), 400
    
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    question = Question(
        question_text=data['question_text'],
        category_id=data['category_id'],
        difficulty=data['difficulty'],
        correct_answer=data['correct_answer'],
        option_1=data['option_1'],
        option_2=data['option_2'],
        option_3=data['option_3'],
        option_4=data['option_4'],
        explanation=data.get('explanation', '')
    )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'message': 'Question added successfully',
        'question': question.to_dict(include_answer=True)
    }), 201

# ==================== DATABASE INITIALIZATION ====================

def init_database():
    """Initialize database with sample data"""
    db.create_all()
    
    # Check if categories already exist
    if Category.query.count() > 0:
        return
    
    # Create categories
    categories_data = [
        {
            'name': 'science',
            'display_name': 'Science & Nature',
            'description': 'Explore the wonders of physics, chemistry, biology, and natural phenomena',
            'icon': 'fas fa-microscope'
        },
        {
            'name': 'history',
            'display_name': 'History',
            'description': 'Journey through time from ancient civilizations to modern events',
            'icon': 'fas fa-landmark'
        },
        {
            'name': 'technology',
            'display_name': 'Technology',
            'description': 'Test your knowledge of computers, programming, and digital innovation',
            'icon': 'fas fa-microchip'
        },
        {
            'name': 'sports',
            'display_name': 'Sports',
            'description': 'From Olympics to world championships, challenge your sports knowledge',
            'icon': 'fas fa-trophy'
        },
        {
            'name': 'arts',
            'display_name': 'Arts & Literature',
            'description': 'Dive into the world of literature, painting, music, and creative arts',
            'icon': 'fas fa-palette'
        },
        {
            'name': 'geography',
            'display_name': 'Geography',
            'description': 'Explore countries, capitals, landmarks, and geographical features',
            'icon': 'fas fa-globe-americas'
        },
        {
            'name': 'entertainment',
            'display_name': 'Entertainment',
            'description': 'Movies, TV shows, celebrities, and pop culture trivia',
            'icon': 'fas fa-film'
        },
        {
            'name': 'general',
            'display_name': 'General Knowledge',
            'description': 'Mixed topics covering a wide range of interesting facts and trivia',
            'icon': 'fas fa-brain'
        }
    ]
    
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)
    
    db.session.commit()
    
    # Add sample questions
    sample_questions = [
        # Science questions
        {
            'question_text': 'What is the chemical symbol for gold?',
            'category_name': 'science',
            'difficulty': 'easy',
            'correct_answer': 0,
            'options': ['Au', 'Ag', 'Fe', 'Cu'],
            'explanation': 'Gold\'s chemical symbol is Au, derived from the Latin word "aurum".'
        },
        {
            'question_text': 'Which planet is closest to the Sun?',
            'category_name': 'science',
            'difficulty': 'easy',
            'correct_answer': 2,
            'options': ['Venus', 'Earth', 'Mercury', 'Mars'],
            'explanation': 'Mercury is the closest planet to the Sun in our solar system.'
        },
        {
            'question_text': 'What is the speed of light in vacuum?',
            'category_name': 'science',
            'difficulty': 'hard',
            'correct_answer': 0,
            'options': ['299,792,458 m/s', '300,000,000 m/s', '299,792,458 km/s', '186,000 miles/s'],
            'explanation': 'The exact speed of light in vacuum is 299,792,458 meters per second.'
        },
        # History questions
        {
            'question_text': 'In which year did World War II end?',
            'category_name': 'history',
            'difficulty': 'easy',
            'correct_answer': 1,
            'options': ['1944', '1945', '1946', '1947'],
            'explanation': 'World War II ended in 1945 with the surrender of Japan.'
        },
        {
            'question_text': 'Who was the first President of the United States?',
            'category_name': 'history',
            'difficulty': 'easy',
            'correct_answer': 2,
            'options': ['Thomas Jefferson', 'John Adams', 'George Washington', 'Benjamin Franklin'],
            'explanation': 'George Washington was the first President of the United States (1789-1797).'
        },
        # Technology questions
        {
            'question_text': 'What does CPU stand for?',
            'category_name': 'technology',
            'difficulty': 'easy',
            'correct_answer': 0,
            'options': ['Central Processing Unit', 'Computer Processing Unit', 'Central Program Unit', 'Computer Program Unit'],
            'explanation': 'CPU stands for Central Processing Unit, the main processor of a computer.'
        },
        {
            'question_text': 'Which programming language is known as the "language of the web"?',
            'category_name': 'technology',
            'difficulty': 'medium',
            'correct_answer': 2,
            'options': ['Python', 'Java', 'JavaScript', 'C++'],
            'explanation': 'JavaScript is often called the "language of the web" as it runs in web browsers.'
        }
    ]
    
    for q_data in sample_questions:
        category = Category.query.filter_by(name=q_data['category_name']).first()
        if category:
            question = Question(
                question_text=q_data['question_text'],
                category_id=category.id,
                difficulty=q_data['difficulty'],
                correct_answer=q_data['correct_answer'],
                option_1=q_data['options'][0],
                option_2=q_data['options'][1],
                option_3=q_data['options'][2],
                option_4=q_data['options'][3],
                explanation=q_data['explanation']
            )
            db.session.add(question)
    
    db.session.commit()
    logger.info("Database initialized with sample data")

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# ==================== MAIN APPLICATION ====================

if __name__ == '__main__':
    with app.app_context():
        init_database()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"🚀 Starting QUIZDOM API server on port {port}")
    logger.info(f"🎯 Debug mode: {debug}")
    
    print(f"🌐 QUIZDOM is accessible at:")
    print(f"   • Local: http://localhost:{port}")
    print(f"   • Network: http://0.0.0.0:{port}")
    print(f"   • All interfaces: http://127.0.0.1:{port}")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)