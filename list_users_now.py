from database import db, User
from app import app

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"Username: {user.username}")
