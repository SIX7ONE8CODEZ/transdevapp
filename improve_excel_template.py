"""
This script improves the Excel template for importing by:
1. Including sample data that matches the database structure
2. Adding validation rules and cell formatting
3. Adding instructions on how to import properly
"""
import pandas as pd
import os
from datetime import datetime, timedelta
import xlsxwriter

# Create a more user-friendly template
output_file = 'static/schedule_template.xlsx'

# Create sample data
now = datetime.now()
tomorrow = now + timedelta(days=1)

# Sample data with clear headers
sample_data = {
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

df = pd.DataFrame(sample_data)

# Create Excel file with improved formatting
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    # Write the data to the worksheet
    df.to_excel(writer, sheet_name='Schedule Template', index=False, startrow=1)
    
    # Get the workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Schedule Template']
    
    # Add title
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    worksheet.merge_range('A1:F1', 'TransDev Schedule Import Template', title_format)
    
    # Add header formatting
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D8E4BC',
        'border': 1,
        'align': 'center'
    })
    
    # Apply header formatting
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(1, col_num, value, header_format)
    
    # Format each column appropriately
    date_format = workbook.add_format({'num_format': 'mm/dd/yyyy hh:mm AM/PM'})
    text_format = workbook.add_format({'text_wrap': True})
    
    # Set column widths
    worksheet.set_column('A:A', 15)  # Employee
    worksheet.set_column('B:B', 25)  # Assignment
    worksheet.set_column('C:D', 20)  # Start/End Time
    worksheet.set_column('E:E', 15)  # Status
    worksheet.set_column('F:F', 30)  # Participants
    
    # Format the datetime columns
    worksheet.set_column('C:D', 20, date_format)
    
    # Add instructions worksheet
    instructions = workbook.add_worksheet('Instructions')
    
    # Instructions formatting
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'font_color': '#1F497D'
    })
    
    heading_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'font_color': '#1F497D'
    })
    
    text_format = workbook.add_format({
        'text_wrap': True
    })
    
    # Add instructions content
    instructions.set_column('A:A', 10)
    instructions.set_column('B:B', 70)
    
    row = 0
    instructions.write(row, 1, 'TransDev Schedule Import Instructions', title_format)
    row += 2
    
    instructions.write(row, 1, 'Required Columns', heading_format)
    row += 1
    instructions.write(row, 1, 'The following columns are required for the import to work correctly:', text_format)
    row += 1
    
    required_columns = [
        ('Employee', 'Username of an existing employee in the system (admin1, admin2, admin3, etc.)'),
        ('Assignment', 'Description of the training or work assignment'),
        ('Start Time', 'Start date and time in MM/DD/YYYY HH:MM AM/PM format'),
        ('End Time', 'End date and time in MM/DD/YYYY HH:MM AM/PM format'),
        ('Status', 'Current status of the shift (Scheduled, Swap Requested, Approved)'),
        ('Participants', 'Optional: List of participants/students involved in this shift')
    ]
    
    for col, desc in required_columns:
        instructions.write(row, 1, f"• {col}: {desc}", text_format)
        row += 1
    
    row += 1
    instructions.write(row, 1, 'Import Process', heading_format)
    row += 1
    
    import_steps = [
        'Fill out the Schedule Template sheet with your data. You can copy data from another source or enter it directly.',
        'Make sure all required fields are filled in and in the correct format.',
        'Save this Excel file to your computer.',
        'Go to the TransDev Spreadsheet View page.',
        'Click the "Import Excel" button and select this file.',
        'The system will process your data and add it to the schedule.'
    ]
    
    for i, step in enumerate(import_steps):
        instructions.write(row, 1, f"{i+1}. {step}", text_format)
        row += 1
    
    row += 1
    instructions.write(row, 1, 'Notes and Troubleshooting', heading_format)
    row += 1
    
    notes = [
        'Only admin users (admin1, admin2, admin3) can import data.',
        'Dates must be in MM/DD/YYYY HH:MM AM/PM format (e.g., 05/21/2025 10:30 AM).',
        'Employee names must match exactly with existing users in the system.',
        'If you get errors during import, check that your data matches the required format.',
        'The ID column is optional. If provided, the system will update existing shifts instead of creating new ones.'
    ]
    
    for note in notes:
        instructions.write(row, 1, f"• {note}", text_format)
        row += 1

print(f"Created improved Excel template at {output_file}")
print("The template includes:")
print("- Sample data with proper formatting")
print("- Instructions for importing")
print("- Column descriptions and requirements")
