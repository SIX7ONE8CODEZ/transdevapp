from database import db, User
from app import app
from werkzeug.security import check_password_hash

with app.app_context():
    # Look for the admin1 user
    admin1 = User.query.filter_by(username='admin1').first()
    
    if admin1:
        print(f"Admin1 found with ID: {admin1.id}")
        print(f"Password hash starts with: {admin1.password[:20]}...")
        
        # Test password verification
        test_password = 'A1d!n@2025#'
        if check_password_hash(admin1.password, test_password):
            print(f"Password check SUCCESSFUL!")
        else:
            print(f"Password check FAILED!")
    else:
        print("Admin1 user not found in database")
