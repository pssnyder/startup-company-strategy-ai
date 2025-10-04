"""
Smart Recruitment System
Analyzes capacity gaps and provides targeted hiring recommendations
"""

import json
from typing import Dict, List, Any, Tuple
import streamlit as st

def analyze_hiring_needs(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze current workforce and determine specific hiring needs"""
    
    # Get current team composition
    workstations = data.get('office', {}).get('workstations', [])
    
    # Analyze current team by role
    current_team = {
        'Developer': [],
        'Designer': [],
        'LeadDeveloper': [],
        'Researcher': [],
        'SalesExecutive': [],
        'Marketer': []
    }
    
    for workstation in workstations:
        if 'employee' in workstation and workstation['employee']:
            emp = workstation['employee']
            role = emp.get('employeeTypeName', 'Unknown')
            if role in current_team:
                current_team[role].append({
                    'name': emp.get('name'),
                    'speed': emp.get('speed', 0),
                    'level': emp.get('level', 'Beginner'),
                    'salary': emp.get('salary', 0)
                })
    
    # Analyze inventory and production needs
    inventory_analysis = analyze_inventory_needs(data)
    
    # Determine hiring priorities
    hiring_priorities = determine_hiring_priorities(current_team, inventory_analysis, data)
    
    return {
        'current_team': current_team,
        'inventory_analysis': inventory_analysis,
        'hiring_priorities': hiring_priorities,
        'urgent_needs': [h for h in hiring_priorities if h['urgency'] == 'URGENT'],
        'recommended_actions': generate_hiring_recommendations(hiring_priorities)
    }

def analyze_inventory_needs(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze inventory levels and production bottlenecks"""
    
    inventory = data.get('inventory', {})
    
    # Key component categories and their builders
    component_builders = {
        'UIComponents': 'Designer',
        'DatabaseComponents': 'Developer', 
        'NetworkingComponents': 'Developer',
        'SecurityComponents': 'Developer',
        'APIComponents': 'Developer',
        'GameComponents': 'Developer',
        'AlgorithmComponents': 'Developer'
    }
    
    low_inventory_items = []
    critical_shortages = []
    
    for component_type, builder_role in component_builders.items():
        # Check if we have this component type in inventory
        component_count = 0
        if component_type in inventory:
            component_count = inventory[component_type].get('amount', 0)
        
        # Determine if this is a shortage
        if component_count < 5:  # Threshold for low inventory
            shortage_data = {
                'component': component_type,
                'current_stock': component_count,
                'builder_role': builder_role,
                'severity': 'CRITICAL' if component_count == 0 else 'LOW'
            }
            
            if component_count == 0:
                critical_shortages.append(shortage_data)
            else:
                low_inventory_items.append(shortage_data)
    
    return {
        'low_inventory': low_inventory_items,
        'critical_shortages': critical_shortages,
        'component_builders': component_builders
    }

def determine_hiring_priorities(current_team: Dict[str, List], inventory_analysis: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Determine hiring priorities based on capacity and inventory needs"""
    
    priorities = []
    
    # Check for critical component shortages
    for shortage in inventory_analysis['critical_shortages']:
        builder_role = shortage['builder_role']
        current_capacity = len(current_team.get(builder_role, []))
        
        priorities.append({
            'role': builder_role,
            'reason': f"Critical shortage: {shortage['component']} (0 in stock)",
            'urgency': 'URGENT',
            'capacity_gap': 'HIGH',
            'component_focus': shortage['component'],
            'recommended_count': 1,
            'priority_score': 100
        })
    
    # Check for low inventory situations
    for low_item in inventory_analysis['low_inventory']:
        builder_role = low_item['builder_role']
        current_capacity = len(current_team.get(builder_role, []))
        
        # Only add if not already covered by critical shortage
        if not any(p['role'] == builder_role and p['urgency'] == 'URGENT' for p in priorities):
            priorities.append({
                'role': builder_role,
                'reason': f"Low inventory: {low_item['component']} ({low_item['current_stock']} in stock)",
                'urgency': 'HIGH',
                'capacity_gap': 'MEDIUM',
                'component_focus': low_item['component'],
                'recommended_count': 1,
                'priority_score': 80
            })
    
    # Check for general team capacity issues
    features = data.get('Features', [])
    in_development = [f for f in features if f.get('DevProgress', 0) > 0 and f.get('DevProgress', 0) < 1]
    needs_development = [f for f in features if f.get('DevProgress', 0) == 0]
    
    total_dev_work = len(in_development) + len(needs_development)
    total_developers = len(current_team.get('Developer', [])) + len(current_team.get('LeadDeveloper', []))
    
    if total_dev_work > total_developers * 2:  # More than 2 features per developer
        priorities.append({
            'role': 'Developer',
            'reason': f"High development workload: {total_dev_work} features for {total_developers} developers",
            'urgency': 'MEDIUM',
            'capacity_gap': 'HIGH',
            'component_focus': 'General Development',
            'recommended_count': 1,
            'priority_score': 60
        })
    
    # Sort by priority score
    priorities.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return priorities

def generate_hiring_recommendations(hiring_priorities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate specific hiring action recommendations"""
    
    recommendations = []
    
    for priority in hiring_priorities:
        if priority['urgency'] == 'URGENT':
            recommendations.append({
                'action': 'IMMEDIATE_HIRE',
                'role': priority['role'],
                'message': f"🚨 URGENT: Hire {priority['role']} immediately",
                'reason': priority['reason'],
                'timeline': 'Within 24 hours',
                'focus': priority['component_focus']
            })
        elif priority['urgency'] == 'HIGH':
            recommendations.append({
                'action': 'PRIORITY_HIRE',
                'role': priority['role'],
                'message': f"⚡ HIGH PRIORITY: Hire {priority['role']} soon",
                'reason': priority['reason'],
                'timeline': 'Within 1 week',
                'focus': priority['component_focus']
            })
        else:
            recommendations.append({
                'action': 'PLANNED_HIRE',
                'role': priority['role'],
                'message': f"📋 PLANNED: Consider hiring {priority['role']}",
                'reason': priority['reason'],
                'timeline': 'Next month',
                'focus': priority['component_focus']
            })
    
    return recommendations

def filter_candidates_by_role(candidates: List[Dict[str, Any]], target_role: str) -> List[Dict[str, Any]]:
    """Filter candidates to only show those matching the target role"""
    
    filtered_candidates = []
    
    for candidate in candidates:
        if candidate.get('employeeTypeName') == target_role:
            filtered_candidates.append({
                'name': candidate.get('name'),
                'level': candidate.get('level', 'Beginner'),
                'speed': candidate.get('speed', 0),
                'expected_salary': candidate.get('salary', 0),
                'hire_recommendation': assess_candidate_value(candidate)
            })
    
    # Sort by speed (highest first) for top performers
    filtered_candidates.sort(key=lambda x: x['speed'], reverse=True)
    
    return filtered_candidates

def assess_candidate_value(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Assess the hiring value of a candidate"""
    
    speed = candidate.get('speed', 0)
    level = candidate.get('level', 'Beginner')
    salary = candidate.get('salary', 0)
    
    # Speed-based assessment
    if speed >= 150:
        speed_rating = 'EXCELLENT'
    elif speed >= 120:
        speed_rating = 'GOOD'
    elif speed >= 100:
        speed_rating = 'AVERAGE'
    else:
        speed_rating = 'BELOW_AVERAGE'
    
    # Level-based assessment
    level_score = {'Expert': 4, 'Advanced': 3, 'Intermediate': 2, 'Beginner': 1}.get(level, 1)
    
    # Value calculation (speed per salary dollar)
    value_ratio = speed / max(salary, 1000)  # Avoid division by zero
    
    if value_ratio > 0.03:
        value_rating = 'EXCELLENT_VALUE'
    elif value_ratio > 0.025:
        value_rating = 'GOOD_VALUE'
    elif value_ratio > 0.02:
        value_rating = 'FAIR_VALUE'
    else:
        value_rating = 'EXPENSIVE'
    
    return {
        'speed_rating': speed_rating,
        'level_score': level_score,
        'value_rating': value_rating,
        'value_ratio': value_ratio,
        'overall_recommendation': calculate_overall_recommendation(speed_rating, level_score, value_rating)
    }

def calculate_overall_recommendation(speed_rating: str, level_score: int, value_rating: str) -> str:
    """Calculate overall hiring recommendation"""
    
    # Speed weight
    speed_points = {'EXCELLENT': 4, 'GOOD': 3, 'AVERAGE': 2, 'BELOW_AVERAGE': 1}[speed_rating]
    
    # Value weight
    value_points = {'EXCELLENT_VALUE': 4, 'GOOD_VALUE': 3, 'FAIR_VALUE': 2, 'EXPENSIVE': 1}[value_rating]
    
    total_score = speed_points + level_score + value_points
    
    if total_score >= 10:
        return 'INSTANT_HIRE'
    elif total_score >= 8:
        return 'STRONG_CANDIDATE'
    elif total_score >= 6:
        return 'CONSIDER'
    else:
        return 'PASS'

def get_top_candidates_for_role(candidates: List[Dict[str, Any]], target_role: str, count: int = 3) -> List[Dict[str, Any]]:
    """Get the top N candidates for a specific role with hiring recommendations"""
    
    filtered_candidates = filter_candidates_by_role(candidates, target_role)
    
    # Get top candidates by overall recommendation
    instant_hires = [c for c in filtered_candidates if c['hire_recommendation']['overall_recommendation'] == 'INSTANT_HIRE']
    strong_candidates = [c for c in filtered_candidates if c['hire_recommendation']['overall_recommendation'] == 'STRONG_CANDIDATE']
    consider_candidates = [c for c in filtered_candidates if c['hire_recommendation']['overall_recommendation'] == 'CONSIDER']
    
    # Combine in priority order
    top_candidates = (instant_hires + strong_candidates + consider_candidates)[:count]
    
    return top_candidates

def generate_instant_hire_suggestion(hiring_needs: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate instant hire suggestions for urgent needs"""
    
    suggestions = []
    
    for urgent_need in hiring_needs['urgent_needs']:
        role = urgent_need['role']
        top_candidates = get_top_candidates_for_role(candidates, role, 1)
        
        if top_candidates:
            best_candidate = top_candidates[0]
            
            suggestions.append({
                'need': urgent_need,
                'recommended_candidate': best_candidate,
                'action': f"Instant hire {best_candidate['name']} for ${best_candidate['expected_salary']:,}",
                'justification': f"Addresses {urgent_need['reason']} with {best_candidate['hire_recommendation']['speed_rating']} performer"
            })
    
    return {
        'has_suggestions': len(suggestions) > 0,
        'suggestions': suggestions,
        'total_cost': sum(s['recommended_candidate']['expected_salary'] for s in suggestions)
    }