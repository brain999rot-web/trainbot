from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models.user import User
from models.program import Program
from models.workout import Workout
from models.exercise_log import ExerciseLog
from models.nutrition import NutritionLog, NutritionProfile
from models.personal_record import PersonalRecord
from models.favorite_exercise import FavoriteExercise
from sync_database import SessionLocal, init_sync_db
import logging
from sqlalchemy import desc

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

csrf = CSRFProtect(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_session = SessionLocal


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Будь ласка, увійдіть в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    if 'user_id' not in session:
        return None
    return db_session.query(User).filter_by(telegram_id=session['user_id']).first()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    user = get_current_user()
    if user:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id or not user_id.isdigit():
            flash('Введіть коректний ID користувача', 'danger')
            return render_template('login.html')

        user = db_session.query(User).filter_by(telegram_id=int(user_id)).first()
        if not user:
            flash('Користувача не знайдено. Зареєструйтесь спочатку.', 'warning')
            return redirect(url_for('register'))

        session['user_id'] = user.telegram_id
        session.permanent = True
        flash(f'Вітаємо, {user.username or "користувач"}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')
        gender = request.form.get('gender')
        experience = request.form.get('experience')
        workouts_per_week = request.form.get('workouts_per_week')
        goal = request.form.get('goal')

        if not user_id or not user_id.isdigit():
            flash('Введіть коректний ID користувача', 'danger')
            return render_template('register.html')

        existing_user = db_session.query(User).filter_by(telegram_id=int(user_id)).first()
        if existing_user:
            flash('Користувач вже існує. Увійдіть.', 'warning')
            return redirect(url_for('login'))

        new_user = User(
            telegram_id=int(user_id),
            username=username,
            age=int(age) if age else None,
            height=float(height) if height else None,
            weight=float(weight) if weight else None,
            gender=gender,
            experience=experience,
            workouts_per_week=int(workouts_per_week) if workouts_per_week else None,
            current_goal=goal
        )

        db_session.add(new_user)
        db_session.commit()

        session['user_id'] = new_user.telegram_id
        session.permanent = True
        flash('Реєстрація успішна!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Ви вийшли з системи', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()

    # Активна програма
    active_program = db_session.query(Program).filter_by(
        user_id=user.telegram_id,
        is_active=True
    ).first()

    # Останні тренування
    recent_workouts = db_session.query(Workout).filter_by(
        user_id=user.telegram_id
    ).order_by(desc(Workout.workout_date)).limit(5).all()

    # Статистика за останній тиждень
    week_ago = datetime.utcnow() - timedelta(days=7)
    workouts_this_week = db_session.query(Workout).filter(
        Workout.user_id == user.telegram_id,
        Workout.workout_date >= week_ago
    ).count()

    # Харчування сьогодні
    today = datetime.utcnow().date()
    nutrition_today = db_session.query(NutritionLog).filter_by(
        user_id=user.telegram_id,
        log_date=today
    ).first()

    return render_template('dashboard.html',
                          user=user,
                          active_program=active_program,
                          recent_workouts=recent_workouts,
                          workouts_this_week=workouts_this_week,
                          nutrition_today=nutrition_today)


@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    return render_template('profile.html', user=user)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = get_current_user()

    if request.method == 'POST':
        user.username = request.form.get('username')
        user.age = int(request.form.get('age')) if request.form.get('age') else None
        user.height = float(request.form.get('height')) if request.form.get('height') else None
        user.weight = float(request.form.get('weight')) if request.form.get('weight') else None
        user.gender = request.form.get('gender')
        user.experience = request.form.get('experience')
        user.workouts_per_week = int(request.form.get('workouts_per_week')) if request.form.get('workouts_per_week') else None
        user.current_goal = request.form.get('goal')

        db_session.commit()
        flash('Профіль оновлено', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user)


@app.route('/programs')
@login_required
def programs():
    user = get_current_user()
    all_programs = db_session.query(Program).filter_by(
        user_id=user.telegram_id
    ).order_by(desc(Program.created_at)).all()

    return render_template('programs.html', programs=all_programs)


@app.route('/programs/create', methods=['GET', 'POST'])
@login_required
def create_program():
    user = get_current_user()

    if request.method == 'POST':
        goal = request.form.get('goal')
        split_type = request.form.get('split_type')
        workouts_per_week = int(request.form.get('workouts_per_week'))

        # Використовуємо генератор програм (потрібно адаптувати під sync)
        # Тут заглушка - в реальності потрібно викликати program_generator
        program_data = {
            "weeks": 4,
            "workouts": {}
        }

        new_program = Program(
            user_id=user.telegram_id,
            goal=goal,
            split_type=split_type,
            workouts_per_week=workouts_per_week,
            program_data=program_data,
            is_active=True
        )

        # Деактивувати інші програми
        db_session.query(Program).filter_by(
            user_id=user.telegram_id,
            is_active=True
        ).update({'is_active': False})

        db_session.add(new_program)
        db_session.commit()

        flash('Програму створено!', 'success')
        return redirect(url_for('programs'))

    return render_template('create_program.html')


@app.route('/programs/<int:program_id>')
@login_required
def view_program(program_id):
    user = get_current_user()
    program = db_session.query(Program).filter_by(
        id=program_id,
        user_id=user.telegram_id
    ).first_or_404()

    return render_template('view_program.html', program=program)


@app.route('/workouts')
@login_required
def workouts():
    user = get_current_user()
    all_workouts = db_session.query(Workout).filter_by(
        user_id=user.telegram_id
    ).order_by(desc(Workout.workout_date)).all()

    return render_template('workouts.html', workouts=all_workouts)


@app.route('/workouts/<int:workout_id>')
@login_required
def view_workout(workout_id):
    user = get_current_user()
    workout = db_session.query(Workout).filter_by(
        id=workout_id,
        user_id=user.telegram_id
    ).first_or_404()

    return render_template('view_workout.html', workout=workout)


@app.route('/nutrition')
@login_required
def nutrition():
    user = get_current_user()

    # Профіль харчування
    nutrition_profile = db_session.query(NutritionProfile).filter_by(
        user_id=user.telegram_id
    ).first()

    # Останні записи
    recent_logs = db_session.query(NutritionLog).filter_by(
        user_id=user.telegram_id
    ).order_by(desc(NutritionLog.log_date)).limit(30).all()

    return render_template('nutrition.html',
                          nutrition_profile=nutrition_profile,
                          logs=recent_logs)


@app.route('/analytics')
@login_required
def analytics():
    user = get_current_user()

    # Статистика тренувань
    total_workouts = db_session.query(Workout).filter_by(
        user_id=user.telegram_id
    ).count()

    # Останні 30 днів
    month_ago = datetime.utcnow() - timedelta(days=30)
    workouts_last_month = db_session.query(Workout).filter(
        Workout.user_id == user.telegram_id,
        Workout.workout_date >= month_ago
    ).count()

    # Персональні рекорди
    records = db_session.query(PersonalRecord).filter_by(
        user_id=user.telegram_id
    ).order_by(desc(PersonalRecord.date_achieved)).limit(10).all()

    return render_template('analytics.html',
                          total_workouts=total_workouts,
                          workouts_last_month=workouts_last_month,
                          records=records)


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
