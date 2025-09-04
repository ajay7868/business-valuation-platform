#!/usr/bin/env python3
"""
SQLite-based authentication backend for Business Valuation Platform
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import string
from datetime import datetime, timedelta
import re
import os
import uuid
import pandas as pd
import openpyxl
from werkzeug.utils import secure_filename
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'f6c65df53e68354a73b4b2411d9b254a8224e171107854d7970a37f0fb19c43c')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Sessions last 30 days
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size (reduced for security)
app.config['UPLOAD_FOLDER'] = 'uploads'

# CORS Configuration - Production Ready
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, supports_credentials=True, origins=allowed_origins)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
log_file = os.environ.get('LOG_FILE', 'logs/app.log')

# Set up logging
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

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
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        print("Database not found, running initialization...")
        os.system('python3 init_db.py')
    else:
        print(f"Database found: {DB_PATH}")

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_verification_token():
    """Generate a secure verification token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def generate_session_token():
    """Generate a secure session token"""
    return str(uuid.uuid4())

def create_user_session(user_id, email):
    """Create a new user session"""
    session_token = generate_session_token()
    expires_at = datetime.now() + timedelta(days=30)
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_sessions (user_id, session_token, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, session_token, expires_at, datetime.now()))
        
        conn.commit()
        return session_token
    except sqlite3.Error as e:
        print(f"Session creation error: {e}")
        return None
    finally:
        conn.close()

def validate_session(session_token):
    """Validate a session token and return user info"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT us.user_id, us.expires_at, u.email, u.mobile, u.email_verified, u.created_at, u.last_login
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            WHERE us.session_token = ? AND us.expires_at > datetime('now')
        ''', (session_token,))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result['user_id'],
                'email': result['email'],
                'mobile': result['mobile'],
                'email_verified': result['email_verified'],
                'created_at': result['created_at'],
                'last_login': result['last_login']
            }
        return None
    except sqlite3.Error as e:
        print(f"Session validation error: {e}")
        return None
    finally:
        conn.close()

def delete_user_session(session_token):
    """Delete a user session"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Session deletion error: {e}")
        return False
    finally:
        conn.close()

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_data_from_excel(file_path):
    """Extract data from Excel files (.xlsx, .xls) with multiple fallback strategies"""
    print("Attempting Excel data extraction...")
    
    # Strategy 1: Try openpyxl engine
    try:
        excel_data = pd.read_excel(file_path, engine='openpyxl', sheet_name=None)
        if excel_data and any(not df.empty for df in excel_data.values()):
            print("✅ Successfully extracted with openpyxl engine")
            return process_excel_data(excel_data)
    except Exception as e:
        print(f"⚠️ openpyxl failed: {str(e)}")
    
    # Strategy 2: Try xlrd engine for older Excel files
    try:
        excel_data = pd.read_excel(file_path, engine='xlrd', sheet_name=None)
        if excel_data and any(not df.empty for df in excel_data.values()):
            print("✅ Successfully extracted with xlrd engine")
            return process_excel_data(excel_data)
    except Exception as e:
        print(f"⚠️ xlrd failed: {str(e)}")
    
    # Strategy 3: Try to read as CSV with different encodings
    try:
        print("🔄 Attempting CSV fallback...")
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                csv_data = pd.read_csv(file_path, encoding=encoding, sep=None, engine='python')
                if not csv_data.empty:
                    print(f"✅ Successfully extracted as CSV with {encoding} encoding")
                    return process_csv_data(csv_data)
            except Exception as e:
                print(f"⚠️ CSV fallback with {encoding} failed: {str(e)}")
                continue
    except Exception as e:
        print(f"⚠️ CSV fallback failed: {str(e)}")
    
    # Strategy 4: Try to read individual sheets one by one
    try:
        print("🔄 Attempting individual sheet extraction...")
        excel_data = {}
        for sheet_name in pd.ExcelFile(file_path).sheet_names:
            try:
                sheet_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                if not sheet_df.empty:
                    # Try to find headers in first few rows
                    for header_row in range(min(3, len(sheet_df))):
                        try:
                            # Use this row as header
                            sheet_with_header = pd.read_excel(
                                file_path, 
                                sheet_name=sheet_name, 
                                header=header_row
                            )
                            if not sheet_with_header.empty and len(sheet_with_header.columns) > 1:
                                excel_data[sheet_name] = sheet_with_header
                                print(f"✅ Extracted sheet '{sheet_name}' with header row {header_row}")
                                break
                        except:
                            continue
            except Exception as e:
                print(f"⚠️ Failed to extract sheet '{sheet_name}': {str(e)}")
                continue
        
        if excel_data:
            print("✅ Successfully extracted with individual sheet method")
            return process_excel_data(excel_data)
    except Exception as e:
        print(f"⚠️ Individual sheet extraction failed: {str(e)}")
    
    # Strategy 5: Last resort - try to read as text and parse manually
    try:
        print("🔄 Attempting manual text parsing...")
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Try to extract any readable text
        text_content = content.decode('utf-8', errors='ignore')
        if len(text_content) > 100:  # Only if we got substantial content
            print("✅ Successfully extracted text content")
            return process_text_data(text_content, file_path)
    except Exception as e:
        print(f"⚠️ Manual text parsing failed: {str(e)}")
    
    print("❌ All extraction methods failed")
    return None

def extract_data_from_csv(file_path):
    """Extract data from CSV files with multiple fallback strategies"""
    print("Attempting CSV data extraction...")
    
    # Try different encodings and separators
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    separators = [',', ';', '\t', '|']
    
    for encoding in encodings:
        for separator in separators:
            try:
                csv_data = pd.read_csv(file_path, encoding=encoding, sep=separator)
                if not csv_data.empty:
                    print(f"✅ Successfully extracted CSV with {encoding} encoding and '{separator}' separator")
                    return process_csv_data(csv_data)
            except Exception as e:
                print(f"⚠️ CSV extraction with {encoding} and '{separator}' failed: {str(e)}")
                continue
    
    # Try with automatic separator detection
    try:
        print("🔄 Attempting automatic separator detection...")
        csv_data = pd.read_csv(file_path, encoding='utf-8', sep=None, engine='python')
        if not csv_data.empty:
            print("✅ Successfully extracted CSV with automatic separator detection")
            return process_csv_data(csv_data)
    except Exception as e:
        print(f"⚠️ Automatic separator detection failed: {str(e)}")
    
    print("❌ All CSV extraction methods failed")
    return None

def process_excel_data(excel_data):
    """Process extracted Excel data into standardized format"""
    extracted_data = {
        'file_type': 'excel',
        'sheets': {},
        'summary': {}
    }
    
    # Process each sheet
    for sheet_name, sheet_df in excel_data.items():
        if sheet_df.empty:
            continue
            
        # Convert DataFrame to list of dictionaries
        sheet_data = sheet_df.to_dict('records')
        
        # Clean the data - remove rows with all NaN values
        cleaned_sheet_data = []
        for row in sheet_data:
            # Check if row has any non-NaN values
            if any(pd.notna(value) for value in row.values()):
                # Clean NaN values
                cleaned_row = {}
                for key, value in row.items():
                    if pd.isna(value):
                        cleaned_row[key] = ''
                    else:
                        cleaned_row[key] = value
                cleaned_sheet_data.append(cleaned_row)
        
        if cleaned_sheet_data:
            extracted_data['sheets'][sheet_name] = cleaned_sheet_data
            
            # Create summary for this sheet
            extracted_data['summary'][sheet_name] = {
                'rows': len(cleaned_sheet_data),
                'columns': len(cleaned_sheet_data[0]) if cleaned_sheet_data else 0,
                'column_names': list(cleaned_sheet_data[0].keys()) if cleaned_sheet_data else []
            }
    
    # Add mapped fields for form prefilling
    if extracted_data['sheets']:
        best_mapped_data = {}
        best_score = 0
        
        for sheet_name, sheet_data in extracted_data['sheets'].items():
            print(f"📊 Processing sheet: {sheet_name}")
            mapped_data = map_csv_data_to_form_fields(sheet_data)
            
            if mapped_data:
                field_score = len(mapped_data)
                print(f"📊 Sheet '{sheet_name}' mapped {field_score} fields")
                
                if field_score > best_score:
                    best_score = field_score
                    best_mapped_data = mapped_data
                    print(f"📊 Sheet '{sheet_name}' is now the best match with {field_score} fields")
        
        if best_mapped_data:
            extracted_data['mapped_fields'] = best_mapped_data
            print(f"🎯 Using best sheet with {best_score} mapped fields")
        else:
            print("⚠️ No suitable data found in any sheet for mapping")
    
    return extracted_data

