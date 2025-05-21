"""
This script tests the Excel import functionality directly by calling the import functions
rather than going through the web interface.
"""
from app import app, db, User, Shift
import pandas as pd
import os
from datetime import datetime
import tempfile
from werkzeug.datastructures import FileStorage

# Path to the test Excel file
test_file_path = 'test_import_data.xlsx'

if not os.path.exists(test_file_path):
    print(f"Test file not found: {test_file_path}")
    exit(1)

print(f"Testing import of file: {test_file_path}")

with app.app_context():
    try:
        # Read the Excel file
        print("Reading Excel file...")
        df = pd.read_excel(test_file_path)
        print(f"Excel data read successfully with {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        
        # Validate required columns
        required_columns = ['Employee', 'Assignment', 'Start Time', 'End Time', 'Status']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            print(f"Available columns: {df.columns.tolist()}")
            exit(1)
        
        # Process data and update database
        success_count = 0
        error_count = 0
        
        print("\nProcessing rows:")
        for idx, row in df.iterrows():
            try:
                print(f"Row {idx}: {row['Employee']} - {row['Assignment']}")
                
                # Get employee
                employee_name = str(row['Employee'])
                employee = User.query.filter_by(username=employee_name).first()
                
                if not employee:
                    print(f"❌ Employee not found: {employee_name}")
                    error_count += 1
                    continue
                
                employee_id = employee.id
                
                # Parse dates
                from app import parse_datetime
                
                try:
                    # Handle different date formats
                    start_time_str = str(row['Start Time'])
                    end_time_str = str(row['End Time'])
                    
                    start_time = parse_datetime(start_time_str)
                    end_time = parse_datetime(end_time_str)
                    
                    if not start_time or not end_time:
                        print(f"❌ Could not parse dates: {start_time_str} - {end_time_str}")
                        error_count += 1
                        continue
                        
                    print(f"Parsed dates: {start_time} - {end_time}")
                except Exception as e:
                    print(f"❌ Date parsing error: {e}")
                    error_count += 1
                    continue
                
                # Get other fields
                assignment = str(row['Assignment'])
                status = str(row['Status'])
                participants = str(row.get('Participants', ''))
                
                # Create new shift
                new_shift = Shift(
                    employee_id=employee_id,
                    assignment=assignment,
                    start_time=start_time,
                    end_time=end_time,
                    status=status,
                    students=participants
                )
                db.session.add(new_shift)
                print(f"✅ Created new shift for {employee_name}")
                
                success_count += 1
            
            except Exception as e:
                print(f"❌ Error processing row: {e}")
                error_count += 1
        
        # Commit changes
        try:
            db.session.commit()
            print(f"\n✅ Database committed: {success_count} successful, {error_count} errors")
        except Exception as e:
            print(f"\n❌ Error during commit: {e}")
            db.session.rollback()
    
    except Exception as e:
        print(f"\n❌ Exception during import: {e}")

print("\nImport test complete.")
