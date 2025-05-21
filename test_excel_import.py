from app import app, db, User, Shift
import pandas as pd
import os
from datetime import datetime
import openpyxl
from flask import url_for

# First, let's ensure pandas and Excel libraries are working correctly
print("Testing Excel libraries:")
try:
    print("- pandas version:", pd.__version__)
    print("- openpyxl version:", openpyxl.__version__)
    print("✅ Excel libraries imported successfully")
except Exception as e:
    print("❌ Error with Excel libraries:", str(e))

# Check if the template file exists
template_path = os.path.join("static", "schedule_template.xlsx")
if os.path.exists(template_path):
    print(f"✅ Found template file: {template_path}")
else:
    print(f"❌ Template file not found at {template_path}")

# Test reading an Excel file
try:
    print("\nTesting Excel reading functionality:")
    # Check for any Excel files in the directory
    excel_files = [f for f in os.listdir() if f.endswith(('.xlsx', '.xls'))]
    
    if excel_files:
        test_file = excel_files[0]
        print(f"- Reading test file: {test_file}")
        df = pd.read_excel(test_file)
        print(f"- Successfully read Excel with {len(df)} rows and columns: {', '.join(df.columns)}")
        print("✅ Excel reading works")
    else:
        print("- No Excel files found in the current directory")
        # Create a simple test Excel file
        print("- Creating a test Excel file")
        test_df = pd.DataFrame({
            'Employee': ['admin1', 'admin2'],
            'Assignment': ['Training 1', 'Training 2'],
            'Start Time': [datetime.now(), datetime.now()],
            'End Time': [datetime.now(), datetime.now()],
            'Status': ['Scheduled', 'Scheduled'],
            'Participants': ['Student1, Student2', 'Student3']
        })
        test_file = "test_import.xlsx"
        test_df.to_excel(test_file, index=False)
        print(f"- Created test file: {test_file}")
        
        # Now try to read it back
        df = pd.read_excel(test_file)
        print(f"- Successfully read test Excel with {len(df)} rows and columns: {', '.join(df.columns)}")
        print("✅ Excel reading and writing works")
except Exception as e:
    print(f"❌ Error testing Excel functionality: {str(e)}")

# Test the database connection
print("\nTesting database connection:")
with app.app_context():
    try:
        # Check if we can access User and Shift tables
        users = User.query.all()
        shifts = Shift.query.all()
        print(f"- Found {len(users)} users and {len(shifts)} shifts in the database")
        print("✅ Database connection works")
        
        # Print admin users for verification
        admin_users = [user for user in users if user.username in ['admin1', 'admin2', 'admin3']]
        if admin_users:
            print("- Admin users found:")
            for admin in admin_users:
                print(f"  * {admin.username} (ID: {admin.id})")
        else:
            print("❌ No admin users found in the database")
    except Exception as e:
        print(f"❌ Error accessing database: {str(e)}")

print("\nImport functionality diagnosis complete.")