def process_csv_data(csv_df):
    """Process extracted CSV data into standardized format"""
    extracted_data = {
        'file_type': 'csv',
        'data': csv_df.to_dict('records'),
        'summary': {
            'rows': len(csv_df),
            'columns': len(csv_df.columns),
            'column_names': list(csv_df.columns)
        }
    }
    
    # Add mapped fields
    mapped_data = map_csv_data_to_form_fields(extracted_data['data'])
    if mapped_data:
        extracted_data['mapped_fields'] = mapped_data
    
    return extracted_data

def process_text_data(text_content, file_path):
    """Process text content into standardized format"""
    extracted_data = {
        'file_type': 'text',
        'content': text_content[:1000],  # Limit content length
        'summary': {
            'rows': len(text_content.split('\n')),
            'columns': 1,
            'column_names': ['text_content']
        }
    }
    
    # Try to extract any structured data from text
    lines = text_content.split('\n')
    structured_data = []
    
    for line in lines[:50]:  # Process first 50 lines
        if len(line.strip()) > 10:  # Only meaningful lines
            # Try to split by common delimiters
            for delimiter in [',', ';', '\t', '|']:
                parts = line.split(delimiter)
                if len(parts) > 2:  # At least 3 columns
                    row_data = {f"col_{i}": str(part).strip() for i, part in enumerate(parts)}
                    structured_data.append(row_data)
                    break
    
    if structured_data:
        extracted_data['structured_data'] = structured_data
        extracted_data['summary']['rows'] = len(structured_data)
        extracted_data['summary']['columns'] = len(structured_data[0]) if structured_data else 0
        extracted_data['summary']['column_names'] = list(structured_data[0].keys()) if structured_data else []
        
        # Try to map structured data
        mapped_data = map_csv_data_to_form_fields(structured_data)
        if mapped_data:
            extracted_data['mapped_fields'] = mapped_data
    
    return extracted_data

def map_excel_financial_data(data):
    """Map Excel financial data with Item/Amount structure to form fields"""
    print("🔄 Processing Excel financial data structure...")
    
    mapped_data = {}
    
    # Define item mappings
    item_mappings = {
        'revenue': ['revenue', 'sales', 'total revenue', 'gross revenue', 'net revenue'],
        'ebitda': ['ebitda', 'operating income', 'operating profit', 'operating earnings'],
        'net_income': ['net profit', 'net income', 'net earnings', 'profit', 'earnings'],
        'total_assets': ['total assets', 'assets', 'total asset'],
        'inventory': ['inventory', 'stock'],
        'accounts_receivable': ['accounts receivable', 'receivables', 'ar'],
        'cash': ['cash', 'cash and equivalents'],
        'total_liabilities': ['total liabilities', 'liabilities', 'debt']
    }
    
    # Process each row in the data
    for row in data:
        if 'Item' in row and 'Amount' in row:
            item = str(row['Item']).lower().strip()
            amount = row['Amount']
            
            # Try to match the item to a form field
            for form_field, patterns in item_mappings.items():
                for pattern in patterns:
                    if pattern in item:
                        # Convert amount to numeric if possible
                        try:
                            if isinstance(amount, (int, float)):
                                mapped_data[form_field] = amount
                            elif isinstance(amount, str) and amount.replace(',', '').replace('.', '').isdigit():
                                mapped_data[form_field] = float(amount.replace(',', ''))
                            else:
                                mapped_data[form_field] = amount
                            print(f"🔗 Mapped '{row['Item']}' → '{form_field}' (value: {mapped_data[form_field]})")
                            break
                        except (ValueError, TypeError):
                            mapped_data[form_field] = amount
                            print(f"🔗 Mapped '{row['Item']}' → '{form_field}' (value: {amount})")
                            break
                else:
                    continue
                break
    
    print(f"🎯 Final mapped data: {mapped_data}")
    return mapped_data

def map_csv_data_to_form_fields(data):
    """Dynamic field mapping system that intelligently maps any column name to form fields"""
    if not data or len(data) == 0:
        return None
    
    # Check if this is Excel data with Item/Amount structure (like Financial Data sheet)
    if isinstance(data, list) and len(data) > 0:
        first_row = data[0]
        if 'Item' in first_row and 'Amount' in first_row:
            return map_excel_financial_data(data)
    
    # Get the first row (most recent data) for regular CSV/Excel data
    first_row = data[0]
    
    # Define intelligent field mappings with multiple patterns
    field_patterns = {
        'company_name': [
            # Company name patterns
            'company', 'company_name', 'name', 'business_name', 'business', 'entity', 'organization',
            'corp', 'corporation', 'inc', 'llc', 'ltd', 'limited', 'co', 'company_name',
            'client', 'customer', 'account', 'account_name'
        ],
        'revenue': [
            # Revenue patterns
            'revenue', 'sales', 'total_revenue', 'annual_revenue', 'gross_revenue', 'net_revenue',
            'income', 'total_income', 'gross_income', 'net_income', 'turnover', 'gross_sales',
            'net_sales', 'operating_revenue', 'business_revenue', 'company_revenue',
            'revenue_amount', 'sales_amount', 'income_amount', 'revenue_', 'sales_', 'income_'
        ],
        'ebitda': [
            # EBITDA patterns
            'ebitda', 'ebit', 'operating_income', 'operating_profit', 'operating_earnings',
            'operating_margin', 'operating_result', 'operating_performance',
            'earnings_before_interest', 'operating_ebitda', 'ebitda_', 'operating_'
        ],
        'net_income': [
            # Net income patterns
            'net_income', 'net_profit', 'net_earnings', 'net_result', 'bottom_line',
            'profit_after_tax', 'earnings_after_tax', 'net_profit_after_tax',
            'net_income_', 'net_profit_', 'net_earnings_', 'profit_', 'earnings_'
        ],
        'total_assets': [
            # Total assets patterns
            'total_assets', 'assets', 'total_asset', 'total_asset_value', 'asset_value',
            'total_asset_base', 'asset_base', 'total_asset_amount', 'asset_amount',
            'total_asset_', 'asset_', 'assets_', 'total_'
        ],
        'inventory': [
            # Inventory patterns
            'inventory', 'stock', 'inventory_value', 'stock_value', 'inventory_amount',
            'stock_amount', 'inventory_balance', 'stock_balance', 'inventory_level',
            'inventory_', 'stock_', 'inventory_value_', 'stock_value_'
        ],
        'accounts_receivable': [
            # Accounts receivable patterns
            'accounts_receivable', 'receivables', 'ar', 'accounts_receivable_amount',
            'receivable_amount', 'ar_amount', 'accounts_receivable_balance',
            'receivable_balance', 'ar_balance', 'accounts_receivable_', 'receivable_'
        ],
        'cash': [
            # Cash patterns
            'cash', 'cash_and_equivalents', 'cash_balance', 'cash_amount', 'cash_value',
            'cash_position', 'cash_holdings', 'cash_reserves', 'cash_', 'cash_balance_',
            'cash_amount_', 'cash_value_'
        ],
        'total_liabilities': [
            # Total liabilities patterns
            'total_liabilities', 'liabilities', 'total_liability', 'liability',
            'total_debt', 'debt', 'total_obligations', 'obligations', 'total_liability_',
            'liability_', 'debt_', 'obligations_'
        ],
        'employees': [
            # Employee patterns
            'employees', 'employee_count', 'staff', 'fte', 'full_time_employees',
            'headcount', 'workforce', 'personnel', 'staff_count', 'employee_number',
            'employees_', 'employee_', 'staff_', 'headcount_'
        ],
        'industry': [
            # Industry patterns
            'industry', 'sector', 'business_type', 'business_sector', 'industry_type',
            'sector_type', 'business_category', 'industry_category', 'business_classification',
            'industry_', 'sector_', 'business_', 'category_'
        ]
    }
    
    mapped_data = {}
    
    # Process each column in the data
    for column_name, column_value in first_row.items():
        column_lower = column_name.lower().strip()
        
        # Try to find the best match for this column
        best_match = None
        best_score = 0
        
        for form_field, patterns in field_patterns.items():
            for pattern in patterns:
                # Calculate similarity score
                score = calculate_similarity(column_lower, pattern.lower())
                if score > best_score and score > 0.7:  # 70% similarity threshold
                    best_score = score
                    best_match = form_field
        
        if best_match:
            # Process the value based on the field type
            processed_value = process_field_value(best_match, column_value)
            mapped_data[best_match] = processed_value
            print(f"🔗 Mapped '{column_name}' → '{best_match}' (score: {best_score:.2f})")
    
    print(f"🎯 Final mapped data: {mapped_data}")
    return mapped_data

