"""
Static Evaluation Engine for Startup Company Game
Pure data-driven analysis with quantitative thresholds and actionable outputs

Input → Calculation → Processing → Output pipeline
Raw game data → Metrics calculation → Threshold analysis → Specific game actions
"""

import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import math

# Game-specific constants and thresholds
PRODUCTION_THRESHOLDS = {
    'ui_component_min_rate': 0.4,  # components per hour
    'feature_completion_target': 80,  # percentage
    'employee_utilization_max': 90,  # percentage
    'employee_utilization_min': 40,  # percentage
    'satisfaction_critical': 60,  # percentage
    'satisfaction_optimal': 80,  # percentage
    'market_penetration_low': 10,  # percentage
    'market_penetration_high': 50,  # percentage
    'cash_runway_critical': 30,  # days
    'lead_value_threshold': 200000,  # impressions
    'beginner_lead_limit': 1,  # maximum concurrent leads
    'cu_utilization_warning': 75,  # percentage
    'cu_utilization_critical': 90,  # percentage
}

class StaticEvaluationEngine:
    """Main evaluation engine for converting game data into actionable insights"""
    
    def __init__(self, game_data: Dict[str, Any]):
        self.raw_data = game_data
        self.calculated_metrics = {}
        self.threshold_analysis = {}
        self.actionable_outputs = []
        
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Execute complete evaluation pipeline"""
        
        # Step 1: Calculate core metrics from raw data
        self.calculated_metrics = self._calculate_core_metrics()
        
        # Step 2: Analyze against thresholds
        self.threshold_analysis = self._analyze_thresholds()
        
        # Step 3: Generate specific game actions
        self.actionable_outputs = self._generate_game_actions()
        
        return {
            'input_data_timestamp': datetime.now().isoformat(),
            'calculated_metrics': self.calculated_metrics,
            'threshold_analysis': self.threshold_analysis,
            'actionable_outputs': self.actionable_outputs,
            'evaluation_summary': self._generate_evaluation_summary()
        }
    
    def _calculate_core_metrics(self) -> Dict[str, Any]:
        """Calculate core metrics from raw game data"""
        
        metrics = {
            'production_rates': self._calculate_production_rates(),
            'team_utilization': self._calculate_team_utilization(),
            'financial_runway': self._calculate_financial_runway(),
            'market_metrics': self._calculate_market_metrics(),
            'system_performance': self._calculate_system_performance(),
            'sales_pipeline': self._calculate_sales_pipeline()
        }
        
        return metrics
    
    def _calculate_production_rates(self) -> Dict[str, float]:
        """Calculate component and feature production rates"""
        
        # This would analyze inventory changes over time to calculate actual production rates
        # For now, using placeholder calculation logic
        
        inventory = self.raw_data.get('inventory', {})
        
        # Example calculation for UI components
        ui_components = 0
        for item_name, item_data in inventory.items():
            if 'ui' in item_name.lower() or 'component' in item_name.lower():
                if isinstance(item_data, dict):
                    ui_components += item_data.get('amount', 0)
                else:
                    ui_components += item_data
        
        # Calculate production rate based on team size and efficiency
        developers = self._count_developers()
        hours_per_dev = 8  # Standard work day
        
        ui_production_rate = (ui_components / max(developers * hours_per_dev, 1)) if developers > 0 else 0
        
        return {
            'ui_component_rate': ui_production_rate,
            'total_components': ui_components,
            'developer_productivity': ui_production_rate / max(developers, 1)
        }
    
    def _calculate_team_utilization(self) -> Dict[str, Any]:
        """Calculate team member utilization rates"""
        
        workstations = self.raw_data.get('office', {}).get('workstations', [])
        
        total_employees = 0
        assigned_employees = 0
        utilization_by_role = {}
        
        for workstation in workstations:
            if 'employee' in workstation and workstation['employee']:
                emp = workstation['employee']
                total_employees += 1
                
                role = emp.get('employeeTypeName', 'Unknown')
                
                if role not in utilization_by_role:
                    utilization_by_role[role] = {'total': 0, 'assigned': 0}
                
                utilization_by_role[role]['total'] += 1
                
                # Check if employee has active assignment
                if emp.get('currentAssignment') or emp.get('workQueue'):
                    assigned_employees += 1
                    utilization_by_role[role]['assigned'] += 1
        
        # Calculate utilization percentages
        for role_data in utilization_by_role.values():
            role_data['utilization_percent'] = (role_data['assigned'] / max(role_data['total'], 1)) * 100
        
        overall_utilization = (assigned_employees / max(total_employees, 1)) * 100
        
        return {
            'overall_utilization': overall_utilization,
            'total_employees': total_employees,
            'assigned_employees': assigned_employees,
            'by_role': utilization_by_role
        }
    
    def _calculate_financial_runway(self) -> Dict[str, Any]:
        """Calculate cash runway and burn rate"""
        
        current_cash = self.raw_data.get('cash', 0)
        
        # Calculate monthly burn rate from employee salaries
        monthly_burn = 0
        workstations = self.raw_data.get('office', {}).get('workstations', [])
        
        for workstation in workstations:
            if 'employee' in workstation and workstation['employee']:
                emp = workstation['employee']
                salary = emp.get('salary', 0)
                monthly_burn += salary
        
        # Add office costs (estimated)
        office_costs = len(workstations) * 100  # $100 per workstation estimate
        monthly_burn += office_costs
        
        # Calculate runway in days
        daily_burn = monthly_burn / 30
        runway_days = current_cash / max(daily_burn, 1) if daily_burn > 0 else float('inf')
        
        return {
            'current_cash': current_cash,
            'monthly_burn_rate': monthly_burn,
            'daily_burn_rate': daily_burn,
            'runway_days': runway_days,
            'runway_months': runway_days / 30
        }
    
    def _calculate_market_metrics(self) -> Dict[str, Any]:
        """Calculate market penetration and user metrics"""
        
        users = self.raw_data.get('users', 0)
        satisfaction = self.raw_data.get('satisfaction', 0)
        
        # Estimate market size based on features and user base
        features = self.raw_data.get('features', {})
        completed_features = sum(1 for f in features.values() if f.get('completionPercent', 0) >= 100)
        
        # Simple market size estimation
        estimated_market_size = completed_features * 10000  # 10k users per feature estimate
        market_penetration = (users / max(estimated_market_size, 1)) * 100
        
        return {
            'current_users': users,
            'satisfaction_percent': satisfaction,
            'estimated_market_size': estimated_market_size,
            'market_penetration_percent': market_penetration,
            'completed_features': completed_features
        }
    
    def _calculate_system_performance(self) -> Dict[str, Any]:
        """Calculate server and CU performance metrics"""
        
        # Extract CU data (placeholder logic - actual field names may vary)
        cu_current = self.raw_data.get('cu', {}).get('current', 0) if isinstance(self.raw_data.get('cu'), dict) else self.raw_data.get('cu', 0)
        cu_max = self.raw_data.get('cu', {}).get('max', 1000) if isinstance(self.raw_data.get('cu'), dict) else 1000
        
        cu_utilization = (cu_current / max(cu_max, 1)) * 100
        
        return {
            'cu_current': cu_current,
            'cu_maximum': cu_max,
            'cu_utilization_percent': cu_utilization,
            'cu_available': cu_max - cu_current
        }
    
    def _calculate_sales_pipeline(self) -> Dict[str, Any]:
        """Calculate sales pipeline metrics"""
        
        # Extract sales data (placeholder logic)
        # This would need to be adapted based on actual game data structure
        
        return {
            'active_leads': 0,
            'pipeline_value': 0,
            'conversion_rate': 0,
            'average_deal_size': 0
        }
    
    def _count_developers(self) -> int:
        """Count total developers in the team"""
        
        count = 0
        workstations = self.raw_data.get('office', {}).get('workstations', [])
        
        for workstation in workstations:
            if 'employee' in workstation and workstation['employee']:
                emp = workstation['employee']
                role = emp.get('employeeTypeName', '')
                if role in ['Developer', 'LeadDeveloper']:
                    count += 1
        
        return count
    
    def _analyze_thresholds(self) -> Dict[str, Any]:
        """Analyze calculated metrics against defined thresholds"""
        
        analysis = {
            'production_analysis': self._analyze_production_thresholds(),
            'utilization_analysis': self._analyze_utilization_thresholds(),
            'financial_analysis': self._analyze_financial_thresholds(),
            'market_analysis': self._analyze_market_thresholds(),
            'system_analysis': self._analyze_system_thresholds()
        }
        
        return analysis
    
    def _analyze_production_thresholds(self) -> List[Dict[str, Any]]:
        """Analyze production rates against thresholds"""
        
        production = self.calculated_metrics['production_rates']
        alerts = []
        
        # UI Component production rate check
        ui_rate = production['ui_component_rate']
        if ui_rate < PRODUCTION_THRESHOLDS['ui_component_min_rate']:
            alerts.append({
                'metric': 'ui_component_production_rate',
                'current_value': ui_rate,
                'threshold': PRODUCTION_THRESHOLDS['ui_component_min_rate'],
                'status': 'BELOW_THRESHOLD',
                'severity': 'HIGH',
                'trigger_condition': f'UI component rate {ui_rate:.2f} < {PRODUCTION_THRESHOLDS["ui_component_min_rate"]}'
            })
        
        return alerts
    
    def _analyze_utilization_thresholds(self) -> List[Dict[str, Any]]:
        """Analyze team utilization against thresholds"""
        
        utilization = self.calculated_metrics['team_utilization']
        alerts = []
        
        overall_util = utilization['overall_utilization']
        
        if overall_util > PRODUCTION_THRESHOLDS['employee_utilization_max']:
            alerts.append({
                'metric': 'team_utilization',
                'current_value': overall_util,
                'threshold': PRODUCTION_THRESHOLDS['employee_utilization_max'],
                'status': 'ABOVE_THRESHOLD',
                'severity': 'HIGH',
                'trigger_condition': f'Team utilization {overall_util:.1f}% > {PRODUCTION_THRESHOLDS["employee_utilization_max"]}%'
            })
        elif overall_util < PRODUCTION_THRESHOLDS['employee_utilization_min']:
            alerts.append({
                'metric': 'team_utilization',
                'current_value': overall_util,
                'threshold': PRODUCTION_THRESHOLDS['employee_utilization_min'],
                'status': 'BELOW_THRESHOLD',
                'severity': 'MEDIUM',
                'trigger_condition': f'Team utilization {overall_util:.1f}% < {PRODUCTION_THRESHOLDS["employee_utilization_min"]}%'
            })
        
        return alerts
    
    def _analyze_financial_thresholds(self) -> List[Dict[str, Any]]:
        """Analyze financial metrics against thresholds"""
        
        financial = self.calculated_metrics['financial_runway']
        alerts = []
        
        runway_days = financial['runway_days']
        
        if runway_days < PRODUCTION_THRESHOLDS['cash_runway_critical']:
            alerts.append({
                'metric': 'cash_runway',
                'current_value': runway_days,
                'threshold': PRODUCTION_THRESHOLDS['cash_runway_critical'],
                'status': 'BELOW_THRESHOLD',
                'severity': 'CRITICAL',
                'trigger_condition': f'Cash runway {runway_days:.1f} days < {PRODUCTION_THRESHOLDS["cash_runway_critical"]} days'
            })
        
        return alerts
    
    def _analyze_market_thresholds(self) -> List[Dict[str, Any]]:
        """Analyze market metrics against thresholds"""
        
        market = self.calculated_metrics['market_metrics']
        alerts = []
        
        satisfaction = market['satisfaction_percent']
        penetration = market['market_penetration_percent']
        
        if satisfaction < PRODUCTION_THRESHOLDS['satisfaction_critical']:
            alerts.append({
                'metric': 'user_satisfaction',
                'current_value': satisfaction,
                'threshold': PRODUCTION_THRESHOLDS['satisfaction_critical'],
                'status': 'BELOW_THRESHOLD',
                'severity': 'HIGH',
                'trigger_condition': f'User satisfaction {satisfaction}% < {PRODUCTION_THRESHOLDS["satisfaction_critical"]}%'
            })
        
        if penetration < PRODUCTION_THRESHOLDS['market_penetration_low']:
            alerts.append({
                'metric': 'market_penetration',
                'current_value': penetration,
                'threshold': PRODUCTION_THRESHOLDS['market_penetration_low'],
                'status': 'BELOW_THRESHOLD',
                'severity': 'MEDIUM',
                'trigger_condition': f'Market penetration {penetration:.1f}% < {PRODUCTION_THRESHOLDS["market_penetration_low"]}%'
            })
        
        return alerts
    
    def _analyze_system_thresholds(self) -> List[Dict[str, Any]]:
        """Analyze system performance against thresholds"""
        
        system = self.calculated_metrics['system_performance']
        alerts = []
        
        cu_utilization = system['cu_utilization_percent']
        
        if cu_utilization > PRODUCTION_THRESHOLDS['cu_utilization_critical']:
            alerts.append({
                'metric': 'cu_utilization',
                'current_value': cu_utilization,
                'threshold': PRODUCTION_THRESHOLDS['cu_utilization_critical'],
                'status': 'ABOVE_THRESHOLD',
                'severity': 'CRITICAL',
                'trigger_condition': f'CU utilization {cu_utilization:.1f}% > {PRODUCTION_THRESHOLDS["cu_utilization_critical"]}%'
            })
        elif cu_utilization > PRODUCTION_THRESHOLDS['cu_utilization_warning']:
            alerts.append({
                'metric': 'cu_utilization',
                'current_value': cu_utilization,
                'threshold': PRODUCTION_THRESHOLDS['cu_utilization_warning'],
                'status': 'ABOVE_THRESHOLD',
                'severity': 'MEDIUM',
                'trigger_condition': f'CU utilization {cu_utilization:.1f}% > {PRODUCTION_THRESHOLDS["cu_utilization_warning"]}%'
            })
        
        return alerts
    
    def _generate_game_actions(self) -> List[Dict[str, Any]]:
        """Generate specific, actionable game commands based on threshold analysis"""
        
        actions = []
        
        # Process all threshold alerts and generate corresponding game actions
        for category, alerts in self.threshold_analysis.items():
            for alert in alerts:
                action = self._convert_alert_to_action(alert, category)
                if action:
                    actions.append(action)
        
        return actions
    
    def _convert_alert_to_action(self, alert: Dict[str, Any], category: str) -> Optional[Dict[str, Any]]:
        """Convert threshold alert to specific game action"""
        
        metric = alert['metric']
        severity = alert['severity']
        current_value = alert['current_value']
        
        if metric == 'ui_component_production_rate':
            return {
                'action_type': 'PRODUCTION_OPTIMIZATION',
                'priority': severity,
                'game_command': 'INCREASE_UI_COMPONENT_PRODUCTION',
                'specific_action': 'Add UIComponent to developer work queues',
                'target_metric': 'ui_component_rate',
                'current_value': current_value,
                'target_value': PRODUCTION_THRESHOLDS['ui_component_min_rate'],
                'implementation': {
                    'step_1': 'Identify developers with available queue capacity',
                    'step_2': 'Add +2 UIComponent tasks to each available developer',
                    'step_3': 'Monitor production rate improvement',
                    'expected_result': f'Increase production from {current_value:.2f} to ≥{PRODUCTION_THRESHOLDS["ui_component_min_rate"]}'
                }
            }
        
        elif metric == 'team_utilization':
            if alert['status'] == 'ABOVE_THRESHOLD':
                return {
                    'action_type': 'CAPACITY_EXPANSION',
                    'priority': severity,
                    'game_command': 'HIRE_ADDITIONAL_STAFF',
                    'specific_action': 'Hire 1-2 additional developers',
                    'target_metric': 'team_utilization',
                    'current_value': current_value,
                    'target_value': PRODUCTION_THRESHOLDS['employee_utilization_max'],
                    'implementation': {
                        'step_1': 'Access hiring interface',
                        'step_2': 'Hire Developer (Level 1-2)',
                        'step_3': 'Assign to UIComponent production',
                        'expected_result': f'Reduce utilization from {current_value:.1f}% to <{PRODUCTION_THRESHOLDS["employee_utilization_max"]}%'
                    }
                }
            else:  # BELOW_THRESHOLD
                return {
                    'action_type': 'WORKLOAD_INCREASE',
                    'priority': severity,
                    'game_command': 'ASSIGN_ADDITIONAL_TASKS',
                    'specific_action': 'Add more tasks to underutilized team members',
                    'target_metric': 'team_utilization',
                    'current_value': current_value,
                    'target_value': PRODUCTION_THRESHOLDS['employee_utilization_min'],
                    'implementation': {
                        'step_1': 'Identify underutilized employees',
                        'step_2': 'Add production tasks to their work queues',
                        'step_3': 'Balance workload across team',
                        'expected_result': f'Increase utilization from {current_value:.1f}% to >{PRODUCTION_THRESHOLDS["employee_utilization_min"]}%'
                    }
                }
        
        elif metric == 'cash_runway':
            return {
                'action_type': 'FINANCIAL_EMERGENCY',
                'priority': 'CRITICAL',
                'game_command': 'REDUCE_EXPENSES_OR_INCREASE_REVENUE',
                'specific_action': 'Immediate cost reduction or revenue generation',
                'target_metric': 'cash_runway',
                'current_value': current_value,
                'target_value': PRODUCTION_THRESHOLDS['cash_runway_critical'],
                'implementation': {
                    'step_1': 'Reduce non-essential expenses',
                    'step_2': 'Accelerate sales activities',
                    'step_3': 'Consider emergency funding',
                    'expected_result': f'Extend runway from {current_value:.1f} to >{PRODUCTION_THRESHOLDS["cash_runway_critical"]} days'
                }
            }
        
        elif metric == 'user_satisfaction':
            return {
                'action_type': 'QUALITY_IMPROVEMENT',
                'priority': severity,
                'game_command': 'ASSIGN_BUG_FIXES_AND_IMPROVEMENTS',
                'specific_action': 'Prioritize quality and bug fix tasks',
                'target_metric': 'satisfaction',
                'current_value': current_value,
                'target_value': PRODUCTION_THRESHOLDS['satisfaction_critical'],
                'implementation': {
                    'step_1': 'Assign developers to bug fixing',
                    'step_2': 'Prioritize quality over new features',
                    'step_3': 'Monitor satisfaction improvement',
                    'expected_result': f'Increase satisfaction from {current_value}% to >{PRODUCTION_THRESHOLDS["satisfaction_critical"]}%'
                }
            }
        
        elif metric == 'cu_utilization':
            return {
                'action_type': 'INFRASTRUCTURE_SCALING',
                'priority': severity,
                'game_command': 'UPGRADE_SERVER_CAPACITY',
                'specific_action': 'Add server capacity or optimize CU usage',
                'target_metric': 'cu_utilization',
                'current_value': current_value,
                'target_value': PRODUCTION_THRESHOLDS['cu_utilization_warning'],
                'implementation': {
                    'step_1': 'Assess current server configuration',
                    'step_2': 'Add additional server capacity',
                    'step_3': 'Optimize CU allocation',
                    'expected_result': f'Reduce CU utilization from {current_value:.1f}% to <{PRODUCTION_THRESHOLDS["cu_utilization_warning"]}%'
                }
            }
        
        return None
    
    def _generate_evaluation_summary(self) -> Dict[str, Any]:
        """Generate high-level summary of evaluation results"""
        
        total_alerts = sum(len(alerts) for alerts in self.threshold_analysis.values())
        critical_actions = len([a for a in self.actionable_outputs if a.get('priority') == 'CRITICAL'])
        
        return {
            'total_metrics_calculated': len(self.calculated_metrics),
            'total_threshold_alerts': total_alerts,
            'critical_actions_required': critical_actions,
            'evaluation_status': 'CRITICAL' if critical_actions > 0 else 'NORMAL',
            'next_evaluation_recommended': 'IMMEDIATE' if critical_actions > 0 else 'HOURLY'
        }

def run_static_evaluation(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for static evaluation engine"""
    
    engine = StaticEvaluationEngine(game_data)
    return engine.run_full_evaluation()

# Example usage and testing
if __name__ == "__main__":
    # Example game data structure
    sample_data = {
        'cash': 50000,
        'users': 1000,
        'satisfaction': 45,
        'cu': {'current': 850, 'max': 1000},
        'inventory': {
            'UIComponent': {'amount': 5},
            'NetworkComponent': {'amount': 2}
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
                }
            ]
        }
    }
    
    result = run_static_evaluation(sample_data)
    print(json.dumps(result, indent=2))