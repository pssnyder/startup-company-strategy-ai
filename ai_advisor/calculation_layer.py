"""
Calculation Layer: Game State Analysis

This module processes current game state against known game rules to identify
issues, opportunities, and resource requirements.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from .data_layer import GameDataManager, ComponentRequirement
from .input_layer import SaveFileParser, GameMetrics, FeatureInstance


@dataclass
class ComponentShortfall:
    """Represents missing components needed for feature upgrades."""
    component_name: str
    needed_quantity: int
    current_quantity: int
    employee_type: str
    total_hours_required: float


@dataclass
class StrategicAlert:
    """Represents a critical issue requiring immediate attention."""
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    title: str
    description: str
    recommended_action: str


@dataclass
class ProductionPlan:
    """Represents a recommended production plan."""
    priority: int
    component_name: str
    quantity_to_produce: int
    employee_type: str
    estimated_hours: float
    reason: str


class GameStateAnalyzer:
    """Analyzes current game state and provides strategic insights."""
    
    def __init__(self, game_data: GameDataManager, save_parser: SaveFileParser):
        self.game_data = game_data
        self.save_parser = save_parser
        self.alerts: List[StrategicAlert] = []
        self.component_shortfalls: List[ComponentShortfall] = []
        self.production_plan: List[ProductionPlan] = []
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of the current game state."""
        self.alerts.clear()
        self.component_shortfalls.clear()
        self.production_plan.clear()
        
        # Run all analysis components
        self._check_critical_alerts()
        self._analyze_feature_gaps()
        self._calculate_component_shortfalls()
        self._generate_production_plan()
        
        return {
            "alerts": self.alerts,
            "component_shortfalls": self.component_shortfalls,
            "production_plan": self.production_plan,
            "metrics_summary": self._get_metrics_summary()
        }
    
    def _check_critical_alerts(self):
        """Identify critical issues requiring immediate attention."""
        if not self.save_parser.metrics:
            return
        
        metrics = self.save_parser.metrics
        
        # Critical satisfaction alert
        if metrics.user_satisfaction < 50.0:
            self.alerts.append(StrategicAlert(
                severity="CRITICAL",
                title="User Satisfaction Crisis",
                description=f"User satisfaction is only {metrics.user_satisfaction:.1f}% (Target: >75%)",
                recommended_action="Immediately upgrade feature Quality/Efficiency levels"
            ))
        elif metrics.user_satisfaction < 75.0:
            self.alerts.append(StrategicAlert(
                severity="HIGH",
                title="Low User Satisfaction",
                description=f"User satisfaction is {metrics.user_satisfaction:.1f}% (Target: >75%)",
                recommended_action="Focus on upgrading key features"
            ))
        
        # Financial runway alert
        if metrics.runway_months < 1.0:
            self.alerts.append(StrategicAlert(
                severity="CRITICAL",
                title="Financial Crisis",
                description=f"Only {metrics.runway_months:.1f} months of runway remaining",
                recommended_action="Secure immediate funding or reduce expenses"
            ))
        elif metrics.runway_months < 3.0:
            self.alerts.append(StrategicAlert(
                severity="HIGH",
                title="Low Financial Runway",
                description=f"Only {metrics.runway_months:.1f} months of runway remaining",
                recommended_action="Focus on revenue generation and cost optimization"
            ))
        
        # Cash flow alert
        if metrics.monthly_burn_rate > metrics.cash_on_hand:
            self.alerts.append(StrategicAlert(
                severity="CRITICAL",
                title="Negative Cash Flow",
                description=f"Monthly burn rate (${metrics.monthly_burn_rate:,.0f}) exceeds cash reserves",
                recommended_action="Reduce expenses immediately or secure emergency funding"
            ))
    
    def _analyze_feature_gaps(self):
        """Analyze quality/efficiency gaps in features."""
        for feature in self.save_parser.features:
            quality_gap = feature.max_quality - feature.current_quality
            efficiency_gap = feature.max_efficiency - feature.current_efficiency
            
            if quality_gap > 20 or efficiency_gap > 20:
                severity = "HIGH" if (quality_gap > 50 or efficiency_gap > 50) else "MEDIUM"
                self.alerts.append(StrategicAlert(
                    severity=severity,
                    title=f"{feature.name} Needs Upgrade",
                    description=f"Q: {feature.current_quality}/{feature.max_quality}, E: {feature.current_efficiency}/{feature.max_efficiency}",
                    recommended_action=f"Upgrade {feature.name} quality and efficiency"
                ))
    
    def _calculate_component_shortfalls(self):
        """Calculate what components are needed for critical upgrades."""
        # Focus on the most critical feature first (likely Landing Page based on the plan)
        critical_features = ["Landing Page", "Login System"]
        
        for feature_name in critical_features:
            feature_instance = self.save_parser.get_feature_by_name(feature_name)
            if not feature_instance:
                continue
            
            # Get requirements for upgrading this feature
            requirements = self.game_data.get_feature_requirements(feature_name)
            
            for req in requirements:
                current_qty = self.save_parser.get_inventory_quantity(req.component_name)
                needed_qty = max(0, req.quantity - current_qty)
                
                if needed_qty > 0:
                    shortfall = ComponentShortfall(
                        component_name=req.component_name,
                        needed_quantity=needed_qty,
                        current_quantity=current_qty,
                        employee_type=req.employee_type,
                        total_hours_required=needed_qty * req.base_time_hours
                    )
                    self.component_shortfalls.append(shortfall)
    
    def _generate_production_plan(self):
        """Generate a prioritized production plan."""
        priority = 1
        
        # Sort shortfalls by criticality (components for critical features first)
        critical_components = ["UI Component", "Backend Component", "Frontend Module", "Backend Module"]
        
        for shortfall in self.component_shortfalls:
            # Higher priority for critical components
            if shortfall.component_name in critical_components:
                plan_priority = priority
                priority += 1
            else:
                plan_priority = priority + 10
            
            reason = f"Required for upgrading critical features (satisfaction boost)"
            
            self.production_plan.append(ProductionPlan(
                priority=plan_priority,
                component_name=shortfall.component_name,
                quantity_to_produce=shortfall.needed_quantity,
                employee_type=shortfall.employee_type,
                estimated_hours=shortfall.total_hours_required,
                reason=reason
            ))
        
        # Sort by priority
        self.production_plan.sort(key=lambda x: x.priority)
    
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of key metrics for the AI strategy layer."""
        if not self.save_parser.metrics:
            return {}
        
        metrics = self.save_parser.metrics
        
        # Calculate team utilization (simplified)
        total_employees = len(self.save_parser.employees)
        active_employees = len([emp for emp in self.save_parser.employees if emp.current_task])
        utilization = (active_employees / total_employees * 100) if total_employees > 0 else 0
        
        return {
            "cash_on_hand": metrics.cash_on_hand,
            "monthly_burn_rate": metrics.monthly_burn_rate,
            "runway_months": metrics.runway_months,
            "user_satisfaction": metrics.user_satisfaction,
            "total_users": metrics.total_users,
            "total_employees": metrics.total_employees,
            "team_utilization": utilization,
            "critical_alerts_count": len([a for a in self.alerts if a.severity == "CRITICAL"]),
            "high_alerts_count": len([a for a in self.alerts if a.severity == "HIGH"])
        }
    
    def get_ai_strategy_context(self) -> str:
        """Generate context string for AI strategy layer."""
        if not self.save_parser.metrics:
            return "No game data available for analysis."
        
        metrics = self.save_parser.metrics
        summary = self._get_metrics_summary()
        
        # Build context string for Gemini
        context_parts = []
        
        # Critical metrics
        context_parts.append(f"CURRENT GAME STATE:")
        context_parts.append(f"- User Satisfaction: {metrics.user_satisfaction:.1f}% (Target: >75%)")
        context_parts.append(f"- Monthly Burn Rate: ${metrics.monthly_burn_rate:,.0f}")
        context_parts.append(f"- Financial Runway: {metrics.runway_months:.1f} months")
        context_parts.append(f"- Total Employees: {metrics.total_employees}")
        context_parts.append(f"- Team Utilization: {summary['team_utilization']:.1f}%")
        
        # Critical alerts
        critical_alerts = [a for a in self.alerts if a.severity == "CRITICAL"]
        if critical_alerts:
            context_parts.append(f"\nCRITICAL ISSUES:")
            for alert in critical_alerts:
                context_parts.append(f"- {alert.title}: {alert.description}")
        
        # Component shortfalls
        if self.component_shortfalls:
            context_parts.append(f"\nCOMPONENT SHORTFALLS:")
            for shortfall in self.component_shortfalls[:5]:  # Top 5 most critical
                context_parts.append(f"- Need {shortfall.needed_quantity}x {shortfall.component_name} ({shortfall.employee_type}, {shortfall.total_hours_required:.1f}h)")
        
        return "\n".join(context_parts)