from app import app, db, User
from werkzeug.security import generate_password_hash

# User credentials to update
user_credentials = [
    {"username": "Terry", "password": "Welcome1"},
    {"username": "Veronica", "password": "Welcome2"},
    {"username": "Sisay", "password": "Welcome3"},
    {"username": "Patsy", "password": "Welcome4"},
    {"username": "Donald", "password": "Welcome5"},
    {"username": "Demo", "password": "Welcome6"},
    {"username": "Geary", "password": "Welcome7"},
    {"username": "Galen", "password": "Welcome8"},
    {"username": "Norman", "password": "Welcome9"}
]

with app.app_context():
    print("Updating user passwords with proper hashing...")
    
    updated_count = 0
    for user_cred in user_credentials:
        username = user_cred["username"]
        password = user_cred["password"]
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        if user:
            # Update with hashed password
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            updated_count += 1
            print(f"Updated password for: {username}")
        else:
            print(f"User not found: {username}")
    
    # Commit changes
    db.session.commit()
    print(f"\nUpdated passwords for {updated_count} users")
    
    # Verify users
    print("\nVerifying user list:")
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}")
