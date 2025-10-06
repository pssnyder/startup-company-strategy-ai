#!/usr/bin/env python3
"""
Comprehensive Trend Analysis for Momentum AI
Advanced temporal analysis using the historical database
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import sqlite3
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from strategic_advisor.temporal_database import TemporalGameDatabase

class MomentumAIAnalyzer:
    """Advanced trend analysis for Momentum AI company progression"""
    
    def __init__(self, db_path: str = "momentum_ai_historical.db"):
        self.db = TemporalGameDatabase(db_path)
    
    def analyze_growth_trajectory(self) -> Dict[str, Any]:
        """Analyze company growth patterns and key inflection points"""
        
        print("📈 Growth Trajectory Analysis")
        print("="*50)
        
        # Get complete timeline
        timeline = self.db.execute_read_query("""
            SELECT 
                game_date,
                game_day,
                balance,
                xp,
                research_points,
                real_timestamp,
                filename
            FROM save_files 
            ORDER BY game_day, real_timestamp
        """)
        
        if not timeline:
            print("❌ No timeline data available")
            return {}
        
        print(f"📊 Analyzing {len(timeline)} snapshots spanning {timeline[-1]['game_day'] - timeline[0]['game_day']} game days")
        
        # Growth phases analysis
        phases = []
        for i, snapshot in enumerate(timeline):
            if i == 0:
                phase = "🌱 Foundation"
            elif snapshot['balance'] < 100000:
                phase = "🏢 Early Growth"
            elif snapshot['balance'] < 500000:
                phase = "📈 Scaling"
            else:
                phase = "🚀 Expansion"
            
            phases.append({
                'snapshot': i + 1,
                'game_day': snapshot['game_day'],
                'phase': phase,
                'balance': snapshot['balance'],
                'xp': snapshot['xp'],
                'research': snapshot['research_points'],
                'date': snapshot['game_date']
            })
        
        # Financial growth rates
        growth_analysis = []
        for i in range(1, len(timeline)):
            prev = timeline[i-1]
            curr = timeline[i]
            
            day_diff = curr['game_day'] - prev['game_day']
            if day_diff > 0:
                balance_growth_rate = (curr['balance'] - prev['balance']) / day_diff
                xp_growth_rate = (curr['xp'] - prev['xp']) / day_diff
                
                growth_analysis.append({
                    'period': f"Day {prev['game_day']} → {curr['game_day']}",
                    'days': day_diff,
                    'balance_per_day': balance_growth_rate,
                    'xp_per_day': xp_growth_rate,
                    'total_balance_change': curr['balance'] - prev['balance'],
                    'total_xp_change': curr['xp'] - prev['xp']
                })
        
        # Display growth phases
        print(f"\n🎯 Company Evolution Phases:")
        for phase in phases:
            print(f"   {phase['phase']} - Day {phase['game_day']}")
            print(f"      💰 Balance: ${phase['balance']:,.2f}")
            print(f"      ⭐ XP: {phase['xp']:,.0f}")
            print(f"      🔬 Research: {phase['research']}")
            print()
        
        # Display growth rates
        print(f"📊 Growth Rate Analysis:")
        for period in growth_analysis:
            if period['days'] <= 30:  # Focus on shorter periods for clarity
                print(f"   {period['period']} ({period['days']} days)")
                print(f"      💰 ${period['balance_per_day']:,.2f}/day (Total: ${period['total_balance_change']:,.2f})")
                print(f"      ⭐ {period['xp_per_day']:,.0f} XP/day (Total: {period['total_xp_change']:,.0f})")
                print()
        
        return {
            'phases': phases,
            'growth_rates': growth_analysis,
            'total_snapshots': len(timeline),
            'total_game_days': timeline[-1]['game_day'] - timeline[0]['game_day']
        }
    
    def analyze_cash_flow_patterns(self) -> Dict[str, Any]:
        """Analyze transaction patterns and cash flow trends"""
        
        print("\n💳 Cash Flow Pattern Analysis")
        print("="*50)
        
        # Get transaction patterns by day
        daily_cash_flow = self.db.execute_read_query("""
            SELECT 
                day,
                COUNT(*) as transaction_count,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as daily_income,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as daily_expenses,
                SUM(amount) as net_cash_flow
            FROM transactions
            GROUP BY day
            ORDER BY day
        """)
        
        if daily_cash_flow:
            print(f"📊 Transaction data available for {len(daily_cash_flow)} days")
            
            # Calculate averages
            total_income = sum(day['daily_income'] for day in daily_cash_flow)
            total_expenses = abs(sum(day['daily_expenses'] for day in daily_cash_flow))
            total_net = sum(day['net_cash_flow'] for day in daily_cash_flow)
            avg_daily_income = total_income / len(daily_cash_flow)
            avg_daily_expenses = total_expenses / len(daily_cash_flow)
            
            print(f"💰 Total Income: ${total_income:,.2f}")
            print(f"💸 Total Expenses: ${total_expenses:,.2f}")
            print(f"📈 Net Cash Flow: ${total_net:,.2f}")
            print(f"📊 Average Daily Income: ${avg_daily_income:,.2f}")
            print(f"📊 Average Daily Expenses: ${avg_daily_expenses:,.2f}")
            
            # Find best and worst days
            best_income_day = max(daily_cash_flow, key=lambda x: x['daily_income'])
            worst_expense_day = min(daily_cash_flow, key=lambda x: x['daily_expenses'])
            best_net_day = max(daily_cash_flow, key=lambda x: x['net_cash_flow'])
            
            print(f"\n🏆 Best Income Day: Day {best_income_day['day']} (${best_income_day['daily_income']:,.2f})")
            print(f"💸 Highest Expense Day: Day {worst_expense_day['day']} (${abs(worst_expense_day['daily_expenses']):,.2f})")
            print(f"📈 Best Net Day: Day {best_net_day['day']} (${best_net_day['net_cash_flow']:,.2f})")
        
        # Analyze transaction types
        transaction_types = self.db.execute_read_query("""
            SELECT 
                description,
                COUNT(*) as frequency,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(day) as first_day,
                MAX(day) as last_day
            FROM transactions
            GROUP BY description
            ORDER BY total_amount DESC
            LIMIT 15
        """)
        
        if transaction_types:
            print(f"\n📋 Top Transaction Types:")
            for tx_type in transaction_types:
                print(f"   {tx_type['description']}")
                print(f"      🔢 Frequency: {tx_type['frequency']}")
                print(f"      💰 Total: ${tx_type['total_amount']:,.2f}")
                print(f"      📊 Average: ${tx_type['avg_amount']:,.2f}")
                print(f"      📅 Period: Day {tx_type['first_day']} → {tx_type['last_day']}")
                print()
        
        return {
            'daily_patterns': daily_cash_flow,
            'transaction_types': transaction_types,
            'totals': {
                'income': total_income if daily_cash_flow else 0,
                'expenses': total_expenses if daily_cash_flow else 0,
                'net': total_net if daily_cash_flow else 0
            }
        }
    
    def analyze_market_trends(self) -> Dict[str, Any]:
        """Analyze market component pricing trends"""
        
        print("\n📊 Market Trend Analysis")
        print("="*50)
        
        # Get component price trends
        price_trends = self.db.execute_read_query("""
            SELECT 
                component_name,
                COUNT(*) as data_points,
                AVG(base_price) as avg_price,
                MIN(base_price) as min_price,
                MAX(base_price) as max_price,
                AVG(price_change) as avg_change,
                MIN(game_day) as first_seen,
                MAX(game_day) as last_seen
            FROM market_values
            GROUP BY component_name
            ORDER BY avg_price DESC
            LIMIT 20
        """)
        
        if price_trends:
            print(f"📈 Tracking {len(price_trends)} components")
            
            print(f"\n💰 Most Valuable Components:")
            for component in price_trends[:10]:
                price_volatility = component['max_price'] - component['min_price']
                print(f"   {component['component_name']}")
                print(f"      💰 Avg Price: ${component['avg_price']:,.2f}")
                print(f"      📊 Range: ${component['min_price']:,.2f} - ${component['max_price']:,.2f}")
                print(f"      📈 Volatility: ${price_volatility:,.2f}")
                print(f"      📅 Tracked: Day {component['first_seen']} → {component['last_seen']}")
                print()
        
        return {
            'component_trends': price_trends
        }
    
    def analyze_social_engagement(self) -> Dict[str, Any]:
        """Analyze social media (Jeets) engagement patterns"""
        
        print("\n🐦 Social Engagement Analysis")
        print("="*50)
        
        # Jeet patterns by user
        user_engagement = self.db.execute_read_query("""
            SELECT 
                jeet_name,
                COUNT(*) as jeet_count,
                MIN(day) as first_jeet,
                MAX(day) as last_jeet,
                COUNT(DISTINCT day) as active_days
            FROM jeets
            GROUP BY jeet_name
            ORDER BY jeet_count DESC
        """)
        
        if user_engagement:
            print(f"👥 Social engagement from {len(user_engagement)} users")
            
            print(f"\n🏆 Most Active Users:")
            for user in user_engagement:
                engagement_span = user['last_jeet'] - user['first_jeet']
                print(f"   {user['jeet_name']}")
                print(f"      🐦 Total Jeets: {user['jeet_count']}")
                print(f"      📅 Active Days: {user['active_days']}")
                print(f"      📊 Engagement Span: {engagement_span} days")
                print()
        
        # Timeline of social activity
        jeet_timeline = self.db.execute_read_query("""
            SELECT 
                day,
                COUNT(*) as daily_jeets,
                COUNT(DISTINCT jeet_name) as unique_users
            FROM jeets
            GROUP BY day
            ORDER BY day
        """)
        
        if jeet_timeline:
            total_jeet_days = len(jeet_timeline)
            avg_daily_jeets = sum(day['daily_jeets'] for day in jeet_timeline) / total_jeet_days
            peak_day = max(jeet_timeline, key=lambda x: x['daily_jeets'])
            
            print(f"📊 Social Activity Timeline:")
            print(f"   📅 Active Days: {total_jeet_days}")
            print(f"   📊 Average Jeets/Day: {avg_daily_jeets:.1f}")
            print(f"   🏆 Peak Day: Day {peak_day['day']} ({peak_day['daily_jeets']} jeets)")
        
        return {
            'user_engagement': user_engagement,
            'timeline': jeet_timeline
        }
    
    def generate_strategic_insights(self) -> Dict[str, Any]:
        """Generate strategic insights from temporal analysis"""
        
        print("\n🎯 Strategic Insights")
        print("="*50)
        
        # Get latest company state
        latest_state = self.db.execute_read_query("""
            SELECT * FROM save_files
            ORDER BY game_day DESC, real_timestamp DESC
            LIMIT 1
        """)[0]
        
        # Calculate key performance indicators
        total_game_days = latest_state['game_day'] - 20360  # From first save
        daily_balance_growth = latest_state['balance'] / total_game_days
        daily_xp_growth = latest_state['xp'] / total_game_days
        
        print(f"🏢 Current Company Status:")
        print(f"   📅 Game Day: {latest_state['game_day']}")
        print(f"   💰 Balance: ${latest_state['balance']:,.2f}")
        print(f"   ⭐ XP: {latest_state['xp']:,.0f}")
        print(f"   🔬 Research Points: {latest_state['research_points']}")
        print()
        
        print(f"📊 Performance Metrics:")
        print(f"   📈 Daily Balance Growth: ${daily_balance_growth:,.2f}/day")
        print(f"   📈 Daily XP Growth: {daily_xp_growth:,.0f}/day")
        print(f"   🕐 Total Play Time: {total_game_days} game days")
        print()
        
        # Strategic recommendations
        recommendations = []
        
        if latest_state['balance'] > 500000:
            recommendations.append("💰 Strong financial position - consider major expansion")
        
        if latest_state['research_points'] > 1000:
            recommendations.append("🔬 High research capacity - invest in advanced technologies")
        
        if daily_xp_growth > 1000:
            recommendations.append("⭐ Excellent XP generation - maintain current strategy")
        
        print(f"🎯 Strategic Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
        
        return {
            'current_state': latest_state,
            'performance_metrics': {
                'daily_balance_growth': daily_balance_growth,
                'daily_xp_growth': daily_xp_growth,
                'total_days': total_game_days
            },
            'recommendations': recommendations
        }
    
    def run_comprehensive_analysis(self):
        """Run complete temporal analysis suite"""
        
        print("🚀 Momentum AI - Comprehensive Temporal Analysis")
        print("="*70)
        print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all analysis modules
        growth_analysis = self.analyze_growth_trajectory()
        cash_flow_analysis = self.analyze_cash_flow_patterns()
        market_analysis = self.analyze_market_trends()
        social_analysis = self.analyze_social_engagement()
        strategic_insights = self.generate_strategic_insights()
        
        print(f"\n✅ Comprehensive Analysis Complete!")
        print(f"📊 Database contains complete company timeline from foundation to current state")
        print(f"🎯 Ready for strategic decision making with full historical context")

if __name__ == "__main__":
    analyzer = MomentumAIAnalyzer()
    analyzer.run_comprehensive_analysis()