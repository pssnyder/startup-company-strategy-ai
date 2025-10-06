#!/usr/bin/env python3
"""
Check what was actually saved to the database
"""

import sqlite3
import json
from pathlib import Path

def check_database():
    """Check the contents of the database"""
    
    db_path = "real_game_analysis.db"
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"🔍 Analyzing database: {db_path}")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Tables in database: {len(tables)}")
    for table in tables:
        print(f"   • {table}")
    
    print()
    
    # Check each table
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"📋 {table}: {count} records")
            
            # Show sample data for key tables
            if table == "save_files" and count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                row = cursor.fetchone()
                print(f"   Sample: {row[:5]}...")  # First 5 columns
                
            elif table == "employees" and count > 0:
                cursor.execute(f"SELECT COUNT(*), AVG(salary) FROM {table}")
                count, avg_salary = cursor.fetchone()
                print(f"   Average salary: ${avg_salary:,.2f}")
                
            elif table == "transactions" and count > 0:
                cursor.execute(f"SELECT MIN(amount), MAX(amount), COUNT(*) FROM {table}")
                min_amt, max_amt, count = cursor.fetchone()
                print(f"   Amount range: ${min_amt:,.2f} to ${max_amt:,.2f}")
                
        except Exception as e:
            print(f"❌ Error checking {table}: {str(e)}")
    
    # Get latest save file details
    try:
        cursor.execute("""
        SELECT filename, company_name, balance, total_employees, real_timestamp 
        FROM save_files 
        ORDER BY real_timestamp DESC 
        LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            filename, company, balance, employees, timestamp = row
            print()
            print("🎯 Latest Save File:")
            print(f"   File: {filename}")
            print(f"   Company: {company}")
            print(f"   Balance: ${balance:,.2f}")
            print(f"   Employees: {employees}")
            print(f"   Timestamp: {timestamp}")
    except Exception as e:
        print(f"❌ Error getting latest save: {str(e)}")
    
    conn.close()
    print("\n✅ Database analysis complete!")

if __name__ == "__main__":
    check_database()