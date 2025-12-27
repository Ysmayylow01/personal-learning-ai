from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oguz-ai-academy-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oguz_ai_academy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.relationship('Progress', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True, cascade='all, delete-orphan')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='course', lazy=True, cascade='all, delete-orphan')
    quiz_results = db.relationship('QuizResult', backref='course', lazy=True, cascade='all, delete-orphan')

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(500))
    duration = db.Column(db.String(50))
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    progress_percentage = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    courses = Course.query.filter_by(is_published=True).all()
    return render_template('index.html', courses=courses)

@app.route('/courses')
def courses():
    all_courses = Course.query.filter_by(is_published=True).all()
    return render_template('courses.html', courses=all_courses)

@app.route('/course/<slug>')
def course_detail(slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).all()
    
    user_progress = None
    if 'user_id' in session:
        user_progress = Progress.query.filter_by(
            user_id=session['user_id'],
            course_id=course.id
        ).first()
    
    return render_template('course_detail.html', course=course, lessons=lessons, progress=user_progress)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    progress_data = Progress.query.filter_by(user_id=user.id).all()
    quiz_results = QuizResult.query.filter_by(user_id=user.id).order_by(QuizResult.completed_at.desc()).limit(5).all()
    
    enrolled_courses = []
    for prog in progress_data:
        course = Course.query.get(prog.course_id)
        enrolled_courses.append({
            'course': course,
            'progress': prog
        })
    
    return render_template('dashboard.html', user=user, enrolled_courses=enrolled_courses, quiz_results=quiz_results)

# ============ ADMIN ROUTES ============

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_lessons = Lesson.query.count()
    total_enrollments = Progress.query.count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_enrollments = Progress.query.order_by(Progress.last_accessed.desc()).limit(10).all()
    
    # Course statistics
    course_stats = []
    courses = Course.query.all()
    for course in courses:
        enrollments = Progress.query.filter_by(course_id=course.id).count()
        completions = Progress.query.filter_by(course_id=course.id, completed=True).count()
        course_stats.append({
            'course': course,
            'enrollments': enrollments,
            'completions': completions
        })
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_courses=total_courses,
                         total_lessons=total_lessons,
                         total_enrollments=total_enrollments,
                         recent_users=recent_users,
                         recent_enrollments=recent_enrollments,
                         course_stats=course_stats)

