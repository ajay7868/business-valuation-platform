#!/usr/bin/env python3
"""
Database initialization script for SQLite
"""

import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize SQLite database with required tables"""
    
    # Database file path
    db_path = 'valuation_platform.db'
    
    print(f"🔧 Initializing SQLite database: {db_path}")
    
    try:
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Database connection established successfully")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                mobile TEXT,
                email_verified BOOLEAN DEFAULT 0,
                verification_token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        print("✅ Users table created/verified")
        
        # Create rate_limits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                device_id TEXT,
                endpoint TEXT NOT NULL,
                attempt_count INTEGER DEFAULT 1,
                first_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_until TIMESTAMP
            )
        ''')
        print("✅ Rate limits table created/verified")
        
        # Create user_activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ip_address TEXT NOT NULL,
                device_id TEXT,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ User activities table created/verified")
        
        # Create user_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ User sessions table created/verified")
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_endpoint ON rate_limits(ip_address, endpoint)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)')
        print("✅ Database indexes created/verified")
        
        # Commit changes
        conn.commit()
        print("✅ Database initialization completed successfully")
        
        # Test database operations
        test_database_operations(cursor)
        
        conn.close()
        print("✅ Database connection closed")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_operations(cursor):
    """Test basic database operations"""
    print("\n🧪 Testing database operations...")
    
    try:
        # Test insert
        cursor.execute('''
            INSERT OR IGNORE INTO users (email, password_hash, mobile, email_verified)
            VALUES (?, ?, ?, ?)
        ''', ('test@example.com', 'test_hash', '1234567890', 1))
        
        # Test select
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"✅ User count: {user_count}")
        
        # Test rate limit insert
        cursor.execute('''
            INSERT OR IGNORE INTO rate_limits (ip_address, endpoint, attempt_count)
            VALUES (?, ?, ?)
        ''', ('127.0.0.1', 'test_endpoint', 1))
        
        # Test rate limit select
        cursor.execute('SELECT COUNT(*) FROM rate_limits')
        rate_limit_count = cursor.fetchone()[0]
        print(f"✅ Rate limit count: {rate_limit_count}")
        
        print("✅ All database operations working correctly")
        
    except sqlite3.Error as e:
        print(f"❌ Database operation test failed: {e}")

def check_database_status():
    """Check current database status"""
    db_path = 'valuation_platform.db'
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"📊 Database file: {db_path}")
        print(f"📏 File size: {file_size} bytes ({file_size/1024:.2f} KB)")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check table counts
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📋 Tables: {[table[0] for table in tables]}")
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} records")
            
            conn.close()
            print("✅ Database status check completed")
            
        except sqlite3.Error as e:
            print(f"❌ Database status check failed: {e}")
    else:
        print(f"❌ Database file not found: {db_path}")

if __name__ == "__main__":
    print("🚀 SQLite Database Initialization")
    print("=" * 50)
    
    # Initialize database
    if init_database():
        print("\n" + "=" * 50)
        print("📊 Database Status Report")
        print("=" * 50)
        check_database_status()
    else:
        print("❌ Database initialization failed")
