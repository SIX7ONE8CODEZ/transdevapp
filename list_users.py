from app import app, db, User
from flask_sqlalchemy import SQLAlchemy

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"User: {user.username}")
