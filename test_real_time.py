"""
Test script for the real-time monitoring system.
This creates mock data to test the dashboard and analysis components.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import random

from ai_advisor.dashboard import RealTimeDashboard
from ai_advisor.file_watcher import SaveFileWatcher


def create_mock_save_data(balance: float, users: int, satisfaction: float, employees: int) -> dict:
    """Create mock save file data for testing."""
    return {
        "date": datetime.now().isoformat(),
        "started": (datetime.now() - timedelta(days=30)).isoformat(),
        "balance": balance,
        "progress": {
            "products": [{
                "users": {
                    "total": users,
                    "satisfaction": satisfaction
                }
            }]
        },
        "office": {
            "workstations": [
                {"employee": {"salary": 5000 + random.randint(-1000, 1000)}}
                for _ in range(employees)
            ]
        },
        "featureInstances": [
            {
                "featureName": "Landing Page",
                "quality": {"current": 25, "max": 50},
                "efficiency": {"current": 30, "max": 50}
            },
            {
                "featureName": "Login System", 
                "quality": {"current": 15, "max": 40},
                "efficiency": {"current": 20, "max": 40}
            }
        ]
    }


def test_dashboard_system():
    """Test the dashboard system with mock data."""
    print("🧪 Testing Real-Time Dashboard System")
    print("=====================================")
    
    # Create test data directory
    test_dir = Path("test_game_saves")
    test_dir.mkdir(exist_ok=True)
    
    # Create mock timeline data
    metrics_file = test_dir / "metrics_timeline.jsonl"
    
    print("📝 Creating mock timeline data...")
    
    # Generate 24 hours of mock data
    start_time = datetime.now() - timedelta(hours=24)
    
    with open(metrics_file, 'w', encoding='utf-8') as f:
        for hour in range(24):
            timestamp = start_time + timedelta(hours=hour)
            
            # Simulate declining satisfaction and cash
            satisfaction = max(40, 85 - (hour * 2) + random.randint(-5, 5))
            balance = max(10000, 200000 - (hour * 3000) + random.randint(-5000, 5000))
            users = min(50000, 1000 + (hour * 500) + random.randint(-100, 200))
            employees = min(15, 3 + (hour // 4))
            
            metrics = {
                'timestamp': timestamp.isoformat(),
                'file_type': 'autosave' if hour % 2 == 0 else 'manual',
                'game_date': f"Day {30 + hour}",
                'balance': balance,
                'total_users': users,
                'satisfaction': satisfaction,
                'total_employees': employees,
                'features_count': 2,
                'monthly_expenses': employees * 5000
            }
            
            f.write(json.dumps(metrics) + '\n')
    
    print(f"✅ Created {24} hours of mock data")
    
    # Test dashboard
    print("\n📊 Testing Dashboard Analysis...")
    dashboard = RealTimeDashboard(str(test_dir))
    
    # Get current state
    current_state = dashboard.get_current_state()
    if current_state:
        print(f"   Balance: ${current_state.balance:,.2f}")
        print(f"   Users: {current_state.total_users:,}")
        print(f"   Satisfaction: {current_state.satisfaction:.1f}%")
        print(f"   Runway: {current_state.runway_months:.1f} months")
        print(f"   User Growth: {current_state.user_growth_rate:.1f}%")
    
    # Generate alerts
    alerts = dashboard.generate_alerts()
    print(f"\n🚨 Generated {len(alerts)} alerts:")
    for alert in alerts:
        icon = {"critical": "🔥", "warning": "⚠️", "info": "ℹ️"}.get(alert.level, "📌")
        print(f"   {icon} {alert.title}: {alert.message}")
    
    # Export dashboard data
    dashboard_file = dashboard.export_dashboard_json()
    print(f"\n💾 Dashboard data exported to: {dashboard_file}")
    
    # Test trend data
    print("\n📈 Testing Trend Analysis...")
    satisfaction_trend = dashboard.get_trend_data('satisfaction', hours_back=12)
    print(f"   Satisfaction trend points: {len(satisfaction_trend['values'])}")
    
    balance_trend = dashboard.get_trend_data('balance', hours_back=12)
    print(f"   Balance trend points: {len(balance_trend['values'])}")
    
    print("\n✅ Dashboard system test completed!")
    print(f"🗂️ Test data saved in: {test_dir}")


def test_file_watcher():
    """Test file watcher with mock save files."""
    print("\n🔍 Testing File Watcher System")
    print("==============================")
    
    # Create test save directory
    save_dir = Path("test_saves")
    save_dir.mkdir(exist_ok=True)
    
    output_dir = Path("test_file_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create mock save files
    autosave_file = save_dir / "sg_rts technology & solutions llc_autosave.json"
    manual_file = save_dir / "sg_rts technology & solutions llc.json"
    
    # Create file watcher
    watcher = SaveFileWatcher(str(save_dir), str(output_dir))
    
    print("📁 Creating mock save files...")
    
    # Create and process mock autosave
    mock_data = create_mock_save_data(150000, 25000, 65.5, 8)
    with open(autosave_file, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, indent=2)
    
    watcher._process_save_file(autosave_file, autosave_file.name)
    
    # Create and process mock manual save
    mock_data['balance'] = 145000  # Slightly different data
    mock_data['progress']['products'][0]['users']['satisfaction'] = 62.0
    
    with open(manual_file, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, indent=2)
    
    watcher._process_save_file(manual_file, manual_file.name)
    
    print("✅ File processing test completed!")
    print(f"🗂️ Output files saved in: {output_dir}")
    
    # List generated files
    output_files = list(output_dir.glob("*"))
    print(f"   Generated {len(output_files)} files:")
    for file in output_files:
        print(f"   - {file.name}")


def main():
    """Run all tests."""
    print("🧪 Startup Company AI Advisor - System Tests")
    print("=" * 50)
    
    try:
        test_dashboard_system()
        test_file_watcher()
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo start real-time monitoring:")
        print("python startup_monitor.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()