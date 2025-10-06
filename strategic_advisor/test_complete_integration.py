"""
Test Complete Database Integration
Load real save file data into the complete schema
"""

import json
import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from complete_database import CompleteGameDatabase

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_database_integration():
    """Test the complete database with real save file data"""
    
    logger.info("🚀 Starting Complete Database Integration Test")
    
    # Initialize database
    db = CompleteGameDatabase()
    
    # Load save file
    save_file_path = Path("save_files/20251005_1139_sg_momentum_ai.json")
    
    if not save_file_path.exists():
        logger.error(f"❌ Save file not found: {save_file_path}")
        return False
    
    try:
        # Load JSON data
        logger.info(f"📁 Loading save file: {save_file_path}")
        with open(save_file_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        logger.info(f"✅ Save file loaded: {len(save_data)} top-level keys")
        
        # Ingest into complete database
        logger.info("💾 Ingesting save file into complete database...")
        game_state_id = db.ingest_complete_save_file(save_file_path, save_data)
        
        logger.info(f"✅ Save file ingested successfully! Game State ID: {game_state_id}")
        
        # Get dashboard summary
        logger.info("📊 Generating dashboard summary...")
        dashboard_data = db.get_dashboard_summary()
        
        # Display results
        print("\n" + "="*60)
        print("📈 COMPLETE DATABASE INTEGRATION RESULTS")
        print("="*60)
        
        company_info = dashboard_data.get('company_info', {})
        print(f"🏢 Company: {company_info.get('name', 'Unknown')}")
        print(f"📅 Game Date: {company_info.get('game_date', 'Unknown')}")
        print(f"🗓️  Game Day: {company_info.get('game_day', 0)}")
        print(f"💰 Balance: ${company_info.get('balance', 0):,.2f}")
        print(f"⭐ XP: {company_info.get('xp', 0):,.0f}")
        print(f"🔬 Research Points: {company_info.get('research_points', 0)}")
        
        # Calculated metrics
        calc_metrics = dashboard_data.get('calculated_metrics', {})
        
        if 'employee_metrics' in calc_metrics:
            emp_metrics = calc_metrics['employee_metrics']
            print(f"\n👥 EMPLOYEE METRICS:")
            print(f"   Total Employees: {emp_metrics.get('total_employees', 0)}")
            print(f"   Average Salary: ${emp_metrics.get('average_salary', 0):,.2f}")
            print(f"   Total Payroll: ${emp_metrics.get('total_payroll', 0):,.2f}")
        
        if 'financial_metrics' in calc_metrics:
            fin_metrics = calc_metrics['financial_metrics']
            print(f"\n💸 FINANCIAL METRICS:")
            print(f"   Transactions: {fin_metrics.get('transaction_count', 0)}")
            print(f"   Total Income: ${fin_metrics.get('total_income', 0):,.2f}")
            print(f"   Total Expenses: ${fin_metrics.get('total_expenses', 0):,.2f}")
            print(f"   Net Income: ${fin_metrics.get('net_income', 0):,.2f}")
        
        if 'product_metrics' in calc_metrics:
            prod_metrics = calc_metrics['product_metrics']
            print(f"\n📦 PRODUCT METRICS:")
            print(f"   Total Products: {prod_metrics.get('total_products', 0)}")
        
        if 'market_metrics' in calc_metrics:
            market_metrics = calc_metrics['market_metrics']
            print(f"\n📈 MARKET METRICS:")
            print(f"   Components Tracked: {market_metrics.get('components_tracked', 0)}")
            print(f"   Avg Component Price: ${market_metrics.get('average_component_price', 0):,.2f}")
        
        if 'performance_metrics' in calc_metrics:
            perf_metrics = calc_metrics['performance_metrics']
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Data Ingestion: {'✅' if perf_metrics.get('data_ingestion_complete') else '❌'}")
            print(f"   Schema Coverage: {perf_metrics.get('schema_coverage', 'Unknown')}")
            print(f"   Tables Populated: {perf_metrics.get('tables_populated', 0)}")
        
        # Data quality
        data_quality = dashboard_data.get('data_quality', {})
        print(f"\n🔍 DATA QUALITY:")
        print(f"   Ingestion Time: {data_quality.get('ingestion_time', 'Unknown')}")
        print(f"   File Size: {data_quality.get('file_size', 0):,} bytes")
        print(f"   Schema Version: {data_quality.get('schema_version', 'Unknown')}")
        
        print("\n" + "="*60)
        print("✅ COMPLETE DATABASE INTEGRATION SUCCESSFUL!")
        print("="*60)
        
        # Test some specific queries
        logger.info("🔍 Testing specific reporting queries...")
        
        # Employee breakdown
        employees = db.execute_reporting_query("""
            SELECT employeeTypeName, COUNT(*) as count, AVG(CAST(salary AS REAL)) as avg_salary
            FROM employees 
            WHERE game_state_id = ?
            GROUP BY employeeTypeName
            ORDER BY count DESC
        """, (game_state_id,))
        
        if employees:
            print(f"\n👥 EMPLOYEE BREAKDOWN:")
            for emp_type in employees:
                print(f"   {emp_type['employeeTypeName']}: {emp_type['count']} employees (avg: ${emp_type['avg_salary']:,.2f})")
        
        # Recent transactions
        recent_transactions = db.execute_reporting_query("""
            SELECT label, amount, day, hour, minute
            FROM transactions 
            WHERE game_state_id = ?
            ORDER BY day DESC, hour DESC, minute DESC
            LIMIT 5
        """, (game_state_id,))
        
        if recent_transactions:
            print(f"\n💰 RECENT TRANSACTIONS:")
            for txn in recent_transactions:
                print(f"   Day {txn['day']} {txn['hour']:02d}:{txn['minute']:02d} - {txn['label']}: ${txn['amount']:,.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_database_integration()
    
    if success:
        print("\n🎉 Ready to proceed with reporting layer development!")
        print("📋 Next steps:")
        print("   1. Define reporting views for strategic insights")
        print("   2. Create calculated metrics for decision making")
        print("   3. Build dashboard interfaces")
        print("   4. Integrate with real-time monitoring")
    else:
        print("\n❌ Integration test failed - check logs for details")