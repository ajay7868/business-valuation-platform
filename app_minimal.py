#!/usr/bin/env python3
"""
Minimal working app with authentication to test the issue
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import secrets
import string
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
CORS(app)

# Simple in-memory storage for testing
users = {}
rate_limits = {}

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_verification_token():
    """Generate a secure verification token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'development',
        'version': '1.0.0'
    })

@app.route('/api/auth/test', methods=['GET'])
def auth_test():
    """Test endpoint to verify authentication system is working"""
    return jsonify({
        'status': 'success',
        'message': 'Authentication system is working',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.json
        print(f"Signup request received: {data}")
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password') or not data.get('confirm_password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        confirm_password = data['confirm_password']
        mobile = data.get('mobile', '').strip()
        
        # Validate email format
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if passwords match
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        # Validate password strength
        is_valid, message = is_valid_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        if email in users:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        verification_token = generate_verification_token()
        users[email] = {
            'email': email,
            'password_hash': hash_password(password),
            'mobile': mobile,
            'email_verified': False,
            'verification_token': verification_token,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"User created successfully: {email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Account created successfully. Please check your email for verification.',
            'email_sent': True,
            'email_message': 'Verification email sent (mock)'
        }), 201
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        print(f"Login request received: {data}")
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user
        if email not in users:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = users[email]
        
        if not user['email_verified']:
            return jsonify({'error': 'Email not verified. Please check your email for verification link.'}), 403
        
        if hash_password(password) != user['password_hash']:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        
        print(f"User logged in successfully: {email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': {
                'email': user['email'],
                'mobile': user['mobile'],
                'email_verified': user['email_verified']
            }
        })
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/verify/<token>', methods=['GET'])
def verify_email(token):
    """Email verification endpoint"""
    try:
        print(f"Verification request for token: {token}")
        
        # Find user with this token
        user_email = None
        for email, user in users.items():
            if user.get('verification_token') == token:
                user_email = email
                break
        
        if not user_email:
            return jsonify({'error': 'Invalid verification token'}), 400
        
        user = users[user_email]
        
        if user['email_verified']:
            return jsonify({'error': 'Email already verified'}), 400
        
        # Verify email
        user['email_verified'] = True
        user['verification_token'] = None
        
        print(f"Email verified successfully: {user_email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Email verified successfully! You can now log in.'
        })
        
    except Exception as e:
        print(f"Email verification error: {str(e)}")
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        print("Logout request received")
        # In a real app, you would invalidate the session
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        })
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile - mock implementation"""
    try:
        print("Profile request received")
        # In a real app, you would get the user from the session
        return jsonify({
            'status': 'success',
            'message': 'Profile endpoint working'
        })
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@app.route('/api/auth/rate-limit-status', methods=['GET'])
def get_rate_limit_status_endpoint():
    """Get current rate limit status for user"""
    try:
        print("Rate limit status request received")
        # Mock rate limit status
        return jsonify({
            'status': 'success',
            'upload': {
                'attempts': 0,
                'max_attempts': 2,
                'blocked': False,
                'blocked_until': None
            },
            'report_generation': {
                'attempts': 0,
                'max_attempts': 2,
                'blocked': False,
                'blocked_until': None
            }
        })
    except Exception as e:
        print(f"Rate limit status error: {str(e)}")
        return jsonify({'error': f'Failed to get rate limit status: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting minimal authentication app...")
    print("📝 Available endpoints:")
    print("  - GET  /api/health")
    print("  - GET  /api/auth/test")
    print("  - POST /api/auth/signup")
    print("  - POST /api/auth/login")
    print("  - GET  /api/auth/verify/<token>")
    print("  - POST /api/auth/logout")
    print("  - GET  /api/auth/profile")
    print("  - GET  /api/auth/rate-limit-status")
    app.run(debug=True, host='0.0.0.0', port=5001)
