"""
Strategic Advisor - Real Save File Test
Process actual game save data and show detailed analysis
"""

import json
import sys
from pathlib import Path

# Add strategic_advisor to path
sys.path.append(str(Path(__file__).parent))

from strategic_advisor.main import StrategicAdvisor
from strategic_advisor.logger_config import setup_logging

def process_real_save():
    """Process the real save file and show analysis"""
    
    print("🎮 Processing Real Game Save File")
    print("=" * 60)
    
    # Initialize system
    advisor = StrategicAdvisor(database_path="real_game_analysis.db")
    
    # Find the current save file
    save_files = list(Path("strategic_advisor/save_files").glob("*_sg_momentum_ai.json"))
    if not save_files:
        print("❌ No save files found!")
        return
    
    # Get the newest file
    current_save = max(save_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Processing: {current_save.name}")
    
    # Load and examine the save file structure
    with open(current_save, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    print(f"💾 Save file size: {current_save.stat().st_size / 1024:.1f} KB")
    print(f"📊 Top-level keys: {len(save_data.keys())}")
    print()
    
    # Show key game metrics from raw data
    print("🎯 Raw Game Metrics:")
    print("-" * 30)
    print(f"Game Date: {save_data.get('date', 'Unknown')}")
    print(f"Company: {save_data.get('companyName', 'Unknown')}")
    print(f"Balance: ${save_data.get('balance', 0):,}")
    
    employees = save_data.get('employeesOrder', [])
    print(f"Team Size: {len(employees)} employees")
    
    inventory = save_data.get('inventory', {})
    print(f"Inventory Items: {len(inventory)} types")
    
    transactions = save_data.get('transactions', [])
    print(f"Transaction History: {len(transactions)} records")
    
    research_points = save_data.get('researchPoints', 0)
    print(f"Research Points: {research_points}")
    
    office = save_data.get('office', {})
    workstations = office.get('workstations', []) if office else []
    print(f"Office Workstations: {len(workstations)}")
    print()
    
    # Process through our strategic advisor
    print("🔧 Processing through Strategic Advisor...")
    advisor.process_save_file(str(current_save))
    
    # Get dashboard analysis
    dashboard_data = advisor.get_dashboard_data()
    
    print("\n📈 Strategic Analysis Results:")
    print("=" * 40)
    
    # Company info
    company_info = dashboard_data.get('company_info', {})
    print(f"📊 Company: {company_info.get('name', 'Unknown')}")
    print(f"🕐 Last Updated: {company_info.get('last_save_time', 'Unknown')}")
    print()
    
    # Capacity metrics
    capacity = dashboard_data.get('capacity_metrics', {})
    if capacity:
        print("⚡ Capacity Analysis:")
        print(f"   Overall Utilization: {capacity.get('overall_utilization', 0):.1f}%")
        print(f"   Active Employees: {capacity.get('active_employees', 0)}")
        print(f"   Available Capacity: {capacity.get('available_capacity', 0)}")
        print(f"   Capacity Gap: {capacity.get('capacity_shortage', 0)}")
        print()
    
    # Alerts
    alerts = dashboard_data.get('alerts', [])
    if alerts:
        print("🚨 Active Alerts:")
        for alert in alerts[:5]:  # Show first 5
            priority = alert.get('priority', 'INFO')
            message = alert.get('message', 'No message')
            print(f"   [{priority}] {message}")
        if len(alerts) > 5:
            print(f"   ... and {len(alerts) - 5} more alerts")
        print()
    
    # Show database contents
    print("🗄️ Database Analysis:")
    print("-" * 25)
    
    # Count records in each table
    conn = advisor.database._get_connection(read_only=True)
    cursor = conn.cursor()
    
    tables = ['save_snapshots', 'employees', 'inventory_items', 'transactions', 'research_items']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        except Exception as e:
            print(f"   {table}: Error - {e}")
    
    conn.close()
    print()
    
    print("✅ Real save file processing complete!")
    print(f"📄 Full dashboard data available with {len(dashboard_data)} sections")
    
    return dashboard_data

def examine_save_structure():
    """Examine the structure of the save file in detail"""
    
    save_files = list(Path("strategic_advisor/save_files").glob("*_sg_momentum_ai.json"))
    if not save_files:
        print("❌ No save files found!")
        return
    
    current_save = max(save_files, key=lambda f: f.stat().st_mtime)
    
    with open(current_save, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    print("\n🔍 Save File Structure Analysis:")
    print("=" * 40)
    
    def analyze_structure(data, prefix="", max_depth=3, current_depth=0):
        """Recursively analyze data structure"""
        if current_depth >= max_depth:
            return
            
        if isinstance(data, dict):
            for key, value in list(data.items())[:10]:  # Limit to first 10 items
                value_type = type(value).__name__
                if isinstance(value, (list, dict)):
                    size = len(value)
                    print(f"{prefix}{key}: {value_type}({size})")
                    if current_depth < max_depth - 1:
                        analyze_structure(value, prefix + "  ", max_depth, current_depth + 1)
                else:
                    sample = str(value)[:50] if value is not None else "None"
                    print(f"{prefix}{key}: {value_type} = {sample}")
        elif isinstance(data, list) and data:
            print(f"{prefix}[{len(data)} items] Sample:")
            analyze_structure(data[0], prefix + "  ", max_depth, current_depth + 1)
    
    analyze_structure(save_data)

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    # Process real save file
    dashboard_data = process_real_save()
    
    # Examine structure
    examine_save_structure()
    
    print("\n🎯 Analysis complete! Ready for historical backfill.")