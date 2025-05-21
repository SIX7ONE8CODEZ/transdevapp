from app import app, login_manager

# Check login manager configuration
print("Checking login manager configuration:")
print(f"Login view: {login_manager.login_view}")
print(f"Login message: {login_manager.login_message}")

# Add login view if not set
if not login_manager.login_view:
    print("Setting login_view to 'login'")
    login_manager.login_view = 'login'
    print(f"Login view is now: {login_manager.login_view}")
else:
    print("Login view already set correctly")
