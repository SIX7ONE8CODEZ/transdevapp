from database import db, User
from sqlalchemy import inspect

def check_users():
    with db.engine.connect() as connection:
        result = connection.execute("SELECT * FROM user;")
        users = result.fetchall()
        if not users:
            print("No users found in the database.")
        else:
            for user in users:
                print(user)

def check_admin_users():
    with db.session.begin():
        admin1 = User.query.filter_by(username='admin1').first()

        if admin1:
            print("Admin1 exists in the database.")
        else:
            print("Admin1 does not exist in the database.")

def check_database_schema():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)

    for table in tables:
        columns = inspector.get_columns(table)
        print(f"Columns in {table}:", [column['name'] for column in columns])

def check_shift_table():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('shift')
    print("Columns in 'shift' table:", [column['name'] for column in columns])

if __name__ == "__main__":
    check_users()
    check_admin_users()
    check_database_schema()
    with db.engine.connect() as connection:
        check_shift_table()