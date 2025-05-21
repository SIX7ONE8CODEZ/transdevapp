from database import db, User
from app import app
from werkzeug.security import check_password_hash, generate_password_hash
import os

# Test username and password
test_username = 'admin1'
test_password = 'A1d!n@2025#'

with app.app_context():
    # Look for the specified user
    user = User.query.filter_by(username=test_username).first()
    
    if user:
        print(f"User found: {user.username} (ID: {user.id})")
        print(f"Password hash: {user.password[:30]}...")
        
        # Test password verification
        if check_password_hash(user.password, test_password):
            print(f"✅ Password verification SUCCESSFUL")
        else:
            print(f"❌ Password verification FAILED")
            
            # Debug password hash
            print("\nDEBUG INFO:")
            print(f"Original hash: {user.password}")
            
            # Generate a new hash with the same password for comparison
            new_hash = generate_password_hash(test_password, method='pbkdf2:sha256')
            print(f"New hash with same password: {new_hash}")
            
            # Re-check the password verification
            print("\nTrying to fix the password...")
            user.password = new_hash
            db.session.commit()
            print(f"Password updated for {user.username}")
            
            # Verify the fix worked
            updated_user = User.query.filter_by(username=test_username).first()
            if check_password_hash(updated_user.password, test_password):
                print(f"✅ Password verification now SUCCESSFUL after update")
            else:
                print(f"❌ Password verification still FAILING after update")
    else:
        print(f"User '{test_username}' not found in database")
