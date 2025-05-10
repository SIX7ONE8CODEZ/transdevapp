from sqlalchemy import create_engine, text

# Database connection
DATABASE_URI = 'sqlite:///instance/transdev.db'
engine = create_engine(DATABASE_URI)

# Add the 'students' column to the 'shift' table
def add_students_column():
    with engine.connect() as connection:
        try:
            connection.execute(text("ALTER TABLE shift ADD COLUMN students TEXT"))
            print("Column 'students' added successfully.")
        except Exception as e:
            print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_students_column()