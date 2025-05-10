from database import db
from app import app

# Drop all tables and recreate them
def reset_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database has been reset successfully.")

if __name__ == "__main__":
    reset_database()