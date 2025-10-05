#!/usr/bin/env python3
"""
Backfill historical save data for trend analysis
Processes all save files from the game_saves directory
"""

import json
from pathlib import Path
from datetime import datetime

from strategic_advisor.main import StrategicAdvisor

def backfill_historical_data():
    """Process all historical save files for trend analysis"""
    
    print("🕐 Historical Data Backfill")
    print("="*60)
    
    # Initialize strategic advisor with the same database
    advisor = StrategicAdvisor(database_path="real_game_analysis.db")
    
    # Look for historical save files
    historical_sources = [
        "game_saves/20250929_sg_momentum ai_ACTIVE",
        "game_saves",  # Check root for any other files
    ]
    
    save_files_found = []
    
    for source_dir in historical_sources:
        source_path = Path(source_dir)
        if source_path.exists():
            print(f"📂 Checking: {source_path}")
            
            # Look for JSON save files
            json_files = list(source_path.glob("*.json"))
            for json_file in json_files:
                if "sg_momentum ai" in json_file.name or "snapshot" in json_file.name:
                    save_files_found.append(json_file)
                    print(f"   Found: {json_file.name} ({json_file.stat().st_size / 1024:.1f} KB)")
    
    print(f"\n📊 Found {len(save_files_found)} historical save files")
    
    if not save_files_found:
        print("⚠️ No historical save files found for processing")
        return
    
    # Sort by modification time (oldest first)
    save_files_found.sort(key=lambda f: f.stat().st_mtime)
    
    print("\n🔄 Processing historical saves in chronological order...")
    
    processed_count = 0
    skipped_count = 0
    
    for save_file in save_files_found:
        try:
            print(f"\n📁 Processing: {save_file.name}")
            
            # Check if this file has already been processed
            with advisor.database.get_read_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM save_files WHERE filename = ?",
                    (save_file.name,)
                )
                exists = cursor.fetchone()[0] > 0
            
            if exists:
                print(f"   ⏭️ Already processed, skipping...")
                skipped_count += 1
                continue
            
            # Load and examine the save file
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Check if it's a valid momentum ai save
            if not _is_valid_momentum_ai_save(save_data):
                print(f"   ❌ Not a valid Momentum AI save file, skipping...")
                skipped_count += 1
                continue
            
            # Extract basic info
            game_date = save_data.get('date', 'Unknown')
            balance = save_data.get('balance', 0)
            employees_data = save_data.get('employees', {})
            employee_count = len([emp for emp in employees_data.values() if emp.get('fired', 0) == 0])
            
            print(f"   📊 Game Date: {game_date}")
            print(f"   💰 Balance: ${balance:,.2f}")
            print(f"   👥 Employees: {employee_count}")
            
            # Process through the system
            result = advisor.process_save_file(str(save_file))
            
            if result['success']:
                print(f"   ✅ Successfully processed (Save ID: {result['save_file_id']})")
                processed_count += 1
            else:
                print(f"   ❌ Processing failed: {result['error']}")
                skipped_count += 1
            
        except Exception as e:
            print(f"   ❌ Error processing {save_file.name}: {str(e)}")
            skipped_count += 1
    
    print(f"\n📈 Backfill Complete!")
    print(f"   ✅ Processed: {processed_count} files")
    print(f"   ⏭️ Skipped: {skipped_count} files")
    
    if processed_count > 0:
        print("\n🔍 Running trend analysis on historical data...")
        try:
            capacity_trends = advisor.capacity_analyzer.calculate_trend_analysis()
            
            print("📊 Capacity Trends:")
            if capacity_trends:
                for key, value in capacity_trends.items():
                    print(f"   {key}: {value}")
            else:
                print("   No trend data available yet")
                
        except Exception as e:
            print(f"   ❌ Trend analysis failed: {str(e)}")
    
    print("\n🎯 Historical backfill complete! Database now contains full timeline.")

def _is_valid_momentum_ai_save(save_data: dict) -> bool:
    """Check if this is a valid Momentum AI save file"""
    try:
        # Check for required fields
        required_fields = ['date', 'balance', 'employees']
        if not all(field in save_data for field in required_fields):
            return False
        
        # Check if it has employee data (indicating it's not just a template)
        employees = save_data.get('employees', {})
        if len(employees) == 0:
            return False
        
        # Check for reasonable balance (not default starting values)
        balance = save_data.get('balance', 0)
        if balance < 1000:  # Too low for an active company
            return False
        
        return True
        
    except Exception:
        return False

if __name__ == "__main__":
    backfill_historical_data()