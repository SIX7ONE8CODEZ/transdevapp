import pytest
from datetime import datetime, timedelta
from app import app, parse_datetime, calculate_duration
from database import db, User, Shift, Notification
from werkzeug.security import generate_password_hash
import json

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test admin user
            admin_user = User(username="admin1",
                             password=generate_password_hash("test_password", method='pbkdf2:sha256'))
            db.session.add(admin_user)
            # Create a regular user
            regular_user = User(username="test_user",
                                password=generate_password_hash("test_password", method='pbkdf2:sha256'))
            db.session.add(regular_user)
            db.session.commit()
            yield client

def test_parse_datetime():
    """Test the parse_datetime function with various formats."""
    test_cases = [
        # ISO format
        ('2025-05-20T14:30:00', datetime(2025, 5, 20, 14, 30)),
        # US format with AM/PM
        ('05/20/2025 02:30 PM', datetime(2025, 5, 20, 14, 30)),
        # 24-hour format
        ('05/20/2025 14:30', datetime(2025, 5, 20, 14, 30)),
        # Date only (should default to midnight)
        ('05/20/2025', datetime(2025, 5, 20)),
        # Should handle None value
        (None, None),
        # Already a datetime object
        (datetime(2025, 5, 20, 14, 30), datetime(2025, 5, 20, 14, 30)),
    ]
    
    for input_value, expected_result in test_cases:
        result = parse_datetime(input_value)
        if expected_result is None:
            assert result is None
        else:
            assert result == expected_result

def test_calculate_duration():
    """Test the calculate_duration function."""
    # Test normal case
    start = datetime(2025, 5, 20, 9, 0)
    end = datetime(2025, 5, 20, 10, 0)
    assert calculate_duration(start, end) == timedelta(hours=1)
    
    # Test when end time is before start time (should default to 1 hour)
    start = datetime(2025, 5, 20, 10, 0)
    end = datetime(2025, 5, 20, 9, 0)
    assert calculate_duration(start, end) == timedelta(hours=1)
    
    # Test when one time is None (should default to 1 hour)
    assert calculate_duration(None, end) == timedelta(hours=1)
    assert calculate_duration(start, None) == timedelta(hours=1)

def test_update_schedule_time_sync(client):
    """Test that the update_schedule route correctly synchronizes times."""
    with app.app_context():
        # Create a test shift
        start_time = datetime.now().replace(microsecond=0)
        end_time = start_time + timedelta(hours=8)
        test_shift = Shift(
            employee_id=2,  # Regular user ID
            start_time=start_time,
            end_time=end_time,
            status='Scheduled',
            assignment='Test Assignment',
            students='Student1, Student2'
        )
        db.session.add(test_shift)
        db.session.commit()
        shift_id = test_shift.id
    
        # Login as admin
        client.post('/login', data={
            'username': 'admin1',
            'password': 'test_password'
        })
        
        # Test updating start time while keeping end time unchanged
        new_start = start_time + timedelta(hours=1)
        response = client.post('/update_schedule', data={
            'shift_id': shift_id,
            'start_time': new_start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': ''  # Empty to test auto-sync
        })
        
        # Get updated shift
        updated_shift = Shift.query.get(shift_id)
        # End time should be shifted by 1 hour to maintain duration
        expected_end_time = end_time + timedelta(hours=1)
        assert updated_shift.start_time == new_start
        assert updated_shift.end_time == expected_end_time
        
def test_spreadsheet_update(client):
    """Test that spreadsheet updates handle date/time synchronization."""
    with app.app_context():
        # Create a test shift
        start_time = datetime.now().replace(microsecond=0)
        end_time = start_time + timedelta(hours=2)
        test_shift = Shift(
            employee_id=2,  # Regular user ID
            start_time=start_time,
            end_time=end_time,
            status='Scheduled',
            assignment='Test Assignment',
            students='Student1, Student2'
        )
        db.session.add(test_shift)
        db.session.commit()
        shift_id = test_shift.id
    
        # Login as admin
        client.post('/login', data={
            'username': 'admin1',
            'password': 'test_password'
        })
        
        # Update via spreadsheet view - changing only start time
        new_start = start_time + timedelta(hours=1)
        shifts_data = [{
            'id': shift_id,
            'employee_name': 'test_user',
            'assignment': 'Test Assignment',
            'start_time': new_start.isoformat(),
            'end_time': end_time.isoformat(),  # Don't change end time directly
            'status': 'Scheduled',
            'participants': 'Student1, Student2'
        }]
        
        response = client.post('/update_spreadsheet', 
                              data=json.dumps({'shifts': shifts_data}),
                              content_type='application/json')
        
        # Check that time was synchronized
        updated_shift = Shift.query.get(shift_id)
        # The previous behavior would adjust end time, check if it still holds
        assert updated_shift.start_time == new_start
        
        # If end time is before start time, it should be adjusted to 1 hour later
        new_bad_start = end_time + timedelta(hours=1)  # Start time after end time
        shifts_data[0]['start_time'] = new_bad_start.isoformat()
        
        response = client.post('/update_spreadsheet', 
                              data=json.dumps({'shifts': shifts_data}),
                              content_type='application/json')
                              
        # Check the adjustment
        updated_shift = Shift.query.get(shift_id)
        assert updated_shift.start_time == new_bad_start
        assert updated_shift.end_time == new_bad_start + timedelta(hours=1)

if __name__ == "__main__":
    pytest.main(['-v', 'test_datetime_sync.py'])
