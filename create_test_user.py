from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create a regular user
    regular_user = User(
        username='testuser',
        password=generate_password_hash('password123', method='pbkdf2:sha256')
    )
    db.session.add(regular_user)
    db.session.commit()
    print(f"Created user: {regular_user.username}")
