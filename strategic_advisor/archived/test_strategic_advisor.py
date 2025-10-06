"""
Test Strategic Advisor System
Verifies file monitoring, database ingestion, and decision modules
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from strategic_advisor.main import StrategicAdvisor
from strategic_advisor.database_sqlite import GameDatabase
from strategic_advisor.decision_modules.capacity_analyzer import CapacityAnalyzer

def test_database_operations():
    """Test database creation and basic operations"""
    print("🧪 Testing database operations...")
    
    try:
        # Create test database
        db = GameDatabase("test_strategic_advisor.db")
        
        # Test basic queries
        latest_save = db.get_latest_save_file()
        print(f"   Latest save: {latest_save}")
        
        balance_trend = db.get_balance_trend(10)
        print(f"   Balance trend records: {len(balance_trend)}")
        
        capacity_metrics = db.get_capacity_metrics()
        print(f"   Capacity metrics: {capacity_metrics}")
        
        print("✅ Database operations successful")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

def test_capacity_analyzer():
    """Test capacity analyzer with mock data"""
    print("🧪 Testing capacity analyzer...")
    
    try:
        # Create test database and analyzer
        db = GameDatabase("test_strategic_advisor.db")
        analyzer = CapacityAnalyzer(db)
        
        # Test capacity analysis (may have no data, but should not crash)
        metrics = analyzer.analyze_current_capacity()
        print(f"   Capacity metrics: {metrics}")
        
        recommendations = analyzer.get_capacity_recommendations(metrics)
        print(f"   Recommendations: {len(recommendations)} items")
        
        trends = analyzer.calculate_trend_analysis()
        print(f"   Trend analysis: {trends}")
        
        print("✅ Capacity analyzer test successful")
        return True
        
    except Exception as e:
        print(f"❌ Capacity analyzer test failed: {str(e)}")
        return False

def test_file_processing():
    """Test processing a real save file"""
    print("🧪 Testing save file processing...")
    
    try:
        # Find a real save file
        save_path = Path("c:/Users/patss/Saved Games/Startup Company/testing_v1/sg_momentum ai.json")
        
        if not save_path.exists():
            print("⚠️ Save file not found, skipping file processing test")
            return True
        
        # Load and process the save file
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # Create test database and ingest
        db = GameDatabase("test_strategic_advisor.db")
        save_file_id = db.ingest_save_file(save_path, save_data)
        
        print(f"   Save file ingested with ID: {save_file_id}")
        
        # Test capacity analysis with real data
        analyzer = CapacityAnalyzer(db)
        metrics = analyzer.analyze_current_capacity()
        
        print(f"   Real data analysis:")
        print(f"     Workstation utilization: {metrics.workstation_utilization:.1f}%")
        print(f"     Growth capacity: {metrics.growth_capacity}")
        print(f"     Team efficiency: {metrics.employee_efficiency:.1f}%")
        print(f"     Capacity shortage: {metrics.capacity_shortage}")
        
        alerts = metrics.get_quantitative_alerts()
        if alerts:
            print(f"   Alerts generated:")
            for alert in alerts:
                print(f"     🚨 {alert}")
        
        print("✅ File processing test successful")
        return True
        
    except Exception as e:
        print(f"❌ File processing test failed: {str(e)}")
        return False

def test_strategic_advisor_init():
    """Test strategic advisor initialization"""
    print("🧪 Testing strategic advisor initialization...")
    
    try:
        # Create strategic advisor (but don't start monitoring)
        advisor = StrategicAdvisor(database_path="test_strategic_advisor.db")
        
        # Test dashboard data generation
        dashboard_data = advisor.get_dashboard_data()
        print(f"   Dashboard data keys: {list(dashboard_data.keys())}")
        
        print("✅ Strategic advisor initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Strategic advisor initialization failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Starting Strategic Advisor System Tests\n")
    
    tests = [
        ("Database Operations", test_database_operations),
        ("Capacity Analyzer", test_capacity_analyzer),
        ("File Processing", test_file_processing),
        ("Strategic Advisor Init", test_strategic_advisor_init)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)
        if test_func():
            passed += 1
        print()
    
    # Summary
    print("="*60)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Strategic Advisor system is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    # Cleanup
    test_db_path = Path("test_strategic_advisor.db")
    if test_db_path.exists():
        test_db_path.unlink()
        print("🧹 Test database cleaned up")

if __name__ == "__main__":
    run_all_tests()