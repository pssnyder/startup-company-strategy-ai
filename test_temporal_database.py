#!/usr/bin/env python3
"""
Test the new temporal database implementation
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from strategic_advisor.temporal_database import TemporalGameDatabase

def test_temporal_database():
    """Test the temporal database with real save file"""
    
    print("🧪 Testing Temporal Database Implementation")
    print("="*60)
    
    # Initialize temporal database
    print("📊 Initializing temporal database...")
    db = TemporalGameDatabase("test_temporal_game.db")
    
    # Load and process real save file
    save_file = Path("strategic_advisor/save_files/20251005_1139_sg_momentum_ai.json")
    
    if not save_file.exists():
        print(f"❌ Save file not found: {save_file}")
        return
    
    print(f"📁 Processing save file: {save_file.name}")
    print(f"💾 File size: {save_file.stat().st_size / 1024:.1f} KB")
    
    import json
    with open(save_file, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    print(f"📊 JSON data loaded: {len(save_data)} top-level fields")
    
    # Test save file ingestion
    print("\n🔄 Ingesting save file with temporal tracking...")
    try:
        save_file_id = db.ingest_save_file(save_file, save_data)
        print(f"✅ Save file ingested successfully! ID: {save_file_id}")
    except Exception as e:
        print(f"❌ Save file ingestion failed: {str(e)}")
        return
    
    # Test data retrieval
    print("\n📈 Testing temporal data retrieval...")
    
    # Check save files table
    latest_save = db.get_latest_save_file()
    if latest_save:
        print(f"✅ Latest save file:")
        print(f"   Company: {latest_save['company_name']}")
        print(f"   Game Date: {latest_save['game_date']}")
        print(f"   Game Day: {latest_save['game_day']}")
        print(f"   Balance: ${latest_save['balance']:,.2f}")
        print(f"   Real Timestamp: {latest_save['real_timestamp']}")
    
    # Check transactions with temporal data
    transactions = db.execute_read_query("""
        SELECT COUNT(*) as count, 
               MIN(day) as earliest_day, 
               MAX(day) as latest_day,
               MIN(captured_at) as first_captured
        FROM transactions
    """)
    
    if transactions:
        tx_data = transactions[0]
        print(f"\n💰 Transactions temporal analysis:")
        print(f"   Total transactions: {tx_data['count']}")
        print(f"   Game day range: {tx_data['earliest_day']} to {tx_data['latest_day']}")
        print(f"   First captured: {tx_data['first_captured']}")
    
    # Check jeets with temporal data
    jeets = db.execute_read_query("""
        SELECT COUNT(*) as count,
               MIN(day) as earliest_day,
               MAX(day) as latest_day,
               COUNT(DISTINCT jeet_id) as unique_jeets
        FROM jeets
    """)
    
    if jeets:
        jeet_data = jeets[0]
        print(f"\n🐦 Jeets temporal analysis:")
        print(f"   Total jeets: {jeet_data['count']}")
        print(f"   Unique jeets: {jeet_data['unique_jeets']}")
        print(f"   Game day range: {jeet_data['earliest_day']} to {jeet_data['latest_day']}")
    
    # Check market values with temporal data
    market_values = db.execute_read_query("""
        SELECT COUNT(*) as count,
               MIN(base_price) as min_price,
               MAX(base_price) as max_price,
               AVG(price_change) as avg_change
        FROM market_values
    """)
    
    if market_values:
        market_data = market_values[0]
        print(f"\n📊 Market values temporal analysis:")
        print(f"   Total components: {market_data['count']}")
        print(f"   Price range: ${market_data['min_price']} to ${market_data['max_price']}")
        print(f"   Average price change: {market_data['avg_change']:.2f}")
    
    # Test duplicate handling
    print(f"\n🔄 Testing deduplication by re-ingesting same file...")
    try:
        save_file_id_2 = db.ingest_save_file(save_file, save_data)
        print(f"✅ Re-ingestion completed! ID: {save_file_id_2}")
        
        # Check if duplicates were avoided
        transactions_after = db.execute_read_query("SELECT COUNT(*) as count FROM transactions")
        if transactions_after:
            print(f"   Transactions count after re-ingestion: {transactions_after[0]['count']}")
            if transactions_after[0]['count'] == tx_data['count']:
                print(f"✅ Duplicate transactions properly avoided!")
            else:
                print(f"⚠️ Transactions increased - deduplication may need improvement")
                
    except Exception as e:
        print(f"❌ Re-ingestion test failed: {str(e)}")
    
    print(f"\n🎯 Temporal Database Test Complete!")
    print(f"   Database file: test_temporal_game.db")
    print(f"   Ready for historical backfill and trend analysis!")

if __name__ == "__main__":
    test_temporal_database()