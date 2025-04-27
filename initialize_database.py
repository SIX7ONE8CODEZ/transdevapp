import os
from database import db, app

def initialize_database():
    db_path = os.path.join('instance', 'transdev.db')

    # Check if the database already exists
    if not os.path.exists(db_path):
        print("Initializing database...")
        with app.app_context():
            db.create_all()
        print("Database initialized successfully.")
    else:
        print("Database already exists. Skipping initialization.")

if __name__ == "__main__":
    initialize_database()