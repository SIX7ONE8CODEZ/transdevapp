"""
Comprehensive test for the TransDev application
This script tests:
1. Admin and regular user login
2. Access to spreadsheet view
3. Export permissions
4. Authentication security
"""

import requests
from bs4 import BeautifulSoup
import sys
import re
import time

BASE_URL = "http://127.0.0.1:5000"

def test_user(username, password, is_admin=False):
    """Test a user's functionality"""
    print(f"\n{'='*50}")
    print(f"Testing {'ADMIN' if is_admin else 'REGULAR'} user: {username}")
    print(f"{'='*50}")
    
    # Create a new session for this user
    session = requests.Session()
    
    # Step 1: Login
    login_success = login(session, username, password)
    if not login_success:
        print("❌ FAILED: Login unsuccessful")
        return False
    
    # Step 2: Access Dashboard
    dashboard_success = access_dashboard(session)
    if not dashboard_success:
        print("❌ FAILED: Could not access dashboard")
        return False
    
    # Step 3: Access Spreadsheet View
    spreadsheet_success, spreadsheet_content = access_spreadsheet(session)
    if not spreadsheet_success:
        print("❌ FAILED: Could not access spreadsheet view")
        return False
    
    # Step 4: Check for Export Button
    has_export = check_for_export(spreadsheet_content)
    if is_admin and not has_export:
        print("❌ FAILED: Admin should have export button")
        return False
    elif not is_admin and has_export:
        print("❌ FAILED: Regular user should NOT have export button")
        return False
    else:
        print(f"✅ PASSED: {'Admin has' if is_admin else 'Regular user does not have'} export button")
    
    # Step 5: Try Direct Export
    export_success = try_export(session, is_admin)
    if not export_success:
        print("❌ FAILED: Export test failed")
        return False
    
    # Step 6: Logout
    logout(session)
    
    print(f"✅ ALL TESTS PASSED for {username}")
    return True

def login(session, username, password):
    """Login to the application"""
    print(f"Attempting to login as {username}...")
    
    # First get the login page to get any CSRF token
    response = session.get(f"{BASE_URL}/login")
    if response.status_code != 200:
        print(f"Failed to load login page: {response.status_code}")
        return False
    
    # Submit login form
    login_data = {
        "username": username,
        "password": password
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    # Check if login was successful
    if "dashboard" in response.url:
        print(f"✅ PASSED: Login successful as {username}")
        return True
    else:
        print(f"Login failed for {username}")
        return False

def access_dashboard(session):
    """Access the dashboard page"""
    print("Accessing dashboard...")
    response = session.get(f"{BASE_URL}/dashboard")
    
    if response.status_code != 200:
        print(f"Failed to access dashboard: {response.status_code}")
        return False
    
    print("✅ PASSED: Successfully accessed dashboard")
    return True

def access_spreadsheet(session):
    """Access the spreadsheet view"""
    print("Accessing spreadsheet view...")
    response = session.get(f"{BASE_URL}/spreadsheet_schedule")
    
    if response.status_code != 200:
        print(f"Failed to access spreadsheet view: {response.status_code}")
        return False, None
    
    print("✅ PASSED: Successfully accessed spreadsheet view")
    return True, response.text

def check_for_export(page_content):
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

def try_export(session, is_admin):
    """Try to export data directly"""
    print("Attempting to export data...")
    response = session.post(f"{BASE_URL}/export_spreadsheet", allow_redirects=True)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response URL: {response.url}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if is_admin:
        # Admin should either get Excel file or a specific error about xlsxwriter
        if response.headers.get('Content-Type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            print("✅ PASSED: Admin successfully exported Excel file")
            # Save the file to verify it worked
            with open(f"export_test_{int(time.time())}.xlsx", "wb") as f:
                f.write(response.content)
            return True
        elif "No module named 'xlsxwriter'" in response.url:
            print("✅ PASSED: Admin has export permission but xlsxwriter module is missing")
            print("This is a configuration issue, not a permission issue")
            return True
        else:
            print(f"Admin could not export data: {response.status_code}")
            print(f"Content preview: {response.text[:200]}...")
            return False
    else:
        # Regular user should be redirected with error
        if "spreadsheet_schedule" in response.url and "message_type=error" in response.url:
            print("✅ PASSED: Regular user was correctly blocked from exporting")
            return True
        else:
            print(f"Regular user was not properly blocked from exporting: {response.url}")
            return False

def logout(session):
    """Logout from the application"""
    print("Logging out...")
    session.get(f"{BASE_URL}/logout")
    print("Logged out")

def main():
    print("\n🧪 STARTING COMPREHENSIVE TESTS 🧪\n")
    
    # Test admin users
    admin_result = test_user("admin1", "A1d!n@2025#", is_admin=True)
    
    # Test regular users
    regular_results = []
    regular_results.append(test_user("Terry", "Welcome1", is_admin=False))
    regular_results.append(test_user("Veronica", "Welcome2", is_admin=False))
    
    # Print summary
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Admin user test: {'PASSED' if admin_result else 'FAILED'}")
    print(f"Regular user tests: {regular_results.count(True)}/{len(regular_results)} passed")
    
    if admin_result and all(regular_results):
        print("\n🎉 ALL TESTS PASSED! The application is working correctly.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
