from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    print("List of all users in the database:")
    print("=" * 50)
    print("{:<5} {:<15} {:<10}".format("ID", "Username", "Is Admin"))
    print("-" * 50)
    
    users = User.query.all()
    for user in users:
        is_admin = "Yes" if user.username in ['admin1', 'admin2', 'admin3'] else "No"
        print("{:<5} {:<15} {:<10}".format(user.id, user.username, is_admin))
    
    print("\nTotal users:", len(users))
