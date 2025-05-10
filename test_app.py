import os
import tempfile
import pytest
from datetime import datetime, timedelta
from app import app
from database import db, User, Shift, Notification
from werkzeug.security import generate_password_hash


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
            admin_user = User(username="test_admin",
                             password=generate_password_hash("test_password", method='pbkdf2:sha256'))
            db.session.add(admin_user)
            # Create a regular user
            regular_user = User(username="test_user",
                                password=generate_password_hash("test_password", method='pbkdf2:sha256'))
            db.session.add(regular_user)
            db.session.commit()
            
            # Create a test shift
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=8)
            test_shift = Shift(
                employee_id=regular_user.id,
                start_time=start_time,
                end_time=end_time,
                status='Scheduled',
                assignment='Test Assignment',
                students='Student1, Student2'
            )
            db.session.add(test_shift)
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.drop_all()


def test_home_redirects_to_login(client):
    """Test that the home page redirects to the login page."""
    response = client.get('/')
    assert response.status_code == 302  # Redirect status code
    assert '/login' in response.headers['Location']


def test_login_get(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_login_post_valid(client):
    """Test login with valid credentials."""
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_login_post_invalid(client):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'wrong_password'
    })
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_dashboard_requires_login(client):
    """Test that the dashboard requires login."""
    response = client.get('/dashboard')
    assert response.status_code == 401  # Unauthorized


def test_dashboard_with_login(client):
    """Test accessing dashboard when logged in."""
    # Login first
    client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    })
    
    # Then access dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_schedule_access_regular_user(client):
    """Test that regular users cannot access the schedule management page."""
    # Login as regular user
    client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    })
    
    # Try to access schedule
    response = client.get('/schedule')
    assert response.status_code == 403  # Forbidden


def test_schedule_access_admin(client):
    """Test that admin users cannot access the schedule management page (unless specifically set as admin1, admin2, or admin3)."""
    # Login as admin
    client.post('/login', data={
        'username': 'test_admin',
        'password': 'test_password'
    })
    
    # Try to access schedule - should be forbidden since it's not one of the hardcoded admin users
    response = client.get('/schedule')
    assert response.status_code == 403  # Only admin1, admin2, admin3 can access


def test_logout(client):
    """Test that logout works correctly."""
    # Login first
    client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

    # Verify can't access protected page
    response = client.get('/dashboard')
    assert response.status_code == 401  # Unauthorized
