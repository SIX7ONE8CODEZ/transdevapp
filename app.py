from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Shift, Notification
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
FLASK_APP = os.getenv('FLASK_APP')
FLASK_ENV = os.getenv('FLASK_ENV')
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transdev.db'
app.config['SECRET_KEY'] = 'your_secret_key'

with app.app_context():
    db.init_app(app)
    db.create_all()

    # Ensure special admin users are created
    special_users = [
        {'username': 'admin1', 'password': 'A1d!n@2025#'},
        {'username': 'admin2', 'password': 'B2m$in#2025&'},
        {'username': 'admin3', 'password': 'C3x#in@2025*'}
    ]

    for user in special_users:
        existing_user = User.query.filter_by(username=user['username']).first()
        if not existing_user:
            new_user = User(
                username=user['username'],
                password=generate_password_hash(user['password'], method='pbkdf2:sha256')
            )
            db.session.add(new_user)
    db.session.commit()

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print("Login POST request received")
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            print(f"User {user.username} authenticated successfully")
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            print("Invalid username or password")
            error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if User.query.filter_by(username=username).first():
            return "Username already exists!"

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Accessing dashboard for user: {current_user.username}")
    user_shifts = Shift.query.filter_by(employee_id=current_user.id).all()
    print(f"Shifts retrieved for user {current_user.username}: {user_shifts}")
    return render_template('dashboard.html', shifts=user_shifts)

@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if current_user.username not in ['admin1', 'admin2', 'admin3']:
        return "Access denied. You do not have permission to edit the schedule.", 403

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        start_time = datetime.fromisoformat(request.form.get('start_time'))
        end_time = datetime.fromisoformat(request.form.get('end_time'))
        assignment = request.form.get('assignment')
        students = request.form.get('students')

        new_shift = Shift(
            employee_id=employee_id,
            start_time=start_time,
            end_time=end_time,
            status='Scheduled',
            assignment=assignment,
            students=students
        )
        db.session.add(new_shift)
        db.session.commit()

        # Notify all users about the schedule change
        users = User.query.all()
        for user in users:
            notification = Notification(
                message=f"Schedule updated: {assignment} from {start_time} to {end_time}",
                user_id=user.id
            )
            db.session.add(notification)
        db.session.commit()

        return redirect(url_for('schedule'))

    shifts = Shift.query.all()
    employees = User.query.all()
    return render_template('schedule.html', shifts=shifts, employees=employees)

@app.route('/view_schedule')
@login_required
def view_schedule():
    if current_user.username in ['admin1', 'admin2', 'admin3']:
        user_shifts = db.session.query(Shift, User).join(User, Shift.employee_id == User.id).all()
    else:
        user_shifts = db.session.query(Shift, User).join(User, Shift.employee_id == User.id).filter(Shift.employee_id == current_user.id).all()

    shifts_with_employee = [
        {
            'assignment': shift.assignment,
            'start_time': shift.start_time,
            'end_time': shift.end_time,
            'status': shift.status,
            'employee_name': user.username,
            'students': shift.students,
        }
        for shift, user in user_shifts
    ]
    return render_template('view_schedule.html', shifts=shifts_with_employee)

@app.route('/api/schedule')
@login_required
def api_schedule():
    user_shifts = Shift.query.filter_by(employee_id=current_user.id).all()
    events = [
        {
            'title': shift.assignment,
            'start': shift.start_time.isoformat(),
            'end': shift.end_time.isoformat(),
            'status': shift.status
        }
        for shift in user_shifts
    ]
    return jsonify(events)

@app.route('/notifications')
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Notification not found'}), 404

@app.route('/update_students', methods=['POST'])
@login_required
def update_students():
    shift_id = request.form.get('shift_id')
    students = request.form.get('students')

    shift = Shift.query.get(shift_id)
    if shift:
        shift.students = students
        db.session.commit()
        return redirect(url_for('schedule'))
    else:
        return "Shift not found", 404

@app.route('/remove_user/<int:user_id>', methods=['POST'])
@login_required
def remove_user(user_id):
    if current_user.username not in ['admin1', 'admin2', 'admin3']:
        return "Access denied. You do not have permission to remove users.", 403

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/delete_schedule', methods=['POST'])
@login_required
def delete_schedule():
    shift_id = request.form.get('shift_id')

    shift = Shift.query.get(shift_id)
    if shift:
        db.session.delete(shift)
        db.session.commit()
        return redirect(url_for('schedule'))
    else:
        return "Shift not found", 404

@app.route('/view_users')
@login_required
def view_users():
    if current_user.username not in ['admin1', 'admin2', 'admin3']:
        return "Access denied. You do not have permission to view users.", 403

    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)