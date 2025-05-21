import pandas as pd
from datetime import datetime, timedelta

# Create a test Excel file for importing
now = datetime.now()
tomorrow = now + timedelta(days=1)

# Create a dataframe with the required columns
data = {
    'Employee': ['admin1', 'admin2', 'admin3'],
    'Assignment': ['Training Session A', 'Training Session B', 'Evaluation Session'],
    'Start Time': [
        now.strftime('%m/%d/%Y %I:%M %p'),
        (now + timedelta(hours=2)).strftime('%m/%d/%Y %I:%M %p'),
        tomorrow.strftime('%m/%d/%Y %I:%M %p')
    ],
    'End Time': [
        (now + timedelta(hours=1)).strftime('%m/%d/%Y %I:%M %p'),
        (now + timedelta(hours=3)).strftime('%m/%d/%Y %I:%M %p'),
        (tomorrow + timedelta(hours=1)).strftime('%m/%d/%Y %I:%M %p')
    ],
    'Status': ['Scheduled', 'Scheduled', 'Scheduled'],
    'Participants': ['Student1, Student2', 'Student3, Student4', 'Student5']
}

df = pd.DataFrame(data)

# Save the dataframe to an Excel file
filename = 'test_import_data.xlsx'
df.to_excel(filename, index=False)

print(f"Created test import file: {filename}")
print("Sample data:")
print(df.head())