@app.route('/admin/courses')
@admin_required
def admin_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/course/add', methods=['GET', 'POST'])
@admin_required
def admin_add_course():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        description = request.form.get('description')
        category = request.form.get('category')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        image = request.form.get('image')
        content = request.form.get('content')
        is_published = request.form.get('is_published') == 'on'
        
        new_course = Course(
            title=title,
            slug=slug,
            description=description,
            category=category,
            difficulty=difficulty,
            duration=duration,
            image=image,
            content=content,
            is_published=is_published
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/course_form.html', course=None)

@app.route('/admin/course/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.slug = request.form.get('slug')
        course.description = request.form.get('description')
        course.category = request.form.get('category')
        course.difficulty = request.form.get('difficulty')
        course.duration = request.form.get('duration')
        course.image = request.form.get('image')
        course.content = request.form.get('content')
        course.is_published = request.form.get('is_published') == 'on'
        
        db.session.commit()
        
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/course_form.html', course=course)

@app.route('/admin/course/delete/<int:course_id>', methods=['POST'])
@admin_required
def admin_delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin_courses'))

@app.route('/admin/course/<int:course_id>/lessons')
@admin_required
def admin_course_lessons(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    return render_template('admin/lessons.html', course=course, lessons=lessons)

@app.route('/admin/course/<int:course_id>/lesson/add', methods=['GET', 'POST'])
@admin_required
def admin_add_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        video_url = request.form.get('video_url')
        duration = request.form.get('duration')
        order = request.form.get('order', type=int)
        
        new_lesson = Lesson(
            course_id=course_id,
            title=title,
            content=content,
            video_url=video_url,
            duration=duration,
            order=order
        )
        
        db.session.add(new_lesson)
        db.session.commit()
        
        flash('Lesson added successfully!', 'success')
        return redirect(url_for('admin_course_lessons', course_id=course_id))
    
    max_order = db.session.query(db.func.max(Lesson.order)).filter_by(course_id=course_id).scalar() or 0
    
    return render_template('admin/lesson_form.html', course=course, lesson=None, next_order=max_order + 1)

@app.route('/admin/lesson/edit/<int:lesson_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get(lesson.course_id)
    
    if request.method == 'POST':
        lesson.title = request.form.get('title')
        lesson.content = request.form.get('content')
        lesson.video_url = request.form.get('video_url')
        lesson.duration = request.form.get('duration')
        lesson.order = request.form.get('order', type=int)
        
        db.session.commit()
        
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('admin_course_lessons', course_id=lesson.course_id))
    
    return render_template('admin/lesson_form.html', course=course, lesson=lesson, next_order=lesson.order)

@app.route('/admin/lesson/delete/<int:lesson_id>', methods=['POST'])
@admin_required
def admin_delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id
    db.session.delete(lesson)
    db.session.commit()
    
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('admin_course_lessons', course_id=course_id))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/statistics')
@admin_required
def admin_statistics():
    # Overall statistics
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Progress.query.count()
    total_completions = Progress.query.filter_by(completed=True).count()
    
    # Course enrollment data
    course_data = []
    courses = Course.query.all()
    for course in courses:
        enrollments = Progress.query.filter_by(course_id=course.id).count()
        completions = Progress.query.filter_by(course_id=course.id, completed=True).count()
        avg_progress = db.session.query(db.func.avg(Progress.progress_percentage)).filter_by(course_id=course.id).scalar() or 0
        
        course_data.append({
            'title': course.title,
            'enrollments': enrollments,
            'completions': completions,
            'avg_progress': round(avg_progress, 2)
        })
    
    return render_template('admin/statistics.html',
                         total_users=total_users,
                         total_courses=total_courses,
                         total_enrollments=total_enrollments,
                         total_completions=total_completions,
                         course_data=course_data)

# Regular user routes
@app.route('/quiz/<int:course_id>')
def quiz(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    return render_template('quiz.html', course=course)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    course_id = data.get('course_id')
    score = data.get('score')
    total = data.get('total')
    
    quiz_result = QuizResult(
        user_id=session['user_id'],
        course_id=course_id,
        score=score,
        total_questions=total
    )
    
    db.session.add(quiz_result)
    
    progress = Progress.query.filter_by(
        user_id=session['user_id'],
        course_id=course_id
    ).first()
    
    if not progress:
        progress = Progress(
            user_id=session['user_id'],
            course_id=course_id,
            progress_percentage=100,
            completed=True
        )
        db.session.add(progress)
    else:
        progress.progress_percentage = 100
        progress.completed = True
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Quiz submitted successfully!'})

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    existing = Progress.query.filter_by(
        user_id=session['user_id'],
        course_id=course_id
    ).first()
    
    if not existing:
        progress = Progress(
            user_id=session['user_id'],
            course_id=course_id,
            progress_percentage=0
        )
        db.session.add(progress)
        db.session.commit()
        flash('Successfully enrolled in the course!', 'success')
    else:
        flash('You are already enrolled in this course!', 'info')
    
    return redirect(url_for('course_detail', slug=Course.query.get(course_id).slug))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # OpenRouter API call with DeepSeek
        import requests
        
        api_key = os.getenv('OPENROUTER_API_KEY', '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')
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5000',
            'X-Title': 'Oguz AI Academy Chatbot'
        }
        
        payload = {
            'model': 'deepseek/deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful AI learning assistant for Oguz AI Academy. Help students with questions about AI, machine learning, deep learning, and programming. Be friendly, educational, and encourage learning.'
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_message = result['choices'][0]['message']['content']
            return jsonify({'message': bot_message})
        else:
            return jsonify({'error': 'API request failed', 'details': response.text}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@oguzai.com',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
        
        # Add sample courses if database is empty
        if Course.query.count() == 0:
            courses_data = [
                {
                    'title': 'Machine Learning Fundamentals',
                    'slug': 'machine-learning',
                    'description': 'Master the basics of Machine Learning including supervised and unsupervised learning algorithms.',
                    'category': 'Machine Learning',
                    'difficulty': 'Beginner',
                    'duration': '8 weeks',
                    'image': '🤖',
                    'content': '<h2>Course Overview</h2><p>Learn machine learning fundamentals.</p>'
                }
            ]
            
            for course_data in courses_data:
                course = Course(**course_data)
                db.session.add(course)
            
            db.session.commit()
            print("Database initialized with sample courses!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)