#!/usr/bin/env python3
"""
Historical Data Backfill for Temporal Database
Process all save files to build complete company timeline
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from strategic_advisor.temporal_database import TemporalGameDatabase

def backfill_historical_data():
    """Process all historical save files for complete timeline analysis"""
    
    print("🕐 Historical Data Backfill for Temporal Database")
    print("="*70)
    
    # Initialize temporal database
    print("📊 Initializing temporal database...")
    db = TemporalGameDatabase("momentum_ai_historical.db")
    
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
    print("\n🔍 Scanning for save files...")
    for source in save_sources:
        print(f"\n📂 Checking: {source['name']}")
        print(f"   Path: {source['path']}")
        print(f"   Description: {source['description']}")
        
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
    
    # Sort by modification time (oldest first for chronological processing)
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
            # Check if already processed
            existing = db.execute_read_query(
                "SELECT id FROM save_files WHERE filename = ?",
                (save_file.name,)
            )
            
            if existing:
                print(f"   ⏭️ Already processed, skipping...")
                skipped_count += 1
                continue
            
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
            
            print(f"   📊 Game Date: {game_date}")
            print(f"   💰 Balance: ${balance:,.2f}")
            print(f"   ⭐ XP: {xp:,.0f}")
            print(f"   🔬 Research Points: {research_points}")
            
            # Process through temporal database
            print(f"   🔄 Ingesting with temporal tracking...")
            save_file_id = db.ingest_save_file(save_file, save_data)
            
            print(f"   ✅ Successfully processed! Database ID: {save_file_id}")
            processed_count += 1
            
            # Show progress summary every 5 files
            if i % 5 == 0:
                print(f"\n📈 Progress Summary:")
                print(f"   Processed: {processed_count}")
                print(f"   Skipped: {skipped_count}")
                print(f"   Errors: {error_count}")
                print(f"   Remaining: {len(all_save_files) - i}")
            
        except Exception as e:
            print(f"   ❌ Error processing {save_file.name}: {str(e)}")
            error_count += 1
            continue
    
    print(f"\n🎯 Historical Backfill Complete!")
    print("="*50)
    print(f"✅ Successfully processed: {processed_count} files")
    print(f"⏭️ Skipped (duplicates): {skipped_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"📊 Total in database: {processed_count + skipped_count - error_count} save files")
    
    if processed_count > 0:
        print(f"\n📈 Generating temporal analysis...")
        analyze_timeline(db)
    
    print(f"\n🗄️ Database file: momentum_ai_historical.db")
    print(f"🚀 Ready for comprehensive trend analysis!")

def analyze_timeline(db: TemporalGameDatabase):
    """Generate timeline analysis from processed data"""
    
    try:
        # Get save file timeline
        timeline = db.execute_read_query("""
            SELECT 
                game_date,
                game_day,
                company_name,
                balance,
                xp,
                research_points,
                real_timestamp
            FROM save_files 
            ORDER BY game_day, real_timestamp
        """)
        
        if timeline:
            print(f"\n📅 Company Timeline Analysis:")
            print(f"   📊 Total snapshots: {len(timeline)}")
            
            first_save = timeline[0]
            last_save = timeline[-1]
            
            print(f"   🏁 First save: Game Day {first_save['game_day']} ({first_save['game_date']})")
            print(f"   🏆 Latest save: Game Day {last_save['game_day']} ({last_save['game_date']})")
            
            # Financial progression
            balance_growth = last_save['balance'] - first_save['balance']
            print(f"   💰 Balance progression: ${first_save['balance']:,.2f} → ${last_save['balance']:,.2f}")
            print(f"   📈 Net growth: ${balance_growth:,.2f}")
            
            # XP progression
            xp_growth = last_save['xp'] - first_save['xp']
            print(f"   ⭐ XP progression: {first_save['xp']:,.0f} → {last_save['xp']:,.0f}")
            print(f"   📈 XP gained: {xp_growth:,.0f}")
            
            # Research progression
            research_growth = last_save['research_points'] - first_save['research_points']
            print(f"   🔬 Research progression: {first_save['research_points']} → {last_save['research_points']}")
            print(f"   📈 Research gained: {research_growth}")
        
        # Transaction analysis
        transaction_summary = db.execute_read_query("""
            SELECT 
                COUNT(*) as total_transactions,
                MIN(day) as earliest_transaction_day,
                MAX(day) as latest_transaction_day,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as total_expenses,
                COUNT(DISTINCT transaction_id) as unique_transactions
            FROM transactions
        """)
        
        if transaction_summary:
            tx_data = transaction_summary[0]
            print(f"\n💳 Transaction Timeline Analysis:")
            print(f"   📊 Total transactions: {tx_data['total_transactions']}")
            print(f"   🔄 Unique transactions: {tx_data['unique_transactions']}")
            print(f"   📅 Transaction span: Day {tx_data['earliest_transaction_day']} to Day {tx_data['latest_transaction_day']}")
            print(f"   💰 Total income: ${tx_data['total_income']:,.2f}")
            print(f"   💸 Total expenses: ${abs(tx_data['total_expenses']):,.2f}")
            print(f"   📈 Net cash flow: ${tx_data['total_income'] + tx_data['total_expenses']:,.2f}")
        
        # Jeets timeline
        jeet_summary = db.execute_read_query("""
            SELECT 
                COUNT(*) as total_jeets,
                COUNT(DISTINCT jeet_id) as unique_jeets,
                MIN(day) as earliest_jeet_day,
                MAX(day) as latest_jeet_day,
                COUNT(DISTINCT jeet_name) as unique_users
            FROM jeets
        """)
        
        if jeet_summary:
            jeet_data = jeet_summary[0]
            print(f"\n🐦 Social Timeline Analysis:")
            print(f"   📊 Total jeets captured: {jeet_data['total_jeets']}")
            print(f"   🔄 Unique jeets: {jeet_data['unique_jeets']}")
            print(f"   👥 Unique users: {jeet_data['unique_users']}")
            print(f"   📅 Jeet span: Day {jeet_data['earliest_jeet_day']} to Day {jeet_data['latest_jeet_day']}")
        
        # Market trends
        market_summary = db.execute_read_query("""
            SELECT 
                COUNT(*) as total_market_snapshots,
                COUNT(DISTINCT component_name) as unique_components,
                AVG(base_price) as avg_base_price,
                AVG(price_change) as avg_price_change,
                MIN(game_day) as earliest_market_day,
                MAX(game_day) as latest_market_day
            FROM market_values
        """)
        
        if market_summary:
            market_data = market_summary[0]
            print(f"\n📊 Market Timeline Analysis:")
            print(f"   📈 Market snapshots: {market_data['total_market_snapshots']}")
            print(f"   🏷️ Unique components: {market_data['unique_components']}")
            print(f"   💰 Average base price: ${market_data['avg_base_price']:,.2f}")
            print(f"   📊 Average price change: {market_data['avg_price_change']:.2f}")
            print(f"   📅 Market data span: Day {market_data['earliest_market_day']} to Day {market_data['latest_market_day']}")
        
    except Exception as e:
        print(f"❌ Timeline analysis failed: {str(e)}")

if __name__ == "__main__":
    backfill_historical_data()