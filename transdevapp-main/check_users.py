from database import db, User
from sqlalchemy import inspect
from flask import Flask, request, redirect, url_for
from flask_login import login_required
from datetime import datetime
from .models import Shift, Notification  # Use relative import if models.py is in the same package

app = Flask(__name__)

def check_users():
    with db.engine.connect() as connection:
        result = connection.execute("SELECT * FROM user;")
        users = result.fetchall()
        if not users:
            print("No users found in the database.")
        else:
            for user in users:
                print(user)

def check_admin_users():
    with db.session.begin():
        admin1 = User.query.filter_by(username='admin1').first()

        if admin1:
            print("Admin1 exists in the database.")
        else:
            print("Admin1 does not exist in the database.")

def check_database_schema():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)

    for table in tables:
        columns = inspector.get_columns(table)
        print(f"Columns in {table}:", [column['name'] for column in columns])

def check_shift_table():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('shift')
    print("Columns in 'shift' table:", [column['name'] for column in columns])

@app.route('/update_schedule', methods=['POST'])
@login_required
def update_schedule():
    print("Update schedule route hit!")
    # Get form data    
    shift_id = request.form.get('shift_id')
    print(f"Processing update for shift_id: {shift_id}")
    
    # Get assignment data
    new_assignment = request.form.get('assignment')
    print(f"New assignment value: {new_assignment}")
    
    shift = Shift.query.get(shift_id)
    
    if shift:
        print(f"Original assignment: {shift.assignment}")
        
        # Update assignment field - directly set it
        if new_assignment is not None:
            shift.assignment = new_assignment
            print(f"Assignment updated to: {shift.assignment}")
        
        # Process start time
        new_start_time = request.form.get('start_time')
        if new_start_time and new_start_time.strip():
            try:
                start_time = datetime.strptime(new_start_time, '%Y-%m-%dT%H:%M')
                shift.start_time = start_time
            except (ValueError, TypeError) as e:
                print(f"Error parsing start_time: {e}")
        
        # Process end time
        new_end_time = request.form.get('end_time')
        if new_end_time and new_end_time.strip():
            try:
                end_time = datetime.strptime(new_end_time, '%Y-%m-%dT%H:%M')
                shift.end_time = end_time
            except (ValueError, TypeError) as e:
                print(f"Error parsing end_time: {e}")
        
        # Explicitly commit the changes
        db.session.commit()
        print("Database changes committed")
        
        # Notify all users about the update
        users = User.query.all()
        for user in users:
            notification = Notification(
                message=f"Schedule updated: {shift.assignment} from {shift.start_time.strftime('%m/%d/%Y %I:%M %p')} to {shift.end_time.strftime('%m/%d/%Y %I:%M %p')}",
                user_id=user.id
            )
            db.session.add(notification)
        db.session.commit()
    else:
        print(f"Shift with ID {shift_id} not found")
    
    return redirect(url_for('schedule'))

@app.route('/', methods=['POST'])
def handle_empty_path():
    print("Empty path POST request received")
    print(f"Form data: {request.form}")
    
    # Try to process as if it were an update_schedule request
    if 'shift_id' in request.form:
        print("Treating as update_schedule request")
        return update_schedule()
    
    return "Invalid request", 400

@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    print(f"404 Error: Path '{path}' not found")
    print(f"Request method: {request.method}")
    print(f"Request form data: {request.form}")
    return f"The path /{path} was not found on the server", 404

if __name__ == "__main__":
    check_users()
    check_admin_users()
    check_database_schema()
    with db.engine.connect() as connection:
        check_shift_table()

# Check this line in your schedule.html file:
# <form method="POST" action="{{ url_for('update_schedule') }}">
# </form>
# TODO: Add the rest of the form handling logic in your schedule.html file.