"""
Main AI Advisor Module

This module coordinates all layers to provide complete strategic analysis
for Startup Company game saves.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from .data_layer import GameDataManager
from .input_layer import SaveFileParser
from .calculation_layer import GameStateAnalyzer
from .strategy_layer import GeminiStrategyAdvisor, AIInsight


class StartupCompanyAdvisor:
    """Main AI advisor for Startup Company strategic analysis."""
    
    def __init__(self, gemini_api_key: Optional[str] = None, data_file_path: Optional[Path] = None):
        """Initialize the AI advisor with all layers."""
        self.game_data = GameDataManager(data_file_path)
        self.save_parser = SaveFileParser()
        self.analyzer = GameStateAnalyzer(self.game_data, self.save_parser)
        self.ai_advisor = GeminiStrategyAdvisor(gemini_api_key)
        
        self.current_analysis: Optional[Dict[str, Any]] = None
        self.current_strategy: Optional[AIInsight] = None
    
    def load_save_file(self, save_file_path: Path) -> bool:
        """Load and analyze a game save file."""
        success = self.save_parser.load_save_file(save_file_path)
        if success and self.save_parser.metrics:
            metrics = self.save_parser.metrics
            print(f"✅ Successfully loaded save file: {save_file_path.name}")
            print(f"Company: {metrics.company_name}")
            print(f"Game Date: {metrics.game_date}")
            print(f"Cash: ${metrics.cash_on_hand:,.0f}")
            print(f"Users: {metrics.total_users:,}")
            print(f"Satisfaction: {metrics.user_satisfaction:.1f}%")
        return success
    
    async def analyze_game_state(self) -> Dict[str, Any]:
        """Perform complete analysis of the current game state."""
        if not self.save_parser.metrics:
            raise ValueError("No save file loaded. Call load_save_file() first.")
        
        print("🔍 Analyzing game state...")
        self.current_analysis = self.analyzer.analyze()
        
        print("🤖 Generating AI strategy...")
        self.current_strategy = await self.ai_advisor.generate_strategy(self.analyzer)
        
        return {
            "analysis": self.current_analysis,
            "strategy": self.current_strategy
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        if not self.current_analysis or not self.current_strategy:
            return {"error": "No analysis available. Run analyze_game_state() first."}
        
        metrics = self.save_parser.metrics
        if not metrics:
            return {"error": "No metrics available from save file."}
        
        analysis = self.current_analysis
        strategy = self.current_strategy
        
        return {
            "company_info": {
                "name": metrics.company_name,
                "date": metrics.game_date,
                "cash": metrics.cash_on_hand,
                "users": metrics.total_users,
                "satisfaction": metrics.user_satisfaction,
                "employees": metrics.total_employees
            },
            "financial_metrics": {
                "cash_on_hand": metrics.cash_on_hand,
                "monthly_burn_rate": metrics.monthly_burn_rate,
                "runway_months": metrics.runway_months,
                "risk_level": strategy.risk_level
            },
            "alerts": [
                {
                    "severity": alert.severity,
                    "title": alert.title,
                    "description": alert.description,
                    "action": alert.recommended_action
                }
                for alert in analysis["alerts"]
            ],
            "recommendations": [
                {
                    "priority": rec.priority,
                    "type": rec.action_type,
                    "title": rec.title,
                    "description": rec.description,
                    "outcome": rec.expected_outcome,
                    "timeframe": rec.time_frame,
                    "resources": rec.resources_needed
                }
                for rec in strategy.key_recommendations
            ],
            "production_plan": [
                {
                    "priority": plan.priority,
                    "component": plan.component_name,
                    "quantity": plan.quantity_to_produce,
                    "employee_type": plan.employee_type,
                    "hours": plan.estimated_hours,
                    "reason": plan.reason
                }
                for plan in analysis["production_plan"]
            ],
            "ai_insights": {
                "overall_assessment": strategy.overall_assessment,
                "financial_advice": strategy.financial_advice,
                "production_priorities": strategy.production_priorities,
                "next_steps": strategy.next_steps
            }
        }
    
    def print_summary_report(self):
        """Print a formatted summary report to console."""
        if not self.current_analysis or not self.current_strategy:
            print("❌ No analysis available. Run analyze_game_state() first.")
            return
        
        metrics = self.save_parser.metrics
        if not metrics:
            print("❌ No metrics available from save file.")
            return
            
        analysis = self.current_analysis
        strategy = self.current_strategy
        
        print("\n" + "="*60)
        print(f"🏢 STARTUP COMPANY AI ADVISOR REPORT")
        print("="*60)
        
        print(f"\n📊 COMPANY OVERVIEW:")
        print(f"   Company: {metrics.company_name}")
        print(f"   Date: {metrics.game_date}")
        print(f"   Cash: ${metrics.cash_on_hand:,.0f}")
        print(f"   Users: {metrics.total_users:,}")
        print(f"   Satisfaction: {metrics.user_satisfaction:.1f}%")
        print(f"   Employees: {metrics.total_employees}")
        
        print(f"\n💰 FINANCIAL STATUS:")
        print(f"   Monthly Burn: ${metrics.monthly_burn_rate:,.0f}")
        print(f"   Runway: {metrics.runway_months:.1f} months")
        print(f"   Risk Level: {strategy.risk_level}")
        
        # Critical alerts
        critical_alerts = [a for a in analysis["alerts"] if a.severity == "CRITICAL"]
        if critical_alerts:
            print(f"\n🚨 CRITICAL ALERTS:")
            for alert in critical_alerts:
                print(f"   • {alert.title}: {alert.description}")
        
        # Top recommendations
        print(f"\n🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(strategy.key_recommendations[:3], 1):
            print(f"   {i}. {rec.title}")
            print(f"      {rec.description}")
            print(f"      Expected: {rec.expected_outcome}")
            print(f"      Timeframe: {rec.time_frame}")
        
        # Production priorities
        if strategy.production_priorities:
            print(f"\n⚙️ PRODUCTION PRIORITIES:")
            for i, priority in enumerate(strategy.production_priorities[:5], 1):
                print(f"   {i}. {priority}")
        
        print(f"\n🧠 AI ASSESSMENT:")
        print(f"   {strategy.overall_assessment}")
        
        print(f"\n💡 FINANCIAL ADVICE:")
        print(f"   {strategy.financial_advice}")
        
        print("\n" + "="*60)
        print("Report generated by Project Phoenix AI Advisor")
        print("="*60)
    
    def export_analysis_json(self, output_path: Path):
        """Export complete analysis to JSON file."""
        dashboard_data = self.get_dashboard_data()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(dashboard_data, f, indent=2)
        
        print(f"📄 Analysis exported to: {output_path}")


# Convenience function for quick analysis
async def analyze_save_file(save_file_path: Path, gemini_api_key: Optional[str] = None) -> StartupCompanyAdvisor:
    """Convenience function to quickly analyze a save file."""
    advisor = StartupCompanyAdvisor(gemini_api_key)
    
    if not advisor.load_save_file(save_file_path):
        raise ValueError(f"Failed to load save file: {save_file_path}")
    
    await advisor.analyze_game_state()
    return advisor


# Example usage
if __name__ == "__main__":
    async def main():
        # Example usage
        save_file = Path("../game_saves/example_save.json")
        
        if save_file.exists():
            advisor = await analyze_save_file(save_file)
            advisor.print_summary_report()
        else:
            print(f"Save file not found: {save_file}")
    
    asyncio.run(main())