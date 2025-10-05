"""
Capacity Analyzer - Strategic Decision Module
Calculates team capacity, workstation utilization, and production bottlenecks
"""

from typing import Dict, Any, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..logger_config import setup_logging, SUCCESS_MESSAGES

# Setup safe logging
setup_logging()
logger = logging.getLogger(__name__)

@dataclass
class CapacityMetrics:
    """Container for capacity analysis results"""
    workstation_utilization: float  # % of workstations occupied
    capacity_shortage: int          # How many more workstations needed (negative = surplus)
    employee_efficiency: float      # Average productivity rating
    bottleneck_areas: List[str]     # Areas limiting growth
    growth_capacity: int           # How many more employees can be hired
    
    def get_quantitative_alerts(self) -> List[str]:
        """Generate math-based alerts with specific numbers"""
        alerts = []
        
        if self.workstation_utilization > 90:
            shortage = abs(self.capacity_shortage)
            alerts.append(f"⚠️ CAPACITY CRISIS: Need {shortage} more workstations ({self.workstation_utilization:.1f}% utilization)")
        
        if self.capacity_shortage < -5:
            surplus = abs(self.capacity_shortage)
            alerts.append(f"💰 COST OPPORTUNITY: {surplus} empty workstations = wasted rent")
        
        if self.employee_efficiency < 70:
            alerts.append(f"📉 PRODUCTIVITY ALERT: Team efficiency at {self.employee_efficiency:.1f}% (target: 80%+)")
        
        if self.growth_capacity <= 0:
            alerts.append(f"🚫 GROWTH BLOCKED: Cannot hire more employees (capacity = {self.growth_capacity})")
        
        return alerts

