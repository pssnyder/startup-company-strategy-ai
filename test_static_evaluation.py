"""
Test script to demonstrate the static evaluation engine in action
Shows the data-driven approach with real game scenarios
"""

import json
import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from live_analytics.utilities.static_evaluation_engine import run_static_evaluation

def test_scenario_1_overloaded_team():
    """Test scenario: Team is overloaded and satisfaction is low"""
    print("=" * 60)
    print("SCENARIO 1: Overloaded Team with Low Satisfaction")
    print("=" * 60)
    
    game_data = {
        'cash': 75000,
        'users': 5000,
        'satisfaction': 45,  # Below 60% threshold
        'cu': {'current': 950, 'max': 1000},  # High CU usage
        'inventory': {
            'UIComponent': {'amount': 2},
            'NetworkComponent': {'amount': 1}
        },
        'office': {
            'workstations': [
                {
                    'employee': {
                        'name': 'John Smith',
                        'employeeTypeName': 'Developer',
                        'salary': 5000,
                        'currentAssignment': 'UIComponent'
                    }
                },
                {
                    'employee': {
                        'name': 'Jane Doe',
                        'employeeTypeName': 'Developer',
                        'salary': 5500,
                        'currentAssignment': 'NetworkModule'
                    }
                }
            ]
        }
    }
    
    result = run_static_evaluation(game_data)
    
    print(f"📊 EVALUATION SUMMARY:")
    print(f"   Status: {result['evaluation_summary']['evaluation_status']}")
    print(f"   Total Alerts: {result['evaluation_summary']['total_threshold_alerts']}")
    print(f"   Actions Required: {len(result['actionable_outputs'])}")
    
    print(f"\n🚨 THRESHOLD VIOLATIONS:")
    for category, alerts in result['threshold_analysis'].items():
        for alert in alerts:
            print(f"   • {alert['metric']}: {alert['current_value']} (threshold: {alert['threshold']})")
    
    print(f"\n🎮 GAME ACTIONS REQUIRED:")
    for i, action in enumerate(result['actionable_outputs'], 1):
        print(f"   {i}. {action['game_command']}")
        print(f"      Priority: {action['priority']}")
        print(f"      Action: {action['specific_action']}")
        print(f"      Expected: {action['implementation']['expected_result']}")
        print()

def test_scenario_2_optimal_operations():
    """Test scenario: Everything running optimally"""
    print("=" * 60)
    print("SCENARIO 2: Optimal Operations")
    print("=" * 60)
    
    game_data = {
        'cash': 150000,
        'users': 15000,
        'satisfaction': 85,  # Above 80% threshold
        'cu': {'current': 600, 'max': 1000},  # Good CU usage
        'inventory': {
            'UIComponent': {'amount': 20},
            'NetworkComponent': {'amount': 15},
            'DatabaseModule': {'amount': 10}
        },
        'office': {
            'workstations': [
                {
                    'employee': {
                        'name': 'John Smith',
                        'employeeTypeName': 'Developer',
                        'salary': 5000,
                        'currentAssignment': 'UIComponent'
                    }
                },
                {
                    'employee': {
                        'name': 'Jane Doe',
                        'employeeTypeName': 'Developer',
                        'salary': 5500,
                        'currentAssignment': None  # Available capacity
                    }
                },
                {
                    'employee': {
                        'name': 'Bob Wilson',
                        'employeeTypeName': 'Designer',
                        'salary': 4800,
                        'currentAssignment': 'UIDesign'
                    }
                }
            ]
        }
    }
    
    result = run_static_evaluation(game_data)
    
    print(f"📊 EVALUATION SUMMARY:")
    print(f"   Status: {result['evaluation_summary']['evaluation_status']}")
    print(f"   Total Alerts: {result['evaluation_summary']['total_threshold_alerts']}")
    print(f"   Actions Required: {len(result['actionable_outputs'])}")
    
    if result['evaluation_summary']['total_threshold_alerts'] == 0:
        print("\n✅ ALL SYSTEMS OPTIMAL")
        print("   No threshold violations detected")
        print("   No immediate actions required")
    else:
        print(f"\n⚠️ MINOR OPTIMIZATIONS AVAILABLE:")
        for action in result['actionable_outputs']:
            print(f"   • {action['specific_action']} (Priority: {action['priority']})")

def test_scenario_3_financial_crisis():
    """Test scenario: Running out of money"""
    print("=" * 60)
    print("SCENARIO 3: Financial Crisis")
    print("=" * 60)
    
    game_data = {
        'cash': 8000,  # Very low cash
        'users': 2000,
        'satisfaction': 65,
        'cu': {'current': 400, 'max': 1000},
        'inventory': {
            'UIComponent': {'amount': 1}
        },
        'office': {
            'workstations': [
                {
                    'employee': {
                        'name': 'John Smith',
                        'employeeTypeName': 'Developer',
                        'salary': 5000,
                        'currentAssignment': 'UIComponent'
                    }
                },
                {
                    'employee': {
                        'name': 'Jane Doe',
                        'employeeTypeName': 'Designer',
                        'salary': 4500,
                        'currentAssignment': 'UIDesign'
                    }
                }
            ]
        }
    }
    
    result = run_static_evaluation(game_data)
    
    # Calculate runway manually for verification
    monthly_burn = 5000 + 4500 + 200  # salaries + office costs
    daily_burn = monthly_burn / 30
    runway_days = 8000 / daily_burn
    
    print(f"📊 FINANCIAL ANALYSIS:")
    print(f"   Current Cash: ${game_data['cash']:,}")
    print(f"   Calculated Runway: {runway_days:.1f} days")
    print(f"   Daily Burn Rate: ${daily_burn:.2f}")
    
    print(f"\n🚨 CRITICAL ALERTS:")
    financial_alerts = result['threshold_analysis']['financial_analysis']
    for alert in financial_alerts:
        print(f"   • {alert['trigger_condition']}")
        print(f"     Severity: {alert['severity']}")
    
    print(f"\n🎮 EMERGENCY ACTIONS:")
    for action in result['actionable_outputs']:
        if action['priority'] == 'CRITICAL':
            print(f"   🔴 {action['game_command']}")
            print(f"      {action['specific_action']}")

def demonstrate_data_pipeline():
    """Show the complete data pipeline in action"""
    print("\n" + "=" * 80)
    print("PROJECT PHOENIX: STATIC EVALUATION ENGINE DEMONSTRATION")
    print("Data-Driven Business Intelligence Pipeline")
    print("=" * 80)
    
    print("\n🔄 PIPELINE ARCHITECTURE:")
    print("   Raw Game Data → Metric Calculations → Threshold Analysis → Game Actions")
    print()
    
    # Run all test scenarios
    test_scenario_1_overloaded_team()
    test_scenario_2_optimal_operations()
    test_scenario_3_financial_crisis()
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\n📈 KEY INSIGHTS:")
    print("   • Static evaluation engine converts raw data into actionable decisions")
    print("   • Threshold-based analysis eliminates subjective recommendations")
    print("   • Every action includes specific game commands and expected results")
    print("   • System scales from optimal operations to crisis management")
    print("   • Pipeline ready for neural network training data generation")
    print("\n🎯 NEXT STEPS:")
    print("   • Collect historical game data for pattern analysis")
    print("   • Build ML models using static evaluation as ground truth")
    print("   • Develop hyperstrategy optimization beyond static thresholds")

if __name__ == "__main__":
    demonstrate_data_pipeline()