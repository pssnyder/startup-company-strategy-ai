#!/usr/bin/env python3
"""
Momentum AI Strategic Dashboard
Real-time company status with temporal context
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from strategic_advisor.temporal_database import TemporalGameDatabase

def generate_executive_summary():
    """Generate executive summary dashboard"""
    
    db = TemporalGameDatabase("momentum_ai_historical.db")
    
    print("🚀 MOMENTUM AI - EXECUTIVE DASHBOARD")
    print("="*70)
    print(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Current Status
    latest = db.execute_read_query("""
        SELECT * FROM save_files
        ORDER BY game_day DESC, real_timestamp DESC
        LIMIT 1
    """)[0]
    
    print("📊 CURRENT COMPANY STATUS")
    print("-" * 40)
    print(f"🏢 Company: {latest['company_name']}")
    print(f"📅 Game Date: {latest['game_date']}")
    print(f"📊 Game Day: {latest['game_day']:,}")
    print(f"💰 Current Balance: ${latest['balance']:,.2f}")
    print(f"⭐ Total XP: {latest['xp']:,.0f}")
    print(f"🔬 Research Points: {latest['research_points']:,}")
    print()
    
    # Historical Performance
    first = db.execute_read_query("""
        SELECT * FROM save_files
        ORDER BY game_day ASC, real_timestamp ASC
        LIMIT 1
    """)[0]
    
    total_days = latest['game_day'] - first['game_day']
    balance_growth = latest['balance'] - first['balance']
    xp_growth = latest['xp'] - first['xp']
    
    print("📈 HISTORICAL PERFORMANCE")
    print("-" * 40)
    print(f"🕐 Total Game Days Tracked: {total_days}")
    print(f"💰 Balance Growth: ${balance_growth:,.2f} (${balance_growth/total_days:,.2f}/day)")
    print(f"⭐ XP Growth: {xp_growth:,.0f} ({xp_growth/total_days:,.0f}/day)")
    print(f"🔬 Research Growth: {latest['research_points'] - first['research_points']} points")
    print()
    
    # Financial Summary
    cash_flow = db.execute_read_query("""
        SELECT 
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as total_expenses,
            SUM(amount) as net_cash_flow,
            COUNT(*) as total_transactions
        FROM transactions
    """)[0]
    
    print("💳 FINANCIAL SUMMARY")
    print("-" * 40)
    print(f"💰 Total Income: ${cash_flow['total_income']:,.2f}")
    print(f"💸 Total Expenses: ${abs(cash_flow['total_expenses']):,.2f}")
    print(f"📈 Net Cash Flow: ${cash_flow['net_cash_flow']:,.2f}")
    print(f"📊 Total Transactions: {cash_flow['total_transactions']:,}")
    print()
    
    # Recent Activity
    recent_transactions = db.execute_read_query("""
        SELECT day, SUM(amount) as daily_net
        FROM transactions
        WHERE day >= (SELECT MAX(day) - 7 FROM transactions)
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    """)
    
    if recent_transactions:
        print("📅 RECENT ACTIVITY (Last 7 Days)")
        print("-" * 40)
        for day_data in recent_transactions:
            status = "📈" if day_data['daily_net'] > 0 else "📉"
            print(f"   Day {day_data['day']}: {status} ${day_data['daily_net']:,.2f}")
        print()
    
    # Market Position
    market_components = db.execute_read_query("""
        SELECT COUNT(DISTINCT component_name) as component_count
        FROM market_values
    """)[0]
    
    social_engagement = db.execute_read_query("""
        SELECT 
            COUNT(*) as total_jeets,
            COUNT(DISTINCT jeet_name) as unique_users,
            MAX(day) as latest_jeet_day
        FROM jeets
    """)[0]
    
    print("🌐 MARKET POSITION")
    print("-" * 40)
    print(f"🏷️ Market Components Tracked: {market_components['component_count']}")
    print(f"🐦 Social Engagement: {social_engagement['total_jeets']} jeets from {social_engagement['unique_users']} users")
    print(f"📱 Latest Social Activity: Day {social_engagement['latest_jeet_day']}")
    print()
    
    # Strategic Alerts
    print("🚨 STRATEGIC ALERTS")
    print("-" * 40)
    
    alerts = []
    
    # Cash flow analysis
    if cash_flow['net_cash_flow'] < 0:
        alerts.append("⚠️ Negative overall cash flow - review spending")
    elif latest['balance'] > 1000000:
        alerts.append("💰 Excellent financial position - consider major expansion")
    
    # Research analysis
    if latest['research_points'] > 1500:
        alerts.append("🔬 High research capacity - invest in advanced technologies")
    elif latest['research_points'] < 100:
        alerts.append("⚠️ Low research points - focus on research generation")
    
    # Growth analysis
    recent_growth = (latest['balance'] - first['balance']) / total_days
    if recent_growth > 5000:
        alerts.append("🚀 Excellent growth trajectory - maintain current strategy")
    elif recent_growth < 1000:
        alerts.append("📉 Slow growth - consider strategy optimization")
    
    if not alerts:
        alerts.append("✅ All systems operating within normal parameters")
    
    for alert in alerts:
        print(f"   {alert}")
    print()
    
    # Data Quality Report
    save_count = db.execute_read_query("SELECT COUNT(*) as count FROM save_files")[0]['count']
    transaction_count = cash_flow['total_transactions']
    jeet_count = social_engagement['total_jeets']
    market_count = db.execute_read_query("SELECT COUNT(*) as count FROM market_values")[0]['count']
    
    print("📊 DATA QUALITY REPORT")
    print("-" * 40)
    print(f"💾 Save Files: {save_count} snapshots")
    print(f"💳 Transactions: {transaction_count:,} records")
    print(f"🐦 Social Data: {jeet_count} jeets")
    print(f"📈 Market Data: {market_count:,} price points")
    print(f"🗄️ Database: momentum_ai_historical.db")
    print()
    
    print("🎯 SYSTEM STATUS: ✅ OPERATIONAL")
    print("📊 Historical data complete and ready for strategic analysis")
    print("🚀 Momentum AI temporal tracking system fully operational!")

if __name__ == "__main__":
    generate_executive_summary()