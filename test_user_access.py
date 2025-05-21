import requests
from bs4 import BeautifulSoup
import sys
import re

BASE_URL = "http://127.0.0.1:5000"
SESSION = requests.Session()

def login(username, password):
    """Login to the application"""
    print(f"Attempting to login as {username}...")
    
    # First get the login page to get any CSRF token
    response = SESSION.get(f"{BASE_URL}/login")
    if response.status_code != 200:
        print(f"Failed to load login page: {response.status_code}")
        return False
    
    # Submit login form
    login_data = {
        "username": username,
        "password": password
    }
    
    response = SESSION.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    # Check if login was successful
    if "dashboard" in response.url:
        print(f"Login successful as {username}")
        return True
    else:
        print(f"Login failed for {username}")
        return False

def get_spreadsheet_view():
    """Get the spreadsheet view page"""
    print("Accessing spreadsheet view...")
    response = SESSION.get(f"{BASE_URL}/spreadsheet_schedule")
    
    if response.status_code != 200:
        print(f"Failed to access spreadsheet view: {response.status_code}")
        return None
    
    print("Successfully accessed spreadsheet view")
    return response.text

def check_export_button(page_content):
    """Check if the export button is visible on the page"""
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Look for the form with export_spreadsheet action
    export_forms = soup.find_all("form", action=lambda x: x and "export_spreadsheet" in x)
    
    if export_forms:
        print(f"Found {len(export_forms)} export form(s)")
        return True
    else:
        print("No export form found")
        return False

def try_export():
    """Try to export data directly"""
    print("Attempting to export data...")
    response = SESSION.post(f"{BASE_URL}/export_spreadsheet", allow_redirects=True)
    
    if "spreadsheet_schedule" in response.url and "message_type=error" in response.url:
        print("Export attempt was blocked, as expected for regular users")
        return True
    elif response.headers.get('Content-Type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        print("Export successful, received Excel file")
        return True
    else:
        print(f"Unexpected response when trying to export: {response.status_code}")
        return False

def test_user(username, password, is_admin=False):
    """Test a user's access"""
    print(f"\n{'='*50}")
    print(f"Testing {'ADMIN' if is_admin else 'REGULAR'} user: {username}")
    print(f"{'='*50}")
    
    # Login
    if not login(username, password):
        return
    
    # Get spreadsheet view
    page_content = get_spreadsheet_view()
    if not page_content:
        return
    
    # Check for export button
    has_export_button = check_export_button(page_content)
    
    if is_admin:
        if not has_export_button:
            print("❌ FAILED: Admin should have export button")
        else:
            print("✅ PASSED: Admin has export button")
    else:
        if has_export_button:
            print("❌ FAILED: Regular user should NOT have export button")
        else:
            print("✅ PASSED: Regular user does not have export button")
    
    # Try export
    export_result = try_export()
    
    if is_admin:
        if not export_result:
            print("❌ FAILED: Admin should be able to export")
        else:
            print("✅ PASSED: Admin can export")
    else:
        if export_result:
            print("✅ PASSED: Regular user was correctly blocked from exporting")
        else:
            print("❌ FAILED: Regular user should be blocked from exporting")
    
    # Logout
    SESSION.get(f"{BASE_URL}/logout")
    print("Logged out")

def main():
    # Test admin user
    test_user("admin1", "A1d!n@2025#", is_admin=True)
    
    # Test regular users
    test_user("Terry", "Welcome1", is_admin=False)
    test_user("Veronica", "Welcome2", is_admin=False)
    test_user("Sisay", "Welcome3", is_admin=False)

if __name__ == "__main__":
    main()
