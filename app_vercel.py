#!/usr/bin/env python3
"""
Vercel-optimized Flask app for Business Valuation Platform
Simplified version without heavy dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
from datetime import datetime
import hashlib
import secrets
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'f6c65df53e68354a73b4b2411d9b254a8224e171107854d7970a37f0fb19c43c')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# CORS Configuration - Production Ready
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, supports_credentials=True, origins=allowed_origins)

# File upload security configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'xls', 'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_security(file):
    """Validate file for security threats"""
    if not file or not file.filename:
        return False, "No file provided"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
    
    return True, "File validation passed"

# Database configuration
DB_PATH = 'valuation_platform.db'

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        if conn:
            conn.close()
            db_status = 'connected'
        else:
            db_status = 'disconnected'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'database': f'SQLite ({db_status})',
            'platform': 'Vercel'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': 'Health check failed'
        }), 500

# Authentication endpoints
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
        mobile = data.get('mobile', '')

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate password
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Check if user already exists
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 503

        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400

        # Create user
        verification_token = secrets.token_urlsafe(32)
        cursor.execute('''
            INSERT INTO users (email, password_hash, mobile, verification_token)
            VALUES (?, ?, ?, ?)
        ''', (email, password_hash, mobile, verification_token))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'verification_token': verification_token
        }), 201

    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        print(f"Login request received: {data}")
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400

        email = data['email'].lower().strip()
        password = data['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Check user credentials
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 503

        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, mobile, email_verified, created_at, last_login
            FROM users WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))

        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'Invalid email or password'}), 401

        # Update last login
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
        conn.commit()
        conn.close()

        # Create session token
        session_token = secrets.token_urlsafe(32)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'mobile': user['mobile'],
                'email_verified': bool(user['email_verified']),
                'created_at': user['created_at'],
                'last_login': user['last_login']
            },
            'session_token': session_token
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

# File upload endpoint (simplified for Vercel)
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint - simplified for Vercel"""
    try:
        print("File upload request received")
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Validate file security
        is_valid, message = validate_file_security(file)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # For Vercel, we'll just return a mock response since file storage is limited
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        
        # Mock extracted data for demonstration
        mock_extracted_data = {
            'file_size': file.tell(),
            'file_type': 'excel' if filename.endswith(('.xlsx', '.xls')) else 'text',
            'filename': safe_filename,
            'mapped_fields': {
                'company_name': '100%',
                'total_assets': 'Cash'
            },
            'summary': {
                'Financial Data': {
                    'column_names': ['Item', 'Amount', 'Percentage of Revenue'],
                    'columns': 3,
                    'rows': 13
                }
            }
        }
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': safe_filename,
            'extracted_data': mock_extracted_data
        }), 200

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

# Valuation endpoint (simplified)
@app.route('/api/valuation', methods=['POST'])
def calculate_valuation():
    """Calculate business valuation - simplified for Vercel"""
    try:
        data = request.get_json()
        print(f"Valuation request received: {data}")
        
        # Mock valuation calculation
        company_name = data.get('company_name', 'Unknown Company')
        revenue = float(data.get('revenue', 0))
        ebitda = float(data.get('ebitda', 0))
        net_income = float(data.get('net_income', 0))
        total_assets = float(data.get('total_assets', 0))
        total_liabilities = float(data.get('total_liabilities', 0))
        
        # Simple valuation calculation
        calculated_value = max(revenue * 0.5, ebitda * 5, net_income * 10, total_assets - total_liabilities)
        
        valuation_results = {
            'company_name': company_name,
            'calculated_value': calculated_value,
            'asset_value': total_assets - total_liabilities,
            'ebitda_multiple': 5.0,
            'method': 'Simplified Multiple Approach',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'valuation_results': valuation_results
        }), 200

    except Exception as e:
        print(f"Valuation error: {str(e)}")
        return jsonify({'error': 'Valuation calculation failed'}), 500

# SWOT analysis endpoint (simplified)
@app.route('/api/swot', methods=['POST'])
def generate_swot():
    """Generate SWOT analysis - simplified for Vercel"""
    try:
        data = request.get_json()
        print(f"SWOT request received: {data}")
        
        # Mock SWOT analysis
        swot_analysis = {
            'strengths': [
                'Strong financial performance',
                'Good market position',
                'Experienced management team'
            ],
            'weaknesses': [
                'Limited market diversification',
                'High dependency on key customers'
            ],
            'opportunities': [
                'Market expansion potential',
                'Technology advancement opportunities',
                'Strategic partnerships'
            ],
            'threats': [
                'Economic downturns',
                'Increased competition',
                'Regulatory changes'
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'swot_analysis': swot_analysis
        }), 200

    except Exception as e:
        print(f"SWOT error: {str(e)}")
        return jsonify({'error': 'SWOT analysis failed'}), 500

# Report generation endpoint (simplified)
@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Generate business valuation report - simplified for Vercel"""
    try:
        data = request.get_json()
        print(f"Report generation request received: {data}")
        
        company_name = data.get('company_name', 'Unknown Company')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"{company_name.replace(' ', '_')}_Valuation_Report_{timestamp}.txt"
        
        report_data = {
            'report_id': f"RPT_{timestamp}",
            'company_name': company_name,
            'generated_at': datetime.now().isoformat(),
            'status': 'completed',
            'message': 'Report generated successfully',
            'format': 'txt'
        }
        
        return jsonify({
            'status': 'success',
            'report_filename': report_filename,
            'download_url': f'/api/report/download/{report_filename}',
            'report': report_data
        }), 200

    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

# Report download endpoint (simplified)
@app.route('/api/report/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated report - simplified for Vercel"""
    try:
        print(f"Report download request for: {filename}")
        
        # Generate simple report content
        report_content = f"""
BUSINESS VALUATION REPORT
========================

Report: {filename}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a simplified report generated for Vercel deployment.
For full functionality, please use the complete application.

========================
END OF REPORT
========================
        """.strip()
        
        from flask import Response
        return Response(
            report_content,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/plain; charset=utf-8'
            }
        )

    except Exception as e:
        print(f"Report download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# Root endpoint
@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Business Valuation Platform API',
        'version': '1.0.0',
        'status': 'running',
        'platform': 'Vercel'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
