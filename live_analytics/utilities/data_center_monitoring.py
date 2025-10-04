"""
Data Center Monitoring System
Monitors server performance, CU usage, and hardware metrics
"""

import json
from typing import Dict, List, Any, Tuple
import streamlit as st

def analyze_data_center_performance(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze data center performance and server metrics"""
    
    # Extract CU (Compute Unit) data and hardware metrics
    # Note: Actual field names may vary - adjust based on real save file structure
    
    server_data = extract_server_metrics(data)
    cu_analysis = analyze_cu_usage(server_data)
    hardware_status = assess_hardware_health(server_data)
    optimization_opportunities = identify_optimization_opportunities(cu_analysis, hardware_status)
    
    return {
        'server_metrics': server_data,
        'cu_analysis': cu_analysis,
        'hardware_status': hardware_status,
        'optimization_opportunities': optimization_opportunities,
        'sysadmin_tasks': generate_sysadmin_tasks(cu_analysis, hardware_status),
        'performance_alerts': generate_performance_alerts(server_data)
    }

def extract_server_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract server and CU metrics from game data"""
    
    # Look for server/hardware related data in the save file
    # This is a template - actual implementation depends on game data structure
    
    server_metrics = {
        'total_servers': 0,
        'active_servers': 0,
        'cu_usage': 0,
        'max_cu_capacity': 1000,  # Default values
        'server_efficiency': 100,
        'maintenance_needed': False,
        'hardware_components': []
    }
    
    # Check for server-related data in various locations
    if 'servers' in data:
        servers = data['servers']
        server_metrics['total_servers'] = len(servers) if isinstance(servers, list) else 1
        server_metrics['active_servers'] = server_metrics['total_servers']
    
    # Look for CU data
    if 'cu' in data:
        cu_data = data['cu']
        if isinstance(cu_data, dict):
            server_metrics['cu_usage'] = cu_data.get('current', 0)
            server_metrics['max_cu_capacity'] = cu_data.get('max', 1000)
        elif isinstance(cu_data, (int, float)):
            server_metrics['cu_usage'] = cu_data
    
    # Check for hardware components that affect server performance
    inventory = data.get('inventory', {})
    for component_name, component_data in inventory.items():
        if any(term in component_name.lower() for term in ['server', 'hardware', 'network', 'database']):
            server_metrics['hardware_components'].append({
                'name': component_name,
                'quantity': component_data.get('amount', 0) if isinstance(component_data, dict) else component_data,
                'type': classify_hardware_component(component_name)
            })
    
    return server_metrics

def classify_hardware_component(component_name: str) -> str:
    """Classify hardware components by their function"""
    
    name_lower = component_name.lower()
    
    if 'server' in name_lower:
        return 'Server Hardware'
    elif 'network' in name_lower:
        return 'Network Infrastructure'
    elif 'database' in name_lower:
        return 'Database Systems'
    elif 'security' in name_lower:
        return 'Security Systems'
    else:
        return 'General Hardware'

def analyze_cu_usage(server_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze CU (Compute Unit) usage and efficiency"""
    
    current_cu = server_data['cu_usage']
    max_cu = server_data['max_cu_capacity']
    
    utilization_rate = (current_cu / max_cu) * 100 if max_cu > 0 else 0
    
    # Determine CU status
    if utilization_rate >= 90:
        cu_status = 'CRITICAL'
        status_message = 'Server capacity near maximum'
    elif utilization_rate >= 75:
        cu_status = 'WARNING'
        status_message = 'High server utilization'
    elif utilization_rate >= 50:
        cu_status = 'GOOD'
        status_message = 'Normal server operation'
    else:
        cu_status = 'OPTIMAL'
        status_message = 'Low server utilization'
    
    # Calculate efficiency metrics
    efficiency_score = calculate_server_efficiency(utilization_rate, server_data)
    
    return {
        'current_cu': current_cu,
        'max_cu': max_cu,
        'utilization_rate': utilization_rate,
        'status': cu_status,
        'status_message': status_message,
        'efficiency_score': efficiency_score,
        'recommended_actions': generate_cu_recommendations(utilization_rate, cu_status)
    }

def calculate_server_efficiency(utilization_rate: float, server_data: Dict[str, Any]) -> float:
    """Calculate overall server efficiency score"""
    
    base_efficiency = 100
    
    # Penalize very high utilization (performance degradation)
    if utilization_rate > 85:
        base_efficiency -= (utilization_rate - 85) * 2
    
    # Penalize very low utilization (waste of resources)
    elif utilization_rate < 30:
        base_efficiency -= (30 - utilization_rate) * 0.5
    
    # Factor in hardware quality
    hardware_components = server_data.get('hardware_components', [])
    if hardware_components:
        total_hardware = sum(comp['quantity'] for comp in hardware_components)
        if total_hardware < 5:  # Insufficient hardware
            base_efficiency -= 20
    
    return max(base_efficiency, 0)

def generate_cu_recommendations(utilization_rate: float, status: str) -> List[Dict[str, Any]]:
    """Generate recommendations for CU optimization"""
    
    recommendations = []
    
    if status == 'CRITICAL':
        recommendations.append({
            'priority': 'URGENT',
            'action': 'Add server capacity immediately',
            'reason': f'CU utilization at {utilization_rate:.1f}% - risk of performance issues',
            'task_type': 'Hardware Upgrade'
        })
    elif status == 'WARNING':
        recommendations.append({
            'priority': 'HIGH',
            'action': 'Plan server capacity expansion',
            'reason': f'CU utilization at {utilization_rate:.1f}% - approaching capacity limits',
            'task_type': 'Capacity Planning'
        })
    elif utilization_rate < 30:
        recommendations.append({
            'priority': 'LOW',
            'action': 'Optimize server configuration',
            'reason': f'CU utilization at {utilization_rate:.1f}% - servers may be underutilized',
            'task_type': 'Optimization'
        })
    
    return recommendations

def assess_hardware_health(server_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess overall hardware health and maintenance needs"""
    
    hardware_components = server_data.get('hardware_components', [])
    
    health_issues = []
    maintenance_priorities = []
    
    # Check for component shortages
    component_types = {}
    for component in hardware_components:
        comp_type = component['type']
        if comp_type not in component_types:
            component_types[comp_type] = 0
        component_types[comp_type] += component['quantity']
    
    # Identify shortages
    required_minimums = {
        'Server Hardware': 3,
        'Network Infrastructure': 2,
        'Database Systems': 2,
        'Security Systems': 1
    }
    
    for comp_type, required in required_minimums.items():
        current = component_types.get(comp_type, 0)
        if current < required:
            health_issues.append({
                'type': 'SHORTAGE',
                'component': comp_type,
                'current': current,
                'required': required,
                'severity': 'HIGH' if current == 0 else 'MEDIUM'
            })
    
    # Overall health score
    total_issues = len(health_issues)
    if total_issues == 0:
        health_score = 100
        health_status = 'EXCELLENT'
    elif total_issues <= 2:
        health_score = 75
        health_status = 'GOOD'
    elif total_issues <= 4:
        health_score = 50
        health_status = 'FAIR'
    else:
        health_score = 25
        health_status = 'POOR'
    
    return {
        'health_score': health_score,
        'health_status': health_status,
        'component_inventory': component_types,
        'health_issues': health_issues,
        'maintenance_priorities': maintenance_priorities
    }

def identify_optimization_opportunities(cu_analysis: Dict[str, Any], hardware_status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify opportunities for system optimization"""
    
    opportunities = []
    
    # CU optimization opportunities
    utilization = cu_analysis['utilization_rate']
    if utilization > 80:
        opportunities.append({
            'category': 'Performance',
            'opportunity': 'Server Load Balancing',
            'description': 'Implement load balancing to distribute CU usage more efficiently',
            'expected_benefit': '15-25% performance improvement',
            'implementation': 'SysAdmin task: Configure load balancing components'
        })
    
    if utilization < 40:
        opportunities.append({
            'category': 'Cost Savings',
            'opportunity': 'Server Consolidation',
            'description': 'Consolidate workloads to reduce server overhead',
            'expected_benefit': '20-30% cost reduction',
            'implementation': 'SysAdmin task: Optimize server configuration'
        })
    
    # Hardware optimization
    health_score = hardware_status['health_score']
    if health_score < 75:
        opportunities.append({
            'category': 'Reliability',
            'opportunity': 'Hardware Upgrade',
            'description': 'Upgrade aging hardware components for better reliability',
            'expected_benefit': 'Improved system stability and performance',
            'implementation': 'SysAdmin task: Hardware maintenance and upgrades'
        })
    
    return opportunities

def generate_sysadmin_tasks(cu_analysis: Dict[str, Any], hardware_status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate specific tasks for SysAdmin to work on"""
    
    tasks = []
    
    # CU-related tasks
    cu_status = cu_analysis['status']
    if cu_status in ['CRITICAL', 'WARNING']:
        tasks.append({
            'priority': 'HIGH' if cu_status == 'CRITICAL' else 'MEDIUM',
            'task_type': 'Server Optimization',
            'description': 'Optimize server performance to reduce CU usage',
            'estimated_time': '2-3 days',
            'components_needed': ['ServerOptimizationModules', 'NetworkComponents'],
            'expected_outcome': f'Reduce CU usage by 10-20%'
        })
    
    # Hardware maintenance tasks
    for issue in hardware_status['health_issues']:
        if issue['severity'] == 'HIGH':
            tasks.append({
                'priority': 'HIGH',
                'task_type': 'Hardware Installation',
                'description': f'Install {issue["component"]} components',
                'estimated_time': '1-2 days',
                'components_needed': [issue['component'].replace(' ', '')],
                'expected_outcome': f'Resolve {issue["component"]} shortage'
            })
    
    # Proactive maintenance
    if hardware_status['health_score'] > 80:
        tasks.append({
            'priority': 'LOW',
            'task_type': 'Preventive Maintenance',
            'description': 'Perform routine system maintenance and optimization',
            'estimated_time': '1 day',
            'components_needed': ['MaintenanceTools'],
            'expected_outcome': 'Maintain optimal system performance'
        })
    
    return tasks

def generate_performance_alerts(server_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate alerts for performance issues"""
    
    alerts = []
    
    cu_usage = server_data['cu_usage']
    max_cu = server_data['max_cu_capacity']
    utilization = (cu_usage / max_cu) * 100 if max_cu > 0 else 0
    
    if utilization >= 95:
        alerts.append({
            'level': 'CRITICAL',
            'message': 'Server capacity at maximum - immediate action required',
            'details': f'CU usage: {cu_usage}/{max_cu} ({utilization:.1f}%)',
            'recommended_action': 'Add server capacity or optimize workloads immediately'
        })
    elif utilization >= 85:
        alerts.append({
            'level': 'WARNING',
            'message': 'Server capacity approaching limits',
            'details': f'CU usage: {cu_usage}/{max_cu} ({utilization:.1f}%)',
            'recommended_action': 'Plan capacity expansion or optimization'
        })
    
    # Check for hardware shortages
    hardware_components = server_data.get('hardware_components', [])
    if len(hardware_components) < 3:
        alerts.append({
            'level': 'WARNING',
            'message': 'Insufficient hardware components detected',
            'details': f'Only {len(hardware_components)} hardware types available',
            'recommended_action': 'Prioritize hardware component production'
        })
    
    return alerts

def calculate_server_cost_analysis(server_data: Dict[str, Any], team_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate cost analysis for server operations"""
    
    # This would integrate with financial data to show server operation costs
    # and potential savings from optimization
    
    current_cu = server_data['cu_usage']
    max_cu = server_data['max_cu_capacity']
    
    # Estimated costs (simplified)
    base_server_cost = 1000  # Base monthly cost
    cu_cost_per_unit = 10    # Cost per CU unit
    
    current_monthly_cost = base_server_cost + (current_cu * cu_cost_per_unit)
    potential_savings = calculate_potential_savings(server_data)
    
    return {
        'current_monthly_cost': current_monthly_cost,
        'cu_cost_breakdown': current_cu * cu_cost_per_unit,
        'base_infrastructure_cost': base_server_cost,
        'potential_monthly_savings': potential_savings,
        'optimization_roi': calculate_optimization_roi(potential_savings, team_data)
    }

def calculate_potential_savings(server_data: Dict[str, Any]) -> float:
    """Calculate potential savings from optimization"""
    
    cu_usage = server_data['cu_usage']
    efficiency_score = server_data.get('server_efficiency', 100)
    
    # Estimate savings based on efficiency improvements
    if efficiency_score < 80:
        potential_improvement = (90 - efficiency_score) / 100
        savings = cu_usage * 10 * potential_improvement  # $10 per CU * improvement
        return savings
    
    return 0

def calculate_optimization_roi(potential_savings: float, team_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate ROI for hiring SysAdmin for optimization"""
    
    # Find SysAdmin salary if exists
    sysadmin_salary = 0
    if 'team_members' in team_data:
        for member in team_data['team_members']:
            if member.get('role') == 'SysAdmin':
                sysadmin_salary = member.get('salary', 5000)
                break
    
    if sysadmin_salary == 0:
        sysadmin_salary = 5000  # Estimated salary
    
    monthly_roi = ((potential_savings * 12) - sysadmin_salary) / sysadmin_salary * 100
    
    return {
        'sysadmin_monthly_cost': sysadmin_salary,
        'annual_potential_savings': potential_savings * 12,
        'net_annual_benefit': (potential_savings * 12) - sysadmin_salary,
        'roi_percentage': monthly_roi,
        'payback_period_months': sysadmin_salary / max(potential_savings, 1)
    }