def calculate_similarity(str1, str2):
    """Calculate similarity between two strings using multiple methods"""
    if str1 == str2:
        return 1.0
    
    # Check for exact substring matches
    if str1 in str2 or str2 in str1:
        return 0.9
    
    # Check for word-based matches
    words1 = set(str1.split('_'))
    words2 = set(str2.split('_'))
    
    if words1 and words2:
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        if union:
            jaccard_similarity = len(intersection) / len(union)
            if jaccard_similarity > 0.5:
                return 0.8
    
    # Check for common abbreviations
    common_abbrevs = {
        'revenue': ['rev', 'sales', 'income'],
        'ebitda': ['ebit', 'operating'],
        'assets': ['asset'],
        'liabilities': ['liab', 'debt'],
        'receivable': ['ar', 'receivable'],
        'employees': ['emp', 'staff', 'fte']
    }
    
    for full_word, abbrevs in common_abbrevs.items():
        if str1 in abbrevs and str2 == full_word:
            return 0.85
        if str2 in abbrevs and str1 == full_word:
            return 0.85
    
    return 0.0

def process_field_value(field_name, value):
    """Process and clean field values based on field type"""
    if value is None:
        return None
    
    # Convert to string for processing
    if not isinstance(value, str):
        value = str(value)
    
    # Clean the value
    cleaned_value = value.strip()
    
    # Handle numeric fields
    numeric_fields = ['revenue', 'ebitda', 'net_income', 'total_assets', 'inventory', 
                     'accounts_receivable', 'cash', 'total_liabilities', 'employees']
    
    if field_name in numeric_fields:
        try:
            # Remove common formatting characters
            cleaned_value = cleaned_value.replace(',', '').replace('$', '').replace(' ', '')
            cleaned_value = cleaned_value.replace('(', '').replace(')', '').replace('-', '')
            
            # Handle negative numbers in parentheses
            if '(' in value and ')' in value:
                cleaned_value = '-' + cleaned_value.replace('(', '').replace(')', '')
            
            # Convert to float/int
            if '.' in cleaned_value:
                return float(cleaned_value)
            else:
                return int(cleaned_value)
        except (ValueError, TypeError):
            # If conversion fails, return original value
            return value
    
    # For non-numeric fields, return as-is
    return value

def extract_data_from_pdf(file_path):
    """Extract data from PDF files (basic implementation)"""
    try:
        # For now, return basic PDF info
        # In a real implementation, you'd use PyPDF2 or similar
        extracted_data = {
            'file_type': 'pdf',
            'message': 'PDF file uploaded successfully. Text extraction requires additional processing.',
            'filename': os.path.basename(file_path)
        }
        
        return extracted_data
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

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
    
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Check if already blocked
        cursor.execute('''
            SELECT blocked_until FROM rate_limits 
            WHERE ip_address = ? AND endpoint = ? AND blocked_until > datetime('now')
        ''', (ip_address, endpoint))
        
        existing_block = cursor.fetchone()
        if existing_block:
            blocked_until = datetime.fromisoformat(existing_block['blocked_until'])
            return False, f"Rate limit exceeded. Try again after {blocked_until.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Get or create rate limit record
        cursor.execute('''
            SELECT * FROM rate_limits 
            WHERE ip_address = ? AND endpoint = ?
        ''', (ip_address, endpoint))
        
        rate_limit = cursor.fetchone()
        
        if not rate_limit:
            # Create new rate limit record
            cursor.execute('''
                INSERT INTO rate_limits (ip_address, device_id, endpoint, attempt_count, first_attempt, last_attempt)
                VALUES (?, ?, ?, 1, datetime('now'), datetime('now'))
            ''', (ip_address, device_id, endpoint))
        else:
            # Check if within time window (24 hours)
            first_attempt = datetime.fromisoformat(rate_limit['first_attempt'])
            time_diff = datetime.now() - first_attempt
            
            if time_diff > timedelta(hours=24):
                # Reset counter after 24 hours
                cursor.execute('''
                    UPDATE rate_limits 
                    SET attempt_count = 1, first_attempt = datetime('now'), last_attempt = datetime('now')
                    WHERE ip_address = ? AND endpoint = ?
                ''', (ip_address, endpoint))
            else:
                # Increment counter
                new_count = rate_limit['attempt_count'] + 1
                cursor.execute('''
                    UPDATE rate_limits 
                    SET attempt_count = ?, last_attempt = datetime('now')
                    WHERE ip_address = ? AND endpoint = ?
                ''', (new_count, ip_address, endpoint))
                
                # Block if max attempts exceeded
                if new_count > max_attempts:
                    blocked_until = datetime.now() + timedelta(seconds=block_duration)
                    cursor.execute('''
                        UPDATE rate_limits 
                        SET blocked_until = ? 
                        WHERE ip_address = ? AND endpoint = ?
                    ''', (blocked_until.isoformat(), ip_address, endpoint))
                    conn.commit()
                    return False, f"Rate limit exceeded. Please sign up to continue. Try again after {blocked_until.strftime('%Y-%m-%d %H:%M:%S')}"
        
        conn.commit()
        
        # Get current attempt count
        cursor.execute('''
            SELECT attempt_count FROM rate_limits 
            WHERE ip_address = ? AND endpoint = ?
        ''', (ip_address, endpoint))
        
        result = cursor.fetchone()
        if result:
            current_count = result['attempt_count']
            return True, f"Attempt {current_count}/{max_attempts}"
        else:
            return True, "Attempt 1/2"
        
    except sqlite3.Error as e:
        print(f"Rate limit check error: {e}")
        return False, f"Rate limit check failed: {str(e)}"
    finally:
        conn.close()

