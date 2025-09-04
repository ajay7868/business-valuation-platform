import hashlib
import secrets
import string
from datetime import datetime, timedelta
from flask import request, jsonify
from models import db, RateLimit, UserActivity
import re

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

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

def get_client_info():
    """Get client IP and device information"""
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    device_id = request.headers.get('User-Agent', 'Unknown')
    return ip_address, device_id

def check_rate_limit(endpoint, max_attempts=2, block_duration=3600):
    """Check rate limit for an endpoint"""
    ip_address, device_id = get_client_info()
    
    # Check if already blocked
    existing_block = RateLimit.query.filter_by(
        ip_address=ip_address,
        endpoint=endpoint
    ).filter(
        RateLimit.blocked_until > datetime.utcnow()
    ).first()
    
    if existing_block:
        return False, f"Rate limit exceeded. Try again after {existing_block.blocked_until.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Get or create rate limit record
    rate_limit = RateLimit.query.filter_by(
        ip_address=ip_address,
        endpoint=endpoint
    ).first()
    
    if not rate_limit:
        rate_limit = RateLimit(
            ip_address=ip_address,
            device_id=device_id,
            endpoint=endpoint
        )
        db.session.add(rate_limit)
    else:
        # Check if within time window (24 hours)
        time_diff = datetime.utcnow() - rate_limit.first_attempt
        if time_diff > timedelta(hours=24):
            # Reset counter after 24 hours
            rate_limit.attempt_count = 1
            rate_limit.first_attempt = datetime.utcnow()
        else:
            rate_limit.attempt_count += 1
        
        rate_limit.last_attempt = datetime.utcnow()
        
        # Block if max attempts exceeded
        if rate_limit.attempt_count > max_attempts:
            rate_limit.blocked_until = datetime.utcnow() + timedelta(seconds=block_duration)
            db.session.commit()
            return False, f"Rate limit exceeded. Please sign up to continue. Try again after {rate_limit.blocked_until.strftime('%Y-%m-%d %H:%M:%S')}"
    
    db.session.commit()
    return True, f"Attempt {rate_limit.attempt_count}/{max_attempts}"

def log_user_activity(user_id, action, success=True):
    """Log user activity for audit purposes"""
    ip_address, device_id = get_client_info()
    
    activity = UserActivity(
        user_id=user_id,
        ip_address=ip_address,
        device_id=device_id,
        action=action,
        success=success
    )
    
    db.session.add(activity)
    db.session.commit()

def require_auth(f):
    """Decorator to require authentication for protected endpoints"""
    from functools import wraps
    from flask_login import current_user, login_required
    
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.email_verified:
            return jsonify({
                'error': 'Email not verified',
                'message': 'Please verify your email address before accessing this feature'
            }), 403
        return f(*args, **kwargs)
    
    return decorated_function

def get_rate_limit_status(endpoint):
    """Get current rate limit status for user"""
    ip_address, device_id = get_client_info()
    
    rate_limit = RateLimit.query.filter_by(
        ip_address=ip_address,
        endpoint=endpoint
    ).first()
    
    if not rate_limit:
        return {
            'attempts': 0,
            'max_attempts': 2,
            'blocked': False,
            'blocked_until': None
        }
    
    return {
        'attempts': rate_limit.attempt_count,
        'max_attempts': 2,
        'blocked': rate_limit.blocked_until and rate_limit.blocked_until > datetime.utcnow(),
        'blocked_until': rate_limit.blocked_until.isoformat() if rate_limit.blocked_until else None
    }
