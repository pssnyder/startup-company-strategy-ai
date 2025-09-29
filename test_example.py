"""
Example Usage and Test Script for the AI Advisor

This script demonstrates how to use the Startup Company AI Advisor
and provides test cases with mock data.
"""

import asyncio
import json
from pathlib import Path

# Import the AI advisor modules
from ai_advisor.main import StartupCompanyAdvisor
from ai_advisor.data_layer import GameDataManager
from ai_advisor.input_layer import SaveFileParser


def create_test_save_file(output_path: Path):
    """Create a test save file with realistic game data."""
    test_save_data = {
        "balance": 45000.0,
        "date": "2023-03-15T10:30:00Z",
        "started": "2023-01-01T00:00:00Z",
        "companyName": "RTS Technology & Solutions LLC",
        "progress": {
            "products": [
                {
                    "users": {
                        "total": 15000,
                        "satisfaction": 42.5  # Critical satisfaction level
                    }
                }
            ]
        },
        "featureInstances": [
            {
                "featureName": "Landing Page",
                "quality": {
                    "current": 20,
                    "max": 100
                },
                "efficiency": {
                    "current": 25,
                    "max": 100
                },
                "level": 5
            },
            {
                "featureName": "Login System",
                "quality": {
                    "current": 0,
                    "max": 50
                },
                "efficiency": {
                    "current": 0,
                    "max": 50
                },
                "level": 1
            }
        ],
        "office": {
            "workstations": [
                {
                    "employee": {
                        "name": "Alice Johnson",
                        "type": "Developer",
                        "level": "Intermediate",
                        "salary": 5500.0,
                        "productivity": 85.0,
                        "mood": 65.0,
                        "currentTask": "Backend Component"
                    }
                },
                {
                    "employee": {
                        "name": "Bob Smith",
                        "type": "Designer",
                        "level": "Beginner",
                        "salary": 4200.0,
                        "productivity": 90.0,
                        "mood": 80.0,
                        "currentTask": "Graphics Component"
                    }
                },
                {
                    "employee": {
                        "name": "Carol Davis",
                        "type": "Lead Developer",
                        "level": "Expert",
                        "salary": 11000.0,
                        "productivity": 95.0,
                        "mood": 70.0,
                        "currentTask": "Frontend Module"
                    }
                }
            ]
        },
        "inventory": {
            "UI Component": 2,
            "Backend Component": 1,
            "Blueprint Component": 0,
            "Graphics Component": 1,
            "Frontend Module": 0,
            "Backend Module": 1
        },
        "transactions": [
            {"date": "2023-03-14", "amount": -20700.0, "description": "Monthly salaries"},
            {"date": "2023-03-13", "amount": 5000.0, "description": "Ad revenue"},
            {"date": "2023-03-12", "amount": -3000.0, "description": "Office rent"}
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_save_data, f, indent=2)
    
    print(f"✅ Test save file created: {output_path}")


async def run_example_analysis():
    """Run a complete analysis example."""
    print("🚀 Starting Startup Company AI Advisor Example")
    print("="*60)
    
    # Create test data directory and file
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    test_save_file = test_dir / "example_save.json"
    
    # Create test save file
    create_test_save_file(test_save_file)
    
    # Initialize the AI advisor (without Gemini API key for this example)
    advisor = StartupCompanyAdvisor(gemini_api_key=None)
    
    # Load the test save file
    print("\n📁 Loading save file...")
    if not advisor.load_save_file(test_save_file):
        print("❌ Failed to load save file")
        return
    
    # Analyze the game state
    print("\n🔬 Performing analysis...")
    analysis_result = await advisor.analyze_game_state()
    
    # Print the comprehensive report
    advisor.print_summary_report()
    
    # Export analysis to JSON
    output_file = test_dir / "analysis_report.json"
    advisor.export_analysis_json(output_file)
    
    # Demonstrate dashboard data access
    print("\n📊 Dashboard Data Preview:")
    dashboard_data = advisor.get_dashboard_data()
    
    print(f"Risk Level: {dashboard_data['financial_metrics']['risk_level']}")
    print(f"Critical Alerts: {len([a for a in dashboard_data['alerts'] if a['severity'] == 'CRITICAL'])}")
    print(f"Recommendations: {len(dashboard_data['recommendations'])}")
    print(f"Production Tasks: {len(dashboard_data['production_plan'])}")
    
    print("\n✅ Example analysis completed!")
    return advisor


def demo_individual_modules():
    """Demonstrate individual module capabilities."""
    print("\n🧪 TESTING INDIVIDUAL MODULES")
    print("="*40)
    
    # Test Data Layer
    print("\n1. Testing Data Layer...")
    game_data = GameDataManager()
    print(f"   Loaded {len(game_data.features)} features")
    print(f"   Loaded {len(game_data.employees)} employee types")
    
    landing_page_reqs = game_data.get_feature_requirements("Landing Page")
    print(f"   Landing Page requires {len(landing_page_reqs)} components")
    
    # Test Input Layer
    print("\n2. Testing Input Layer...")
    parser = SaveFileParser()
    test_save_file = Path("test_data/example_save.json")
    
    if test_save_file.exists():
        success = parser.load_save_file(test_save_file)
        if success and parser.metrics:
            print(f"   ✅ Parsed save file successfully")
            print(f"   Cash: ${parser.metrics.cash_on_hand:,.0f}")
            print(f"   Satisfaction: {parser.metrics.user_satisfaction:.1f}%")
            print(f"   Features loaded: {len(parser.features)}")
            print(f"   Employees loaded: {len(parser.employees)}")
            print(f"   Inventory items: {len(parser.inventory)}")
            
            # Test critical checks
            print(f"   Critical satisfaction? {parser.is_critical_satisfaction()}")
            print(f"   Low runway? {parser.is_low_runway()}")
        else:
            print("   ❌ Failed to parse save file")
    else:
        print("   ⏭️  No test save file available")


def print_usage_instructions():
    """Print instructions for using the AI advisor."""
    print("\n📖 USAGE INSTRUCTIONS")
    print("="*40)
    print("""
To use the Startup Company AI Advisor:

1. BASIC USAGE:
   from ai_advisor.main import StartupCompanyAdvisor
   
   advisor = StartupCompanyAdvisor()
   advisor.load_save_file(Path("your_save.json"))
   await advisor.analyze_game_state()
   advisor.print_summary_report()

2. WITH GEMINI AI:
   advisor = StartupCompanyAdvisor(gemini_api_key="your_api_key")
   # ... rest same as above

3. EXPORT RESULTS:
   advisor.export_analysis_json(Path("analysis.json"))
   dashboard_data = advisor.get_dashboard_data()

4. SAVE FILE LOCATION:
   Startup Company saves are typically found in:
   - Windows: %APPDATA%/Startup Company/saves/
   - Look for files named: sg_*.json

5. REQUIRED PYTHON PACKAGES:
   - aiohttp (for Gemini API)
   - Standard library only for basic functionality
    """)


async def main():
    """Main example runner."""
    try:
        # Run the main example
        advisor = await run_example_analysis()
        
        # Test individual modules
        demo_individual_modules()
        
        # Show usage instructions
        print_usage_instructions()
        
        print(f"\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())