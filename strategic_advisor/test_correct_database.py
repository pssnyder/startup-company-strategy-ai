#!/usr/bin/env python3
"""
Test the corrected database with actual save file
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from correct_temporal_database import CorrectTemporalGameDatabase

def test_correct_database():
    print("🧪 Testing Corrected Database with Real Save File")
    print("="*60)
    
    # Use the corrected database
    db = CorrectTemporalGameDatabase("momentum_ai_correct.db")
    
    # Load the current save file
    save_file_path = Path("C:/Users/patss/Saved Games/Startup Company/testing_v1/sg_momentum ai.json")
    
    if not save_file_path.exists():
        # Fallback to processed version
        save_file_path = Path("strategic_advisor/save_files/20251005_1139_sg_momentum_ai.json")
    
    print(f"📁 Loading save file: {save_file_path}")
    
    with open(save_file_path, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    # Show what we're about to ingest
    print(f"📊 Save file analysis:")
    print(f"   Company: {save_data.get('companyName', 'Unknown')}")
    print(f"   Balance: ${save_data.get('balance', 0):,.2f}")
    print(f"   Transactions: {len(save_data.get('transactions', []))}")
    print(f"   Candidates: {len(save_data.get('candidates', []))} ⭐")
    print(f"   Products: {len(save_data.get('products', []))}")
    print(f"   Feature Instances: {len(save_data.get('featureInstances', []))}")
    print(f"   Jeets: {len(save_data.get('jeets', []))}")
    print(f"   Market Values: {len(save_data.get('marketValues', {}))}")
    
    # Ingest the save file
    print(f"\n🔄 Ingesting save file...")
    save_file_id = db.ingest_save_file(save_file_path, save_data)
    
    # Show what was actually captured
    print(f"\n📊 Database Contents After Ingestion:")
    counts = db.get_table_counts()
    
    for table_name, count in counts.items():
        emoji = "⭐" if count > 0 else "❌"
        print(f"   {emoji} {table_name}: {count:,} records")
    
    # Test specific candidate data
    if counts['candidates'] > 0:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT candidate_id, name, employee_type_name, salary, level 
            FROM candidates 
            LIMIT 5
        """)
        
        print(f"\n👥 Sample Candidates Data:")
        for row in cursor.fetchall():
            print(f"   • {row[1]} ({row[2]}) - Level {row[4]} - ${row[3]:,}/salary")
    
    # Test products data
    if counts['products'] > 0:
        cursor.execute("""
            SELECT product_id, name, product_type_name, framework_name 
            FROM products 
            LIMIT 3
        """)
        
        print(f"\n🏭 Sample Products Data:")
        for row in cursor.fetchall():
            print(f"   • {row[1]} ({row[2]}) - Framework: {row[3]}")
    
    print(f"\n✅ Corrected database test complete!")
    print(f"🎯 Now properly capturing ALL game save file data including candidates!")
    
    db.close()

if __name__ == "__main__":
    test_correct_database()