def log_user_activity(user_id, action, success=True):
    """Log user activity for audit purposes"""
    ip_address, device_id = get_client_info()
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_activities (user_id, ip_address, device_id, action, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, ip_address, device_id, action, success))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Activity logging error: {e}")
    finally:
        conn.close()

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
            'database': f'SQLite ({db_status})'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': 'Health check failed'
        }), 500

@app.route('/api/auth/test', methods=['GET'])
def auth_test():
    """Test endpoint to verify authentication system is working"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'status': 'error',
            'message': 'Database connection failed'
        }), 503
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        
        return jsonify({
            'status': 'success',
            'message': 'Authentication system is working',
            'database_connected': True,
            'user_count': user_count,
            'timestamp': datetime.now().isoformat()
        })
    except sqlite3.Error as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500
    finally:
        conn.close()

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
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 503
        
        try:
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return jsonify({'error': 'Email already registered'}), 409
            
            # Create new user
            verification_token = generate_verification_token()
            cursor.execute('''
                INSERT INTO users (email, password_hash, mobile, verification_token)
                VALUES (?, ?, ?, ?)
            ''', (email, hash_password(password), mobile, verification_token))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            print(f"User created successfully: {email} (ID: {user_id})")
            
            # Log activity
            log_user_activity(user_id, 'signup', True)
            
            return jsonify({
                'status': 'success',
                'message': 'Account created successfully. Please check your email for verification.',
                'email_sent': True,
                'email_message': 'Verification email sent (mock)',
                'user_id': user_id
            }), 201
            
        finally:
            conn.close()
        
    except sqlite3.IntegrityError as e:
        print(f"Signup integrity error: {str(e)}")
        return jsonify({'error': 'Email already registered'}), 409
    except sqlite3.Error as e:
        print(f"Signup database error: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
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
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 503
        
        try:
            cursor = conn.cursor()
            
            # Find user
            cursor.execute('''
                SELECT id, email, password_hash, mobile, email_verified, created_at, last_login
                FROM users WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            if hash_password(password) != user['password_hash']:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Email verification is now optional for login
            # Users can login even without verifying their email
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = datetime('now') WHERE id = ?
            ''', (user['id'],))
            
            conn.commit()
            
            print(f"User logged in successfully: {email}")
            
            # Log activity
            log_user_activity(user['id'], 'login', True)
            
            # Create user session
            session_token = create_user_session(user['id'], email)
            if not session_token:
                return jsonify({'error': 'Failed to create session'}), 500
            
            # Add a note about email verification status
            message = 'Login successful'
            if not user['email_verified']:
                message = 'Login successful. Note: Your email is not yet verified. You can still use the platform.'
            
            return jsonify({
                'status': 'success',
                'message': message,
                'session_token': session_token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'mobile': user['mobile'],
                    'email_verified': user['email_verified'],
                    'created_at': user['created_at'],
                    'last_login': user['last_login']
                }
            })
            
        finally:
            conn.close()
        
    except sqlite3.Error as e:
        print(f"Login database error: {str(e)}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/verify/<token>', methods=['GET'])
def verify_email(token):
    """Email verification endpoint"""
    try:
        print(f"Verification request for token: {token}")
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 503
        
        try:
            cursor = conn.cursor()
            
            # Find user with this token
            cursor.execute('''
                SELECT id, email, email_verified FROM users WHERE verification_token = ?
            ''', (token,))
            
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Invalid verification token'}), 400
            
            if user['email_verified']:
                return jsonify({'error': 'Email already verified'}), 400
            
            # Verify email
            cursor.execute('''
                UPDATE users 
                SET email_verified = 1, verification_token = NULL 
                WHERE id = ?
            ''', (user['id'],))
            
            conn.commit()
            
            print(f"Email verified successfully: {user['email']}")
            
            # Log activity
            log_user_activity(user['id'], 'email_verification', True)
            
            return jsonify({
                'status': 'success',
                'message': 'Email verified successfully! You can now log in.'
            })
            
        finally:
            conn.close()
        
    except sqlite3.Error as e:
        print(f"Email verification database error: {str(e)}")
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500
    except Exception as e:
        print(f"Email verification error: {str(e)}")
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        print("Logout request received")
        
        # Get session token from request
        data = request.get_json()
        session_token = data.get('session_token') if data else None
        
        if session_token:
            # Delete the session
            delete_user_session(session_token)
            print(f"Session deleted for token: {session_token}")
        
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        })
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile from session token"""
    try:
        print("Profile request received")
        
        # Get session token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid session token provided'}), 401
        
        session_token = auth_header.split(' ')[1]
        user_data = validate_session(session_token)
        
        if not user_data:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        return jsonify({
            'status': 'success',
            'user': user_data
        })
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({'error': f'Profile failed: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint"""
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
        
        # Secure filename and save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        file.save(file_path)
        print(f"File saved: {file_path}")
        
        # Extract data based on file type
        file_extension = filename.rsplit('.', 1)[1].lower()
        print(f"Processing file with extension: {file_extension}")
        
        extracted_data = None
        
        if file_extension in ['xlsx', 'xls']:
            print("Attempting Excel data extraction...")
            extracted_data = extract_data_from_excel(file_path)
            print(f"Excel extraction result: {extracted_data is not None}")
        elif file_extension == 'csv':
            print("Attempting CSV data extraction...")
            extracted_data = extract_data_from_csv(file_path)
            print(f"CSV extraction result: {extracted_data is not None}")
        elif file_extension == 'pdf':
            print("Attempting PDF data extraction...")
            extracted_data = extract_data_from_pdf(file_path)
            print(f"PDF extraction result: {extracted_data is not None}")
        
        if extracted_data:
            # Add file metadata
            extracted_data['filename'] = filename
            extracted_data['file_size'] = os.path.getsize(file_path)
            extracted_data['uploaded_at'] = datetime.now().isoformat()
            
            print(f"Data extraction successful. Data keys: {list(extracted_data.keys())}")
            
            return jsonify({
                'status': 'success',
                'message': 'File uploaded and processed successfully',
                'extracted_data': extracted_data
            })
        else:
            print("Data extraction failed, returning fallback response")
            return jsonify({
                'status': 'success',
                'message': 'File uploaded but data extraction failed',
                'extracted_data': {
                    'filename': filename,
                    'file_size': os.path.getsize(file_path),
                    'uploaded_at': datetime.now().isoformat(),
                    'message': 'File uploaded successfully but data extraction failed'
                }
            })
            
    except Exception as e:
        print(f"File upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/auth/rate-limit-status', methods=['GET'])
def get_rate_limit_status_endpoint():
    """Get current rate limit status for user"""
    try:
        print("Rate limit status request received")
        ip_address, device_id = get_client_info()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 503
        
        try:
            cursor = conn.cursor()
            
            # Get rate limit status for upload
            cursor.execute('''
                SELECT attempt_count, blocked_until FROM rate_limits 
                WHERE ip_address = ? AND endpoint = 'upload'
            ''', (ip_address,))
            
            upload_limit = cursor.fetchone()
            
            # Get rate limit status for report generation
            cursor.execute('''
                SELECT attempt_count, blocked_until FROM rate_limits 
                WHERE ip_address = ? AND endpoint = 'report_generation'
            ''', (ip_address,))
            
            report_limit = cursor.fetchone()
            
            return jsonify({
                'status': 'success',
                'upload': {
                    'attempts': upload_limit['attempt_count'] if upload_limit else 0,
                    'max_attempts': 2,
                    'blocked': upload_limit and upload_limit['blocked_until'] and datetime.fromisoformat(upload_limit['blocked_until']) > datetime.now(),
                    'blocked_until': upload_limit['blocked_until'] if upload_limit else None
                },
                'report_generation': {
                    'attempts': report_limit['attempt_count'] if report_limit else 0,
                    'max_attempts': 2,
                    'blocked': report_limit and report_limit['blocked_until'] and datetime.fromisoformat(report_limit['blocked_until']) > datetime.now(),
                    'blocked_until': report_limit['blocked_until'] if report_limit else None
                }
            })
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Rate limit status error: {str(e)}")
        return jsonify({'error': f'Failed to get rate limit status: {str(e)}'}), 500

@app.route('/api/valuation', methods=['POST'])
def calculate_valuation():
    """Calculate business valuation"""
    try:
        print("Valuation calculation request received")
        data = request.get_json()
        
        # Mock valuation calculation
        # In a real implementation, this would use actual financial models
        company_name = data.get('company_name', 'Unknown Company')
        
        # Simple mock calculation based on revenue and EBITDA
        revenue = float(data.get('revenue', 0))
        ebitda = float(data.get('ebitda', 0))
        
        if revenue > 0 and ebitda > 0:
            # Simple multiple-based valuation
            ebitda_multiple = 5.0  # Industry average
            asset_value = float(data.get('total_assets', 0)) * 0.8  # 80% of book value
            
            valuation = max(ebitda * ebitda_multiple, asset_value)
            
            return jsonify({
                'status': 'success',
                'valuation_results': {
                    'company_name': company_name,
                    'calculated_value': round(valuation, 2),
                    'method': 'EBITDA Multiple + Asset Value',
                    'ebitda_multiple': ebitda_multiple,
                    'asset_value': round(asset_value, 2),
                    'calculated_at': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                'status': 'success',
                'valuation_results': {
                    'company_name': company_name,
                    'message': 'Insufficient financial data for valuation calculation',
                    'calculated_at': datetime.now().isoformat()
                }
            })
            
    except Exception as e:
        print(f"Valuation calculation error: {str(e)}")
        return jsonify({'error': f'Valuation failed: {str(e)}'}), 500

@app.route('/api/swot', methods=['POST'])
def generate_swot():
    """Generate intelligent SWOT analysis based on company data and extracted file data"""
    try:
        print("SWOT analysis request received")
        data = request.get_json()
        print(f"📊 SWOT Analysis - Received data keys: {list(data.keys()) if data else 'None'}")
        print(f"📊 SWOT Analysis - extracted_data: {data.get('extracted_data') if data else 'None'}")
        
        # Get basic company info
        company_name = data.get('company_name', 'Unknown Company')
        industry = data.get('industry', 'General')
        
        # Get extracted file data if available (prioritize this over form data)
        extracted_data = data.get('extracted_data', {})
        if extracted_data is None:
            extracted_data = {}
        mapped_fields = extracted_data.get('mapped_fields', {}) if extracted_data else {}
        
        # Use extracted data if available, otherwise fall back to form data
        revenue = mapped_fields.get('revenue') or data.get('revenue', 0)
        ebitda = mapped_fields.get('ebitda') or data.get('ebitda', 0)
        net_income = mapped_fields.get('net_income') or data.get('net_income', 0)
        total_assets = mapped_fields.get('total_assets') or data.get('total_assets', 0)
        total_liabilities = mapped_fields.get('total_liabilities') or data.get('total_liabilities', 0)
        employees = mapped_fields.get('employees') or data.get('employees', 0)
        cash = mapped_fields.get('cash') or data.get('cash', 0)
        inventory = mapped_fields.get('inventory') or data.get('inventory', 0)
        accounts_receivable = mapped_fields.get('accounts_receivable') or data.get('accounts_receivable', 0)
        
        # Additional financial metrics from extracted data
        cost_of_goods_sold = mapped_fields.get('cost_of_goods_sold', 0)
        gross_profit = mapped_fields.get('gross_profit', 0)
        operating_expenses = mapped_fields.get('operating_expenses', 0)
        equipment = mapped_fields.get('equipment', 0)
        fitout = mapped_fields.get('fitout', 0)
        
        print(f"📊 SWOT Analysis - Using extracted data: Revenue=${revenue}, Net Income=${net_income}, Assets=${total_assets}")
        
        # Convert to numeric values for analysis
        revenue = float(revenue) if revenue else 0
        ebitda = float(ebitda) if ebitda else 0
        net_income = float(net_income) if net_income else 0
        total_assets = float(total_assets) if total_assets else 0
        total_liabilities = float(total_liabilities) if total_liabilities else 0
        employees = int(employees) if employees else 0
        cash = float(cash) if cash else 0
        inventory = float(inventory) if inventory else 0
        accounts_receivable = float(accounts_receivable) if accounts_receivable else 0
        cost_of_goods_sold = float(cost_of_goods_sold) if cost_of_goods_sold else 0
        gross_profit = float(gross_profit) if gross_profit else 0
        operating_expenses = float(operating_expenses) if operating_expenses else 0
        equipment = float(equipment) if equipment else 0
        fitout = float(fitout) if fitout else 0
        
        # Calculate comprehensive financial ratios for analysis
        ebitda_margin = (ebitda / revenue * 100) if revenue > 0 else 0
        net_margin = (net_income / revenue * 100) if revenue > 0 else 0
        gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
        operating_margin = ((revenue - cost_of_goods_sold - operating_expenses) / revenue * 100) if revenue > 0 else 0
        debt_to_assets = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
        debt_to_equity = (total_liabilities / (total_assets - total_liabilities) * 100) if (total_assets - total_liabilities) > 0 else 0
        revenue_per_employee = (revenue / employees) if employees > 0 else 0
        current_ratio = ((cash + accounts_receivable) / total_liabilities) if total_liabilities > 0 else 0
        quick_ratio = ((cash + accounts_receivable) / total_liabilities) if total_liabilities > 0 else 0
        inventory_turnover = (cost_of_goods_sold / inventory) if inventory > 0 else 0
        asset_turnover = (revenue / total_assets) if total_assets > 0 else 0
        roa = (net_income / total_assets * 100) if total_assets > 0 else 0
        roe = (net_income / (total_assets - total_liabilities) * 100) if (total_assets - total_liabilities) > 0 else 0
        
        # Generate intelligent SWOT analysis
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # STRENGTHS Analysis - Enhanced with comprehensive ratios
        if ebitda_margin > 15:
            strengths.append(f"Strong EBITDA margin of {ebitda_margin:.1f}% indicates efficient operations")
        elif ebitda_margin > 10:
            strengths.append(f"Healthy EBITDA margin of {ebitda_margin:.1f}% shows good operational efficiency")
        
        if net_margin > 10:
            strengths.append(f"Excellent net profit margin of {net_margin:.1f}% demonstrates strong profitability")
        elif net_margin > 5:
            strengths.append(f"Good net profit margin of {net_margin:.1f}% shows solid financial performance")
        
        if gross_margin > 40:
            strengths.append(f"Strong gross margin of {gross_margin:.1f}% indicates effective cost management")
        elif gross_margin > 30:
            strengths.append(f"Healthy gross margin of {gross_margin:.1f}% shows good pricing power")
        
        if operating_margin > 15:
            strengths.append(f"Excellent operating margin of {operating_margin:.1f}% demonstrates operational efficiency")
        elif operating_margin > 10:
            strengths.append(f"Good operating margin of {operating_margin:.1f}% shows strong operational control")
        
        if debt_to_assets < 30:
            strengths.append(f"Low debt-to-assets ratio of {debt_to_assets:.1f}% indicates strong financial stability")
        elif debt_to_assets < 50:
            strengths.append(f"Moderate debt-to-assets ratio of {debt_to_assets:.1f}% shows manageable leverage")
        
        if debt_to_equity < 50:
            strengths.append(f"Conservative debt-to-equity ratio of {debt_to_equity:.1f}% shows strong equity position")
        
        if revenue_per_employee > 200000:
            strengths.append(f"High revenue per employee of ${revenue_per_employee:,.0f} indicates efficient workforce")
        elif revenue_per_employee > 100000:
            strengths.append(f"Good revenue per employee of ${revenue_per_employee:,.0f} shows productive operations")
        
        if current_ratio > 2:
            strengths.append(f"Strong liquidity position with current ratio of {current_ratio:.1f}")
        elif current_ratio > 1.5:
            strengths.append(f"Good liquidity position with current ratio of {current_ratio:.1f}")
        
        if roa > 10:
            strengths.append(f"Strong return on assets of {roa:.1f}% indicates efficient asset utilization")
        elif roa > 5:
            strengths.append(f"Good return on assets of {roa:.1f}% shows effective asset management")
        
        if roe > 15:
            strengths.append(f"Excellent return on equity of {roe:.1f}% demonstrates strong shareholder value creation")
        elif roe > 10:
            strengths.append(f"Good return on equity of {roe:.1f}% shows solid profitability")
        
        if asset_turnover > 1.5:
            strengths.append(f"High asset turnover of {asset_turnover:.1f}x indicates efficient asset utilization")
        elif asset_turnover > 1.0:
            strengths.append(f"Good asset turnover of {asset_turnover:.1f}x shows effective asset management")
        
        if inventory_turnover > 6:
            strengths.append(f"High inventory turnover of {inventory_turnover:.1f}x indicates efficient inventory management")
        elif inventory_turnover > 4:
            strengths.append(f"Good inventory turnover of {inventory_turnover:.1f}x shows effective inventory control")
        
        if revenue > 10000000:
            strengths.append(f"Large revenue base of ${revenue:,.0f} provides market presence and scale")
        elif revenue > 1000000:
            strengths.append(f"Solid revenue base of ${revenue:,.0f} indicates established market position")
        
        # Asset composition strengths
        if cash > revenue * 0.1:
            strengths.append(f"Strong cash position of ${cash:,.0f} provides financial flexibility")
        if equipment > 0:
            strengths.append(f"Equipment assets of ${equipment:,.0f} provide operational infrastructure")
        
        # WEAKNESSES Analysis - Enhanced with comprehensive ratios
        if ebitda_margin < 5:
            weaknesses.append(f"Low EBITDA margin of {ebitda_margin:.1f}% suggests operational inefficiencies")
        
        if net_margin < 2:
            weaknesses.append(f"Low net profit margin of {net_margin:.1f}% indicates profitability challenges")
        
        if gross_margin < 20:
            weaknesses.append(f"Low gross margin of {gross_margin:.1f}% suggests pricing or cost control issues")
        
        if operating_margin < 5:
            weaknesses.append(f"Low operating margin of {operating_margin:.1f}% indicates operational inefficiencies")
        
        if debt_to_assets > 70:
            weaknesses.append(f"High debt-to-assets ratio of {debt_to_assets:.1f}% creates financial risk")
        elif debt_to_assets > 50:
            weaknesses.append(f"Elevated debt-to-assets ratio of {debt_to_assets:.1f}% increases financial pressure")
        
        if debt_to_equity > 100:
            weaknesses.append(f"High debt-to-equity ratio of {debt_to_equity:.1f}% indicates excessive leverage")
        
        if revenue_per_employee < 50000:
            weaknesses.append(f"Low revenue per employee of ${revenue_per_employee:,.0f} suggests operational inefficiency")
        
        if current_ratio < 1:
            weaknesses.append(f"Low current ratio of {current_ratio:.1f} indicates potential liquidity issues")
        
        if roa < 3:
            weaknesses.append(f"Low return on assets of {roa:.1f}% suggests inefficient asset utilization")
        
        if roe < 5:
            weaknesses.append(f"Low return on equity of {roe:.1f}% indicates poor profitability for shareholders")
        
        if asset_turnover < 0.5:
            weaknesses.append(f"Low asset turnover of {asset_turnover:.1f}x suggests underutilized assets")
        
        if inventory_turnover < 2:
            weaknesses.append(f"Low inventory turnover of {inventory_turnover:.1f}x indicates slow-moving inventory")
        
        if revenue < 100000:
            weaknesses.append(f"Small revenue base of ${revenue:,.0f} limits market presence and growth potential")
        
        # Asset composition weaknesses
        if accounts_receivable > revenue * 0.5:
            weaknesses.append(f"High accounts receivable of ${accounts_receivable:,.0f} indicates collection issues")
        
        if inventory > revenue * 0.3:
            weaknesses.append(f"High inventory levels of ${inventory:,.0f} suggest overstocking or slow sales")
        
        # OPPORTUNITIES Analysis
        if ebitda_margin > 10 and revenue < 5000000:
            opportunities.append("Strong operational efficiency provides foundation for revenue growth")
        
        if net_margin > 5 and debt_to_assets < 40:
            opportunities.append("Healthy profitability and low debt enable expansion opportunities")
        
        if revenue_per_employee > 150000:
            opportunities.append("High productivity per employee supports scaling operations")
        
        if current_ratio > 1.5 and cash > revenue * 0.1:
            opportunities.append("Strong cash position enables strategic investments and acquisitions")
        
        if industry.lower() in ['technology', 'software', 'saas']:
            opportunities.append("Technology sector offers digital transformation and innovation opportunities")
        elif industry.lower() in ['healthcare', 'medical']:
            opportunities.append("Healthcare sector provides growth opportunities from demographic trends")
        elif industry.lower() in ['manufacturing', 'industrial']:
            opportunities.append("Manufacturing sector offers automation and efficiency improvement opportunities")
        
        if employees > 50:
            opportunities.append("Larger workforce enables market expansion and service diversification")
        
        # THREATS Analysis
        if debt_to_assets > 60:
            threats.append("High debt levels increase vulnerability to interest rate changes")
        
        if current_ratio < 1.2:
            threats.append("Low liquidity position creates risk during economic downturns")
        
        if ebitda_margin < 8:
            threats.append("Low operational margins make company vulnerable to cost increases")
        
        if revenue < 500000:
            threats.append("Small size limits ability to compete with larger players")
        
        if industry.lower() in ['retail', 'hospitality']:
            threats.append("Consumer-facing industries face economic sensitivity and competition")
        elif industry.lower() in ['energy', 'utilities']:
            threats.append("Regulated industries face policy and regulatory risks")
        
        if employees < 10:
            threats.append("Small team size creates key person dependency risks")
        
        # Add industry-specific insights
        industry_insights = get_industry_insights(industry, revenue, ebitda_margin)
        strengths.extend(industry_insights.get('strengths', []))
        weaknesses.extend(industry_insights.get('weaknesses', []))
        opportunities.extend(industry_insights.get('opportunities', []))
        threats.extend(industry_insights.get('threats', []))
        
        # Ensure we have at least some analysis
        if not strengths:
            strengths.append("Company shows potential for growth and development")
        if not weaknesses:
            weaknesses.append("Limited data available for comprehensive weakness analysis")
        if not opportunities:
            opportunities.append("Market conditions may present growth opportunities")
        if not threats:
            threats.append("General market and economic risks apply to all businesses")
        
        swot_analysis = {
            'company_name': company_name,
            'industry': industry,
            'generated_at': datetime.now().isoformat(),
            'financial_metrics': {
                'revenue': revenue,
                'ebitda_margin': ebitda_margin,
                'net_margin': net_margin,
                'gross_margin': gross_margin,
                'operating_margin': operating_margin,
                'debt_to_assets': debt_to_assets,
                'debt_to_equity': debt_to_equity,
                'revenue_per_employee': revenue_per_employee,
                'current_ratio': current_ratio,
                'quick_ratio': quick_ratio,
                'inventory_turnover': inventory_turnover,
                'asset_turnover': asset_turnover,
                'roa': roa,
                'roe': roe,
                'cash': cash,
                'inventory': inventory,
                'accounts_receivable': accounts_receivable,
                'total_assets': total_assets,
                'total_liabilities': total_liabilities
            },
            'strengths': strengths[:8],  # Limit to top 8
            'weaknesses': weaknesses[:8],
            'opportunities': opportunities[:8],
            'threats': threats[:8]
        }
        
        return jsonify({
            'status': 'success',
            'swot_analysis': swot_analysis
        })
        
    except Exception as e:
        print(f"SWOT analysis error: {str(e)}")
        return jsonify({'error': f'SWOT analysis failed: {str(e)}'}), 500

def get_industry_insights(industry, revenue, ebitda_margin):
    """Generate industry-specific SWOT insights"""
    industry_lower = industry.lower()
    insights = {'strengths': [], 'weaknesses': [], 'opportunities': [], 'threats': []}
    
    if 'technology' in industry_lower or 'software' in industry_lower:
        insights['strengths'].append("Technology sector benefits from digital transformation trends")
        insights['opportunities'].append("AI and automation present significant growth opportunities")
        insights['threats'].append("Rapid technological change requires continuous innovation")
        
    elif 'healthcare' in industry_lower or 'medical' in industry_lower:
        insights['strengths'].append("Healthcare sector provides essential services with stable demand")
        insights['opportunities'].append("Aging population creates long-term growth opportunities")
        insights['threats'].append("Regulatory compliance costs and complexity")
        
    elif 'manufacturing' in industry_lower or 'industrial' in industry_lower:
        insights['strengths'].append("Manufacturing provides tangible value and supply chain importance")
        insights['opportunities'].append("Automation and Industry 4.0 transformation opportunities")
        insights['threats'].append("Supply chain disruptions and raw material cost volatility")
        
    elif 'retail' in industry_lower or 'consumer' in industry_lower:
        insights['strengths'].append("Direct customer relationships and brand building potential")
        insights['opportunities'].append("E-commerce and omnichannel retail expansion")
        insights['threats'].append("Intense competition and changing consumer preferences")
        
    elif 'financial' in industry_lower or 'banking' in industry_lower:
        insights['strengths'].append("Financial services provide essential economic functions")
        insights['opportunities'].append("Fintech innovation and digital banking opportunities")
        insights['threats'].append("Regulatory oversight and interest rate sensitivity")
    
    return insights

@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Generate business valuation report"""
    try:
        print("Report generation request received")
        data = request.get_json()
        print(f"📄 Report generation data: {data}")
        
        company_name = data.get('company_name', 'Unknown Company')
        format_type = data.get('format', 'pdf')
        
        # Generate filename - always use .txt extension
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"{company_name.replace(' ', '_')}_Valuation_Report_{timestamp}.txt"
        
        # Mock report generation
        report_data = {
            'report_id': f"RPT_{timestamp}",
            'company_name': company_name,
            'generated_at': datetime.now().isoformat(),
            'status': 'completed',
            'message': 'Report generated successfully',
            'format': format_type
        }
        
        print(f"📄 Generated report filename: {report_filename}")
        
        return jsonify({
            'status': 'success',
            'report_filename': report_filename,
            'download_url': f'/api/report/download/{report_filename}',
            'report': report_data
        })
        
    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

def generate_comprehensive_report(filename):
    """Generate a comprehensive section-wise business valuation report"""
    
    # Get current timestamp
    generated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Extract company name from filename
    company_name = filename.split('_Valuation_Report_')[0].replace('_', ' ')
    
    # Sample data (in a real app, this would come from the database)
    sample_data = {
        'company_name': company_name,
        'industry': 'Technology',
        'revenue': 52000,
        'ebitda': 1000,
        'net_income': 5200,
        'total_assets': 41340,
        'total_liabilities': 11000,
        'employees': 16,
        'calculated_value': 33072,
        'asset_value': 33072,
        'ebitda_multiple': 5.0,
        'method': 'EBITDA Multiple + Asset Value'
    }
    
    report = f"""
{'='*80}
BUSINESS VALUATION REPORT
{'='*80}

Report: {filename}
Generated: {generated_time}
Company: {sample_data['company_name']}
Industry: {sample_data['industry']}

{'='*80}
TABLE OF CONTENTS
{'='*80}

1. EXECUTIVE SUMMARY
2. COMPANY OVERVIEW
3. FINANCIAL ANALYSIS
4. VALUATION METHODOLOGY
5. VALUATION RESULTS
6. SWOT ANALYSIS
7. MARKET POSITIONING
8. RISK ASSESSMENT
9. RECOMMENDATIONS
10. APPENDICES

{'='*80}
1. EXECUTIVE SUMMARY
{'='*80}

This report presents a comprehensive business valuation analysis for {sample_data['company_name']}, 
a {sample_data['industry']} company. The valuation was conducted using multiple methodologies 
to ensure accuracy and reliability.

KEY FINDINGS:
• Fair Market Value: ${sample_data['calculated_value']:,}
• Primary Valuation Method: {sample_data['method']}
• Industry: {sample_data['industry']}
• Annual Revenue: ${sample_data['revenue']:,}
• EBITDA: ${sample_data['ebitda']:,}
• Net Income: ${sample_data['net_income']:,}

The company demonstrates solid financial performance with a net profit margin of 
{(sample_data['net_income']/sample_data['revenue']*100):.1f}% and strong asset base of 
${sample_data['total_assets']:,}.

{'='*80}
2. COMPANY OVERVIEW
{'='*80}

COMPANY PROFILE:
• Company Name: {sample_data['company_name']}
• Industry: {sample_data['industry']}
• Number of Employees: {sample_data['employees']}
• Business Model: Technology Services

FINANCIAL HIGHLIGHTS:
• Annual Revenue: ${sample_data['revenue']:,}
• EBITDA: ${sample_data['ebitda']:,}
• Net Income: ${sample_data['net_income']:,}
• Total Assets: ${sample_data['total_assets']:,}
• Total Liabilities: ${sample_data['total_liabilities']:,}
• Shareholders' Equity: ${sample_data['total_assets'] - sample_data['total_liabilities']:,}

{'='*80}
3. FINANCIAL ANALYSIS
{'='*80}

PROFITABILITY METRICS:
• Gross Profit Margin: {(sample_data['revenue'] - sample_data['revenue']*0.6)/sample_data['revenue']*100:.1f}%
• EBITDA Margin: {sample_data['ebitda']/sample_data['revenue']*100:.1f}%
• Net Profit Margin: {sample_data['net_income']/sample_data['revenue']*100:.1f}%

LIQUIDITY RATIOS:
• Current Ratio: {sample_data['total_assets']/sample_data['total_liabilities']:.2f}x
• Quick Ratio: {(sample_data['total_assets'] - sample_data['total_assets']*0.1)/sample_data['total_liabilities']:.2f}x

LEVERAGE RATIOS:
• Debt-to-Equity: {sample_data['total_liabilities']/(sample_data['total_assets'] - sample_data['total_liabilities']):.2f}x
• Debt-to-Assets: {sample_data['total_liabilities']/sample_data['total_assets']*100:.1f}%

EFFICIENCY RATIOS:
• Asset Turnover: {sample_data['revenue']/sample_data['total_assets']:.2f}x
• Return on Assets (ROA): {sample_data['net_income']/sample_data['total_assets']*100:.1f}%
• Return on Equity (ROE): {sample_data['net_income']/(sample_data['total_assets'] - sample_data['total_liabilities'])*100:.1f}%

{'='*80}
4. VALUATION METHODOLOGY
{'='*80}

The valuation was conducted using the following methodologies:

1. EBITDA MULTIPLE APPROACH:
   • EBITDA: ${sample_data['ebitda']:,}
   • Industry Multiple: {sample_data['ebitda_multiple']}x
   • EBITDA Value: ${sample_data['ebitda'] * sample_data['ebitda_multiple']:,}

2. ASSET-BASED APPROACH:
   • Total Assets: ${sample_data['total_assets']:,}
   • Total Liabilities: ${sample_data['total_liabilities']:,}
   • Net Asset Value: ${sample_data['total_assets'] - sample_data['total_liabilities']:,}

3. INCOME APPROACH:
   • Net Income: ${sample_data['net_income']:,}
   • Capitalization Rate: 15%
   • Income Value: ${sample_data['net_income']/0.15:,.0f}

{'='*80}
5. VALUATION RESULTS
{'='*80}

FINAL VALUATION:
• Calculated Value: ${sample_data['calculated_value']:,}
• Valuation Method: {sample_data['method']}
• Confidence Level: High

VALUATION BREAKDOWN:
• EBITDA Component: ${sample_data['ebitda'] * sample_data['ebitda_multiple']:,}
• Asset Component: ${sample_data['asset_value']:,}
• Weighted Average: ${sample_data['calculated_value']:,}

VALUATION RANGE:
• Conservative Estimate: ${sample_data['calculated_value'] * 0.8:,.0f}
• Most Likely Value: ${sample_data['calculated_value']:,}
• Optimistic Estimate: ${sample_data['calculated_value'] * 1.2:,.0f}

{'='*80}
6. SWOT ANALYSIS
{'='*80}

STRENGTHS:
• Strong financial performance with {sample_data['net_income']/sample_data['revenue']*100:.1f}% net margin
• Low debt-to-equity ratio of {sample_data['total_liabilities']/(sample_data['total_assets'] - sample_data['total_liabilities']):.2f}x
• Solid asset base of ${sample_data['total_assets']:,}
• Good liquidity position
• Strong return on equity of {sample_data['net_income']/(sample_data['total_assets'] - sample_data['total_liabilities'])*100:.1f}%

WEAKNESSES:
• Small revenue base of ${sample_data['revenue']:,}
• Limited market presence
• High dependency on key personnel
• Limited diversification

OPPORTUNITIES:
• Market expansion potential
• Technology sector growth
• Digital transformation opportunities
• Strategic partnerships
• Product/service diversification

THREATS:
• Economic downturns
• Increased competition
• Regulatory changes
• Technology disruption
• Key person dependency

{'='*80}
7. MARKET POSITIONING
{'='*80}

INDUSTRY ANALYSIS:
• Industry: {sample_data['industry']}
• Market Size: Growing
• Competitive Landscape: Moderate
• Barriers to Entry: Medium

COMPETITIVE ADVANTAGES:
• Strong financial position
• Efficient operations
• Good customer relationships
• Technology expertise

MARKET OPPORTUNITIES:
• Digital transformation services
• Cloud computing solutions
• AI and automation
• Cybersecurity services

{'='*80}
8. RISK ASSESSMENT
{'='*80}

FINANCIAL RISKS:
• Revenue concentration risk
• Market volatility
• Economic sensitivity
• Credit risk

OPERATIONAL RISKS:
• Key person dependency
• Technology obsolescence
• Regulatory compliance
• Competition

MITIGATION STRATEGIES:
• Diversify revenue streams
• Implement succession planning
• Invest in technology updates
• Maintain compliance programs

{'='*80}
9. RECOMMENDATIONS
{'='*80}

STRATEGIC RECOMMENDATIONS:
1. Focus on revenue growth and market expansion
2. Diversify service offerings
3. Invest in technology and innovation
4. Develop strategic partnerships
5. Implement succession planning

FINANCIAL RECOMMENDATIONS:
1. Maintain strong cash position
2. Optimize working capital
3. Consider debt restructuring if needed
4. Invest in growth opportunities
5. Regular financial monitoring

{'='*80}
10. APPENDICES
{'='*80}

APPENDIX A: FINANCIAL STATEMENTS
• Income Statement
• Balance Sheet
• Cash Flow Statement

APPENDIX B: VALUATION CALCULATIONS
• Detailed EBITDA calculations
• Asset valuation breakdown
• Discounted cash flow analysis

APPENDIX C: MARKET RESEARCH
• Industry benchmarks
• Comparable company analysis
• Market trends and forecasts

APPENDIX D: ASSUMPTIONS AND LIMITATIONS
• Key assumptions used in valuation
• Limitations of the analysis
• Sensitivity analysis

{'='*80}
DISCLAIMER
{'='*80}

This valuation report is prepared for informational purposes only and should not be 
considered as investment advice. The valuation is based on the information available 
at the time of analysis and may not reflect current market conditions.

For questions or clarifications, please contact the valuation team.

{'='*80}
FILE FORMAT NOTE
{'='*80}

This report is generated as a text file (.txt) for maximum compatibility and to 
prevent file corruption issues. The original filename extension indicated the 
intended format for future conversion:

CONVERSION INSTRUCTIONS:
• To PDF: Copy this content → Paste into Microsoft Word/Google Docs → Export as PDF
• To Word: Copy this content → Paste into Microsoft Word → Save as .docx
• To Excel: Copy this content → Paste into Microsoft Excel → Format as needed

ALTERNATIVE METHODS:
• Use online text-to-PDF converters (e.g., SmallPDF, ILovePDF)
• Use browser "Print to PDF" function after pasting into a document
• Use Microsoft Word's "Save as PDF" feature

This approach ensures the report downloads correctly without corruption errors.

{'='*80}
END OF REPORT
{'='*80}

Generated by Business Valuation Platform
{generated_time}
    """.strip()
    
    return report

@app.route('/api/report/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated report"""
    try:
        print(f"Report download request for: {filename}")
        
        # Generate comprehensive section-wise report
        report_content = generate_comprehensive_report(filename)
        
        # Change filename to .txt to avoid corruption issues
        # This ensures the browser knows it's a text file
        safe_filename = filename.rsplit('.', 1)[0] + '.txt'
        
        from flask import Response
        return Response(
            report_content,
            mimetype='text/plain',
            headers={
                'Content-Disposition': f'attachment; filename={safe_filename}',
                'Content-Type': 'text/plain; charset=utf-8'
            }
        )
        
    except Exception as e:
        print(f"Report download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting SQLite-based authentication app...")
    
    # Initialize database
    init_database()
    
    print("📝 Available endpoints:")
    print("  - GET  /api/health")
    print("  - GET  /api/auth/test")
    print("  - POST /api/auth/signup")
    print("  - POST /api/auth/login")
    print("  - GET  /api/auth/verify/<token>")
    print("  - POST /api/auth/logout")
    print("  - GET  /api/auth/profile")
    print("  - GET  /api/auth/rate-limit-status")
    print("  - POST /api/upload")
    print("  - POST /api/valuation")
    print("  - POST /api/swot")
    print("  - POST /api/report/generate")
    print("  - GET  /api/report/download/<filename>")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
