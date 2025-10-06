#!/usr/bin/env python3
"""
Interactive Database Explorer for Momentum AI
SQL query interface with relationship exploration
"""

import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
import json

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

class DatabaseExplorer:
    """Interactive database exploration tool"""
    
    def __init__(self, db_path: str = "momentum_ai_historical.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SQL query and return results"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            
            return results
        except Exception as e:
            print(f"❌ Query error: {str(e)}")
            return []
    
    def show_table_relationships(self):
        """Show comprehensive table relationship analysis"""
        print("🔗 DATABASE RELATIONSHIP ANALYSIS")
        print("="*60)
        
        # Central hub analysis
        save_files_count = self.execute_query("SELECT COUNT(*) as count FROM save_files")[0]['count']
        print(f"🏛️ CENTRAL HUB: save_files ({save_files_count} snapshots)")
        print()
        
        # Related table analysis
        related_tables = [
            ('transactions', 'Financial activity'),
            ('employees', 'Workforce management'),
            ('jeets', 'Social engagement'),
            ('market_values', 'Market intelligence'),
            ('employee_references', 'Employee tracking')
        ]
        
        for table, description in related_tables:
            try:
                count = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")[0]['count']
                avg_per_save = count / save_files_count if save_files_count > 0 else 0
                
                print(f"📊 {table.upper()}")
                print(f"   📝 {description}")
                print(f"   📊 Total records: {count:,}")
                print(f"   📈 Average per save: {avg_per_save:.1f}")
                
                # Show latest activity
                if table in ['transactions', 'jeets', 'market_values']:
                    latest = self.execute_query(
                        f"SELECT MAX(day) as latest_day FROM {table} WHERE day IS NOT NULL"
                    )[0]
                    if latest['latest_day']:
                        print(f"   📅 Latest activity: Day {latest['latest_day']}")
                
                print()
            except:
                print(f"   ❌ Unable to analyze {table}")
                print()
    
    def analyze_temporal_relationships(self):
        """Analyze time-based relationships between tables"""
        print("⏰ TEMPORAL RELATIONSHIP ANALYSIS")
        print("="*60)
        
        # Game day progression
        game_day_range = self.execute_query("""
            SELECT 
                MIN(game_day) as min_day,
                MAX(game_day) as max_day,
                COUNT(DISTINCT game_day) as unique_days
            FROM save_files
        """)[0]
        
        print(f"🎮 GAME PROGRESSION")
        print(f"   📅 Day range: {game_day_range['min_day']} → {game_day_range['max_day']}")
        print(f"   📊 Total span: {game_day_range['max_day'] - game_day_range['min_day']} days")
        print(f"   💾 Snapshots: {game_day_range['unique_days']} unique days")
        print()
        
        # Transaction activity by time period
        transaction_periods = self.execute_query("""
            SELECT 
                CASE 
                    WHEN day < 50 THEN 'Early (Days 1-49)'
                    WHEN day < 100 THEN 'Growth (Days 50-99)'
                    WHEN day < 150 THEN 'Expansion (Days 100-149)'
                    ELSE 'Mature (Days 150+)'
                END as period,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                MIN(day) as period_start,
                MAX(day) as period_end
            FROM transactions
            GROUP BY 
                CASE 
                    WHEN day < 50 THEN 'Early (Days 1-49)'
                    WHEN day < 100 THEN 'Growth (Days 50-99)'
                    WHEN day < 150 THEN 'Expansion (Days 100-149)'
                    ELSE 'Mature (Days 150+)'
                END
            ORDER BY period_start
        """)
        
        print(f"💳 FINANCIAL ACTIVITY BY PERIOD")
        for period in transaction_periods:
            print(f"   {period['period']}")
            print(f"      📊 Transactions: {period['transaction_count']:,}")
            print(f"      💰 Total value: ${period['total_amount']:,.2f}")
            print(f"      📅 Days: {period['period_start']} → {period['period_end']}")
            print()
    
    def show_data_quality_metrics(self):
        """Show data quality and completeness metrics"""
        print("📊 DATA QUALITY METRICS")
        print("="*60)
        
        # Save file completeness
        save_completeness = self.execute_query("""
            SELECT 
                COUNT(*) as total_saves,
                COUNT(balance) as has_balance,
                COUNT(xp) as has_xp,
                COUNT(research_points) as has_research,
                COUNT(raw_json) as has_raw_json
            FROM save_files
        """)[0]
        
        print(f"💾 SAVE FILE COMPLETENESS")
        print(f"   📊 Total saves: {save_completeness['total_saves']}")
        print(f"   💰 Balance data: {save_completeness['has_balance']}/{save_completeness['total_saves']}")
        print(f"   ⭐ XP data: {save_completeness['has_xp']}/{save_completeness['total_saves']}")
        print(f"   🔬 Research data: {save_completeness['has_research']}/{save_completeness['total_saves']}")
        print(f"   📄 Raw JSON: {save_completeness['has_raw_json']}/{save_completeness['total_saves']}")
        print()
        
        # Transaction data quality
        transaction_quality = self.execute_query("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT transaction_id) as unique_transactions,
                COUNT(amount) as has_amount,
                COUNT(balance) as has_balance,
                MIN(day) as earliest_day,
                MAX(day) as latest_day
            FROM transactions
        """)[0]
        
        print(f"💳 TRANSACTION DATA QUALITY")
        print(f"   📊 Total records: {transaction_quality['total_transactions']:,}")
        print(f"   🔄 Unique transactions: {transaction_quality['unique_transactions']:,}")
        print(f"   💰 Amount data: {transaction_quality['has_amount']}/{transaction_quality['total_transactions']}")
        print(f"   📈 Balance data: {transaction_quality['has_balance']}/{transaction_quality['total_transactions']}")
        print(f"   📅 Time span: Day {transaction_quality['earliest_day']} → {transaction_quality['latest_day']}")
        print()
    
    def run_sample_queries(self):
        """Run sample analytical queries"""
        print("🔍 SAMPLE ANALYTICAL QUERIES")
        print("="*60)
        
        # Company growth analysis
        print("📈 COMPANY GROWTH TRAJECTORY")
        growth_data = self.execute_query("""
            SELECT 
                game_day,
                balance,
                xp,
                research_points,
                LAG(balance) OVER (ORDER BY game_day) as prev_balance,
                LAG(xp) OVER (ORDER BY game_day) as prev_xp
            FROM save_files
            ORDER BY game_day
        """)
        
        for i, row in enumerate(growth_data):
            if i == 0:
                print(f"   Day {row['game_day']}: ${row['balance']:,.2f} | {row['xp']:,.0f} XP | {row['research_points']} RP (Starting point)")
            else:
                balance_change = row['balance'] - (row['prev_balance'] or 0)
                xp_change = row['xp'] - (row['prev_xp'] or 0)
                print(f"   Day {row['game_day']}: ${row['balance']:,.2f} | {row['xp']:,.0f} XP | {row['research_points']} RP")
                print(f"      📈 Change: ${balance_change:+,.2f} | {xp_change:+,.0f} XP")
        print()
        
        # Top transaction days
        print("💰 TOP FINANCIAL ACTIVITY DAYS")
        top_days = self.execute_query("""
            SELECT 
                day,
                COUNT(*) as transaction_count,
                SUM(amount) as daily_total,
                MAX(balance) as end_balance
            FROM transactions
            GROUP BY day
            ORDER BY ABS(daily_total) DESC
            LIMIT 5
        """)
        
        for day in top_days:
            print(f"   Day {day['day']}: {day['transaction_count']} transactions | ${day['daily_total']:+,.2f} | End: ${day['end_balance']:,.2f}")
        print()
        
        # Market component analysis
        print("📊 MARKET COMPONENT INSIGHTS")
        market_insights = self.execute_query("""
            SELECT 
                component_name,
                COUNT(*) as price_points,
                AVG(base_price) as avg_price,
                MIN(base_price) as min_price,
                MAX(base_price) as max_price
            FROM market_values
            GROUP BY component_name
            ORDER BY avg_price DESC
            LIMIT 5
        """)
        
        for component in market_insights:
            volatility = component['max_price'] - component['min_price']
            print(f"   {component['component_name']}: ${component['avg_price']:,.2f} avg | Volatility: ${volatility}")
        print()
    
    def close(self):
        """Close database connection"""
        self.connection.close()

def main():
    """Main exploration interface"""
    print("🗄️ Momentum AI Database Explorer")
    print("="*70)
    print("Comprehensive database analysis and relationship exploration")
    print()
    
    try:
        explorer = DatabaseExplorer()
        
        # Run all analysis modules
        explorer.show_table_relationships()
        print("\n" + "="*70 + "\n")
        
        explorer.analyze_temporal_relationships()
        print("\n" + "="*70 + "\n")
        
        explorer.show_data_quality_metrics()
        print("\n" + "="*70 + "\n")
        
        explorer.run_sample_queries()
        
        print("✅ Database exploration complete!")
        print("🔍 Use the generated ER diagrams for visual relationship analysis")
        print("📊 Database ready for advanced strategic analysis")
        
        explorer.close()
        
    except Exception as e:
        print(f"❌ Error during exploration: {str(e)}")

if __name__ == "__main__":
    main()