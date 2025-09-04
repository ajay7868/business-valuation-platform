#!/usr/bin/env python3
"""
Simple database viewer for the valuation platform
"""

import sqlite3
from datetime import datetime

def view_database():
    """View all database tables and their contents"""
    
    db_path = 'valuation_platform.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Database Viewer for Valuation Platform")
        print("=" * 50)
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 Table: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"Total rows: {row_count}")
            
            if row_count > 0:
                # Get all data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Print column headers
                print(" | ".join(f"{col:15}" for col in column_names))
                print("-" * (len(column_names) * 18))
                
                # Print data rows
                for row in rows:
                    formatted_row = []
                    for i, value in enumerate(row):
                        if value is None:
                            formatted_row.append("NULL")
                        elif isinstance(value, str) and len(value) > 15:
                            formatted_row.append(f"{value[:12]}...")
                        else:
                            formatted_row.append(f"{str(value):15}")
                    print(" | ".join(formatted_row))
            else:
                print("(No data)")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def view_users_summary():
    """View users table summary"""
    
    db_path = 'valuation_platform.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n👥 Users Summary")
        print("=" * 30)
        
        cursor.execute("""
            SELECT 
                id, 
                email, 
                mobile, 
                email_verified,
                created_at,
                last_login
            FROM users 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        
        if users:
            print(f"{'ID':<3} | {'Email':<25} | {'Mobile':<12} | {'Verified':<8} | {'Created':<19} | {'Last Login':<19}")
            print("-" * 100)
            
            for user in users:
                user_id, email, mobile, verified, created, last_login = user
                verified_str = "✅ Yes" if verified else "❌ No"
                mobile_str = mobile if mobile else "N/A"
                created_str = created if created else "N/A"
                last_login_str = last_login if last_login else "Never"
                
                print(f"{user_id:<3} | {email:<25} | {mobile_str:<12} | {verified_str:<8} | {created_str:<19} | {last_login_str:<19}")
        else:
            print("No users found")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Database Viewer...")
    
    # View full database
    view_database()
    
    # View users summary
    view_users_summary()
    
    print("\n✅ Database viewing completed!")
