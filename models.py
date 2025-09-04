from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(20), nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class RateLimit(db.Model):
    """Rate limiting model to track IP/device attempts"""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 compatible
    device_id = db.Column(db.String(100), nullable=True)   # Browser fingerprint
    endpoint = db.Column(db.String(100), nullable=False)   # API endpoint
    attempt_count = db.Column(db.Integer, default=1)
    first_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    blocked_until = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<RateLimit {self.ip_address}:{self.endpoint}>'

class UserActivity(db.Model):
    """Track user activities for audit purposes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)
    device_id = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # upload, report_generation, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<UserActivity {self.action} at {self.timestamp}>'