class CapacityAnalyzer:
    """Analyzes team capacity and workspace utilization"""
    
    def __init__(self, database):
        """Initialize with database connection"""
        self.db = database
        self.decision_name = "Capacity Analysis"
        logger.info("Capacity Analyzer initialized")
    
    def analyze_current_capacity(self) -> CapacityMetrics:
        """
        Analyze current team capacity and workspace utilization
        Returns quantitative metrics for decision making
        """
        try:
            # Get latest workspace data
            office_data = self._get_latest_office_data()
            employee_data = self._get_employee_metrics()
            
            # Calculate core metrics
            utilization = self._calculate_workstation_utilization(office_data)
            shortage = self._calculate_capacity_shortage(office_data, employee_data)
            efficiency = self._calculate_team_efficiency(employee_data)
            bottlenecks = self._identify_bottlenecks(office_data, employee_data)
            growth_capacity = self._calculate_growth_capacity(office_data)
            
            metrics = CapacityMetrics(
                workstation_utilization=utilization,
                capacity_shortage=shortage,
                employee_efficiency=efficiency,
                bottleneck_areas=bottlenecks,
                growth_capacity=growth_capacity
            )
            
            logger.info(f"✅ Capacity analysis complete: {utilization:.1f}% utilization, {shortage} capacity gap")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Capacity analysis failed: {str(e)}")
            # Return safe defaults
            return CapacityMetrics(0, 0, 0, ["Analysis Failed"], 0)
    
    def _get_latest_office_data(self) -> Dict[str, Any]:
        """Get most recent office configuration"""
        query = """
        SELECT workstations_total, workstations_occupied, office_level, monthly_rent
        FROM office_data o
        JOIN save_files s ON o.save_file_id = s.id
        ORDER BY s.real_timestamp DESC
        LIMIT 1
        """
        
        results = self.db.execute_read_query(query)
        if results:
            return results[0]
        else:
            logger.warning("⚠️ No office data found, using defaults")
            return {
                'workstations_total': 10,
                'workstations_occupied': 0,
                'office_level': 1,
                'monthly_rent': 5000
            }
    
    def _get_employee_metrics(self) -> List[Dict[str, Any]]:
        """Get current employee data"""
        query = """
        SELECT employee_id, name, position, skill_level, productivity, assigned_task
        FROM employees e
        JOIN save_files s ON e.save_file_id = s.id
        WHERE s.id = (SELECT id FROM save_files ORDER BY real_timestamp DESC LIMIT 1)
        AND e.is_active = 1
        """
        
        return self.db.execute_read_query(query)
    
    def _calculate_workstation_utilization(self, office_data: Dict[str, Any]) -> float:
        """Calculate percentage of workstations in use"""
        total = office_data.get('workstations_total', 1)
        occupied = office_data.get('workstations_occupied', 0)
        
        if total == 0:
            return 0.0
        
        return (occupied / total) * 100
    
    def _calculate_capacity_shortage(self, office_data: Dict[str, Any], employee_data: List[Dict[str, Any]]) -> int:
        """
        Calculate capacity shortage/surplus
        Negative = surplus workstations, Positive = need more workstations
        """
        total_workstations = office_data.get('workstations_total', 0)
        active_employees = len(employee_data)
        
        # Account for optimal buffer (10% spare capacity for flexibility)
        optimal_capacity = int(active_employees * 1.1)
        shortage = optimal_capacity - total_workstations
        
        return shortage
    
    def _calculate_team_efficiency(self, employee_data: List[Dict[str, Any]]) -> float:
        """Calculate average team productivity"""
        if not employee_data:
            return 0.0
        
        # If productivity data available, use it
        productivities = [emp.get('productivity', 75) for emp in employee_data if emp.get('productivity')]
        
        if productivities:
            return sum(productivities) / len(productivities)
        
        # Fallback: estimate based on skill levels
        skill_levels = [emp.get('skill_level', 3.0) for emp in employee_data if emp.get('skill_level')]
        
        if skill_levels:
            avg_skill = sum(skill_levels) / len(skill_levels)
            # Convert skill (1-5) to productivity percentage (20-100%)
            return 20 + (avg_skill - 1) * 20
        
        return 75.0  # Default assumption
    
    def _identify_bottlenecks(self, office_data: Dict[str, Any], employee_data: List[Dict[str, Any]]) -> List[str]:
        """Identify areas that limit team growth"""
        bottlenecks = []
        
        # Workspace bottlenecks
        utilization = self._calculate_workstation_utilization(office_data)
        if utilization > 90:
            bottlenecks.append("Workspace Space")
        
        # Team composition bottlenecks
        positions = [emp.get('position', 'unknown') for emp in employee_data]
        position_counts = {}
        for pos in positions:
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # Check for missing critical roles
        if position_counts.get('developer', 0) < 2:
            bottlenecks.append("Developer Shortage")
        
        if position_counts.get('designer', 0) == 0 and len(employee_data) > 3:
            bottlenecks.append("No Designers")
        
        if position_counts.get('marketer', 0) == 0 and len(employee_data) > 5:
            bottlenecks.append("No Marketing")
        
        # Financial constraints (if rent is high relative to team size)
        monthly_rent = office_data.get('monthly_rent', 0)
        rent_per_employee = monthly_rent / max(len(employee_data), 1)
        if rent_per_employee > 2000:
            bottlenecks.append("High Rent Overhead")
        
        return bottlenecks if bottlenecks else ["No Major Bottlenecks"]
    
    def _calculate_growth_capacity(self, office_data: Dict[str, Any]) -> int:
        """Calculate how many more employees can be hired"""
        total_workstations = office_data.get('workstations_total', 0)
        occupied_workstations = office_data.get('workstations_occupied', 0)
        
        available_seats = total_workstations - occupied_workstations
        
        # Reserve 1 seat as buffer if we have capacity
        if available_seats > 1:
            return available_seats - 1
        else:
            return available_seats
    
    def get_capacity_recommendations(self, metrics: CapacityMetrics) -> List[str]:
        """Generate specific, actionable recommendations"""
        recommendations = []
        
        # Immediate capacity issues
        if metrics.capacity_shortage > 0:
            recommendations.append(f"🏢 URGENT: Purchase {metrics.capacity_shortage} more workstations")
        
        if metrics.workstation_utilization > 85:
            recommendations.append("📈 Office expansion needed within 2 weeks")
        
        # Efficiency improvements
        if metrics.employee_efficiency < 75:
            recommendations.append("🎯 Implement productivity training program")
            recommendations.append("🔍 Review individual performance metrics")
        
        # Growth planning
        if metrics.growth_capacity > 3:
            recommendations.append(f"✅ Ready to hire {metrics.growth_capacity} more employees")
        elif metrics.growth_capacity <= 0:
            recommendations.append("⚠️ Must expand office before hiring")
        
        # Bottleneck solutions
        for bottleneck in metrics.bottleneck_areas:
            if bottleneck == "Developer Shortage":
                recommendations.append("💻 Priority hire: Senior Developer")
            elif bottleneck == "No Designers":
                recommendations.append("🎨 Priority hire: UI/UX Designer")
            elif bottleneck == "No Marketing":
                recommendations.append("📢 Priority hire: Marketing Specialist")
            elif bottleneck == "High Rent Overhead":
                recommendations.append("💰 Consider moving to cheaper office location")
        
        return recommendations
    
    def calculate_trend_analysis(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze capacity trends over time"""
        try:
            # Get historical office data
            query = """
            SELECT s.game_date, s.real_timestamp, o.workstations_total, 
                   o.workstations_occupied, s.total_employees
            FROM office_data o
            JOIN save_files s ON o.save_file_id = s.id
            WHERE s.real_timestamp >= datetime('now', '-{} days')
            ORDER BY s.real_timestamp ASC
            """.format(days_back)
            
            historical_data = self.db.execute_read_query(query)
            
            if len(historical_data) < 2:
                return {"trend": "insufficient_data", "growth_rate": 0}
            
            # Calculate growth metrics
            first_record = historical_data[0]
            last_record = historical_data[-1]
            
            employee_growth = last_record['total_employees'] - first_record['total_employees']
            workstation_growth = last_record['workstations_total'] - first_record['workstations_total']
            
            # Calculate growth rate (employees per week)
            time_span = len(historical_data)  # Approximate time span
            growth_rate = employee_growth / max(time_span, 1)
            
            return {
                "employee_growth": employee_growth,
                "workstation_growth": workstation_growth,
                "growth_rate_per_save": round(growth_rate, 2),
                "trend": "growing" if employee_growth > 0 else "stable",
                "expansion_frequency": workstation_growth
            }
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed: {str(e)}")
            return {"trend": "error", "growth_rate": 0}