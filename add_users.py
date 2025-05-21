from app import db, User, app
from werkzeug.security import generate_password_hash

def add_user(username, password):
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"User {username} already exists")
        return False
    
    # Create new user with password (no password_hash field)
    new_user = User(
        username=username,
        password=password  # The model uses 'password' not 'password_hash'
    )
    
    # Add to database
    db.session.add(new_user)
    db.session.commit()
    print(f"Added user: {username}")
    return True

# Create Flask application context
with app.app_context():
    # Add users
    users_to_add = [
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
    
    # Add each user
    added_count = 0
    for user in users_to_add:
        if add_user(user["username"], user["password"]):
            added_count += 1
    
    print(f"Added {added_count} new users out of {len(users_to_add)} requested")
