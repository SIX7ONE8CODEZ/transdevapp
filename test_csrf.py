from app import app
import re

# Extract the routes from app.py
routes = [rule.rule for rule in app.url_map.iter_rules()]
print("Routes defined in the application:")
for route in routes:
    print(f" - {route}")

# Check if CSRF protection is enabled
has_csrf = False
try:
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)
    has_csrf = True
    print("\nCSRF protection is now enabled")
except ImportError:
    print("\nflask_wtf is not installed; CSRF protection is not available")

# Check login.html for CSRF token
with open('templates/login.html', 'r') as f:
    login_form = f.read()
    
has_csrf_token = re.search(r'<input.*?name="csrf_token"', login_form) is not None
print(f"\nCSRF token in login form: {'Yes' if has_csrf_token else 'No'}")

# If CSRF token is missing but CSRF protection is enabled, suggest a fix
if has_csrf and not has_csrf_token:
    print("\nWarning: CSRF protection is enabled but login form doesn't have csrf_token field.")
    print("This could cause authentication failures due to CSRF validation.")
    print("Fix: Add {{ form.csrf_token }} to your login form, or disable CSRF protection.")
elif not has_csrf and has_csrf_token:
    print("\nWarning: CSRF token field exists in login form but CSRF protection is not enabled in Flask.")
    print("Fix: Import and initialize CSRFProtect in your app.py file.")
elif not has_csrf and not has_csrf_token:
    print("\nCSRF protection is not used in this application. This is consistent with your form templates.")
