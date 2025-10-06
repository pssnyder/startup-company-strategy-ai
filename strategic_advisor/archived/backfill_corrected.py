#!/usr/bin/env python3
"""
Backfill Historical Data with Corrected Database Schema
Now properly capturing candidates, products, and all other game data
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from correct_temporal_database import CorrectTemporalGameDatabase

def backfill_corrected_database():
    print("🚀 Historical Backfill with CORRECTED Database Schema")
    print("="*70)
    
    # Use the corrected database
    db = CorrectTemporalGameDatabase("momentum_ai_complete.db")
    
    # Define all save file sources
    save_sources = [
        {
            'name': 'Historical Archive',
            'path': Path('game_saves/20250929_sg_momentum ai'),
            'description': 'Historical snapshots from September 29th'
        },
        {
            'name': 'Current Primary Save',
            'path': Path('C:/Users/patss/Saved Games/Startup Company/testing_v1/sg_momentum ai.json'),
            'description': 'Most recent live save file'
        },
        {
            'name': 'Current Autosave',
            'path': Path('C:/Users/patss/Saved Games/Startup Company/testing_v1/sg_momentum ai_autosave.json'),
            'description': 'Most recent autosave backup'
        },
        {
            'name': 'Processed Archive',
            'path': Path('strategic_advisor/save_files'),
            'description': 'Previously processed save files'
        }
    ]
    
    all_save_files = []
    
    # Collect all save files
    print("🔍 Scanning for save files...")
    for source in save_sources:
        print(f"\n📂 Checking: {source['name']}")
        
        if source['path'].is_file():
            # Single file
            if source['path'].suffix == '.json':
                all_save_files.append({
                    'file': source['path'],
                    'source': source['name'],
                    'modified': source['path'].stat().st_mtime
                })
                print(f"   ✅ Found: {source['path'].name} ({source['path'].stat().st_size / 1024:.1f} KB)")
        
        elif source['path'].is_dir():
            # Directory of files
            json_files = list(source['path'].glob('*.json'))
            print(f"   📁 Directory contains {len(json_files)} JSON files")
            
            for json_file in json_files:
                if 'sg_momentum ai' in json_file.name or 'momentum' in json_file.name.lower():
                    all_save_files.append({
                        'file': json_file,
                        'source': source['name'],
                        'modified': json_file.stat().st_mtime
                    })
                    print(f"   ✅ Found: {json_file.name} ({json_file.stat().st_size / 1024:.1f} KB)")
        else:
            print(f"   ❌ Path not found: {source['path']}")
    
    if not all_save_files:
        print("\n❌ No save files found for processing!")
        return
    
    # Sort by modification time (oldest first)
    all_save_files.sort(key=lambda x: x['modified'])
    
    print(f"\n📊 Total save files found: {len(all_save_files)}")
    print("📅 Processing in chronological order...")
    
    # Process each save file
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, save_info in enumerate(all_save_files, 1):
        save_file = save_info['file']
        source_name = save_info['source']
        modified_time = datetime.fromtimestamp(save_info['modified'])
        
        print(f"\n📁 [{i}/{len(all_save_files)}] Processing: {save_file.name}")
        print(f"   Source: {source_name}")
        print(f"   Modified: {modified_time}")
        print(f"   Size: {save_file.stat().st_size / 1024:.1f} KB")
        
        try:
            # Load and validate save file
            print(f"   📖 Loading JSON data...")
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Validate it's a momentum ai save
            company_name = save_data.get('companyName', '')
            if 'momentum' not in company_name.lower():
                print(f"   ❌ Not a Momentum AI save file (company: {company_name}), skipping...")
                skipped_count += 1
                continue
            
            # Extract key info for preview
            game_date = save_data.get('date', 'Unknown')
            balance = save_data.get('balance', 0)
            xp = save_data.get('xp', 0)
            research_points = save_data.get('researchPoints', 0)
            candidates_count = len(save_data.get('candidates', []))
            products_count = len(save_data.get('products', []))
            
            print(f"   📊 Game Date: {game_date}")
            print(f"   💰 Balance: ${balance:,.2f}")
            print(f"   ⭐ XP: {xp:,.0f}")
            print(f"   🔬 Research Points: {research_points}")
            print(f"   👥 Candidates: {candidates_count}")
            print(f"   🏭 Products: {products_count}")
            
            # Process through corrected database
            print(f"   🔄 Ingesting with COMPLETE schema...")
            save_file_id = db.ingest_save_file(save_file, save_data)
            
            print(f"   ✅ Successfully processed! Database ID: {save_file_id}")
            processed_count += 1
            
        except Exception as e:
            print(f"   ❌ Error processing {save_file.name}: {str(e)}")
            error_count += 1
            continue
    
    print(f"\n🎯 CORRECTED Historical Backfill Complete!")
    print("="*60)
    print(f"✅ Successfully processed: {processed_count} files")
    print(f"⏭️ Skipped (not Momentum AI): {skipped_count} files")
    print(f"❌ Errors: {error_count} files")
    
    if processed_count > 0:
        print(f"\n📊 Final Database Summary:")
        counts = db.get_table_counts()
        
        total_records = sum(counts.values())
        print(f"   📊 Total Records: {total_records:,}")
        
        for table_name, count in counts.items():
            if count > 0:
                print(f"   ✅ {table_name}: {count:,} records")
        
        # Show sample data from key tables
        cursor = db.connection.cursor()
        
        print(f"\n👥 Sample Candidates Analysis:")
        cursor.execute("""
            SELECT employee_type_name, COUNT(*) as count, AVG(salary) as avg_salary
            FROM candidates 
            GROUP BY employee_type_name
            ORDER BY count DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"   • {row[0]}: {row[1]} candidates, ${row[2]:,.0f} avg salary")
        
        print(f"\n🏭 Products Timeline:")
        cursor.execute("""
            SELECT p.name, p.product_type_name, COUNT(DISTINCT sf.id) as snapshots
            FROM products p
            JOIN save_files sf ON p.save_file_id = sf.id
            GROUP BY p.name, p.product_type_name
            ORDER BY snapshots DESC
        """)
        for row in cursor.fetchall():
            print(f"   • {row[0]} ({row[1]}): {row[2]} snapshots")
    
    print(f"\n🗄️ Database file: momentum_ai_complete.db")
    print(f"🎉 COMPLETE game save data now properly captured!")
    print(f"✅ Includes: candidates, products, features, inventory, competitors, and more!")
    
    db.close()

if __name__ == "__main__":
    backfill_corrected_database()