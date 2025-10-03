"""
Advanced Workforce Management and Production Planning
Provides data-driven insights for team optimization and capacity planning
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import streamlit as st

def analyze_employee_work_queues(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze individual employee work queues and current assignments"""
    
    employees = data.get('Employees', [])
    features = data.get('Features', [])
    
    # Build employee work queue analysis
    employee_analysis = {}
    
    for emp in employees:
        emp_id = emp.get('ID', 'unknown')
        name = emp.get('Name', f'Employee {emp_id}')
        role = emp.get('Role', 'Unknown')
        
        # Get current assignment
        current_assignment = None
        assigned_feature = emp.get('AssignedFeature')
        if assigned_feature:
            # Find the feature this employee is working on
            for feature in features:
                if feature.get('ID') == assigned_feature:
                    current_assignment = {
                        'feature_name': feature.get('Name', 'Unknown Feature'),
                        'feature_id': assigned_feature,
                        'dev_progress': feature.get('DevProgress', 0),
                        'art_progress': feature.get('ArtProgress', 0),
                        'assignment_role': emp.get('AssignmentRole', 'Unknown')
                    }
                    break
        
        # Analyze skills and capabilities
        skills = {
            'system': emp.get('SystemSkill', 0),
            'algorithm': emp.get('AlgorithmSkill', 0), 
            'research': emp.get('ResearchSkill', 0),
            'design': emp.get('DesignSkill', 0),
            'game': emp.get('GameSkill', 0)
        }
        
        employee_analysis[emp_id] = {
            'name': name,
            'role': role,
            'skills': skills,
            'tier': emp.get('Tier', 1),
            'current_assignment': current_assignment,
            'salary': emp.get('Salary', 0),
            'effectiveness': emp.get('Effectiveness', 100),
            'specialization': get_primary_specialization(skills),
            'capacity_rating': calculate_capacity_rating(skills, emp.get('Tier', 1))
        }
    
    return employee_analysis

def get_primary_specialization(skills: Dict[str, float]) -> str:
    """Determine employee's primary specialization based on highest skill"""
    if not skills:
        return "Generalist"
    
    max_skill = max(skills.values())
    if max_skill == 0:
        return "Trainee"
    
    primary_skills = [skill for skill, value in skills.items() if value == max_skill]
    
    skill_labels = {
        'system': 'System Developer',
        'algorithm': 'Algorithm Specialist', 
        'research': 'Researcher',
        'design': 'Designer',
        'game': 'Game Developer'
    }
    
    if len(primary_skills) == 1:
        return skill_labels.get(primary_skills[0], 'Specialist')
    else:
        return f"Multi-skilled ({', '.join(primary_skills)})"

def calculate_capacity_rating(skills: Dict[str, float], tier: int) -> float:
    """Calculate overall capacity rating for an employee"""
    if not skills:
        return 0.0
    
    # Weight skills by their average
    avg_skill = sum(skills.values()) / len(skills)
    
    # Factor in tier multiplier
    tier_multiplier = 1 + (tier - 1) * 0.5
    
    return avg_skill * tier_multiplier

def analyze_production_requirements(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze what production capacity is needed vs available"""
    
    features = data.get('Features', [])
    employees = data.get('Employees', [])
    
    # Categorize features by development state
    in_development = []
    needs_development = []
    needs_art = []
    completed = []
    
    for feature in features:
        dev_progress = feature.get('DevProgress', 0)
        art_progress = feature.get('ArtProgress', 0)
        
        if dev_progress >= 1.0 and art_progress >= 1.0:
            completed.append(feature)
        elif dev_progress < 1.0 and dev_progress > 0:
            in_development.append(feature)
        elif dev_progress >= 1.0 and art_progress < 1.0:
            needs_art.append(feature)
        else:
            needs_development.append(feature)
    
    # Calculate skill demand
    skill_demand = {
        'system': 0.0,
        'algorithm': 0.0,
        'research': 0.0,
        'design': 0.0,
        'game': 0.0
    }
    
    # Estimate skill requirements for pending features
    for feature in needs_development + in_development:
        # Simplified skill requirement estimation
        # In reality, this would need more complex feature categorization
        feature_type = feature.get('FeatureType', 'Unknown')
        
        # Rough skill allocation based on feature needs
        skill_demand['system'] += 0.3
        skill_demand['algorithm'] += 0.2
        skill_demand['design'] += 0.2
        skill_demand['research'] += 0.1
        skill_demand['game'] += 0.2
    
    # Calculate available capacity
    available_capacity = {
        'system': 0.0,
        'algorithm': 0.0,
        'research': 0.0,
        'design': 0.0,
        'game': 0.0
    }
    
    for emp in employees:
        if emp.get('AssignedFeature'):  # Only count if actively working
            continue
            
        skills = {
            'system': emp.get('SystemSkill', 0),
            'algorithm': emp.get('AlgorithmSkill', 0),
            'research': emp.get('ResearchSkill', 0),
            'design': emp.get('DesignSkill', 0),
            'game': emp.get('GameSkill', 0)
        }
        
        for skill, value in skills.items():
            available_capacity[skill] += value * 0.01  # Convert to daily capacity
    
    # Calculate capacity gaps
    capacity_gaps = {}
    for skill in skill_demand:
        gap = skill_demand[skill] - available_capacity[skill]
        capacity_gaps[skill] = {
            'demand': skill_demand[skill],
            'available': available_capacity[skill],
            'gap': gap,
            'utilization': (available_capacity[skill] / max(skill_demand[skill], 0.1)) * 100
        }
    
    return {
        'features_summary': {
            'in_development': len(in_development),
            'needs_development': len(needs_development),
            'needs_art': len(needs_art),
            'completed': len(completed)
        },
        'capacity_analysis': capacity_gaps,
        'recommendations': generate_capacity_recommendations(capacity_gaps)
    }

def generate_capacity_recommendations(capacity_gaps: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """Generate actionable recommendations for capacity management"""
    
    recommendations = []
    
    for skill, analysis in capacity_gaps.items():
        gap = analysis['gap']
        utilization = analysis['utilization']
        
        if gap > 0.5:  # Significant shortfall
            recommendations.append({
                'priority': 'HIGH',
                'type': 'HIRE',
                'skill': skill,
                'message': f"Critical shortage in {skill} capacity. Consider hiring {skill} specialist.",
                'impact': f"Gap: {gap:.1f} units, Utilization: {utilization:.0f}%"
            })
        elif gap > 0.2:  # Moderate shortfall
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'OPTIMIZE',
                'skill': skill,
                'message': f"Moderate {skill} capacity shortage. Reassign or train existing staff.",
                'impact': f"Gap: {gap:.1f} units, Utilization: {utilization:.0f}%"
            })
        elif utilization < 50:  # Underutilized
            recommendations.append({
                'priority': 'LOW',
                'type': 'REALLOCATE',
                'skill': skill,
                'message': f"{skill} capacity underutilized. Consider cross-training or reassignment.",
                'impact': f"Utilization: {utilization:.0f}%"
            })
    
    return recommendations

def generate_standup_agenda(employee_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate daily standup agenda with employee work status"""
    
    agenda_items = []
    
    for emp_id, emp_data in employee_analysis.items():
        name = emp_data['name']
        assignment = emp_data['current_assignment']
        
        if assignment:
            status = f"Working on {assignment['feature_name']}"
            progress = f"Dev: {assignment['dev_progress']:.0%}, Art: {assignment['art_progress']:.0%}"
            role = assignment['assignment_role']
            
            agenda_items.append({
                'employee': name,
                'status': status,
                'details': f"{role} - {progress}",
                'specialization': emp_data['specialization'],
                'capacity_rating': emp_data['capacity_rating'],
                'blocked': False  # Could be enhanced to detect blockers
            })
        else:
            agenda_items.append({
                'employee': name,
                'status': "Available for assignment",
                'details': f"Tier {emp_data['tier']} {emp_data['specialization']}",
                'specialization': emp_data['specialization'],
                'capacity_rating': emp_data['capacity_rating'],
                'blocked': False
            })
    
    # Sort by capacity rating (highest first) to prioritize discussion
    agenda_items.sort(key=lambda x: x['capacity_rating'], reverse=True)
    
    return agenda_items

def calculate_optimal_team_composition(production_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate optimal team composition based on production needs"""
    
    capacity_analysis = production_requirements['capacity_analysis']
    
    hiring_recommendations = []
    training_recommendations = []
    
    for skill, analysis in capacity_analysis.items():
        gap = analysis['gap']
        
        if gap > 0.3:  # Significant gap requiring action
            # Calculate ideal hire profile
            ideal_tier = 2 if gap > 1.0 else 1
            estimated_salary = estimate_salary_for_skill(skill, ideal_tier)
            
            hiring_recommendations.append({
                'skill': skill,
                'tier': ideal_tier,
                'gap_coverage': min(gap, 1.0),
                'estimated_salary': estimated_salary,
                'roi_estimate': calculate_hire_roi(gap, estimated_salary)
            })
    
    return {
        'hiring_recommendations': hiring_recommendations,
        'training_recommendations': training_recommendations,
        'total_hiring_cost': sum(rec['estimated_salary'] for rec in hiring_recommendations),
        'expected_capacity_improvement': sum(rec['gap_coverage'] for rec in hiring_recommendations)
    }

def estimate_salary_for_skill(skill: str, tier: int) -> int:
    """Estimate appropriate salary for a skill/tier combination"""
    
    base_salaries = {
        'system': 45000,
        'algorithm': 50000,
        'research': 40000,
        'design': 35000,
        'game': 42000
    }
    
    base = base_salaries.get(skill, 40000)
    tier_multiplier = 1 + (tier - 1) * 0.6
    
    return int(base * tier_multiplier)

def calculate_hire_roi(capacity_gap: float, estimated_salary: int) -> float:
    """Calculate rough ROI estimate for hiring decision"""
    
    # Simplified ROI calculation
    # In reality, this would factor in revenue per feature, time to market, etc.
    
    productivity_gain = capacity_gap * 0.5  # Conservative estimate
    annual_value = productivity_gain * 12 * 10000  # Assume $10k value per capacity unit per month
    
    roi = (annual_value - estimated_salary) / estimated_salary
    
    return roi

def generate_calendar_events(employee_analysis: Dict[str, Any], production_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate calendar events for workforce management"""
    
    events = []
    today = datetime.now()
    
    # Daily Standup
    standup_agenda = generate_standup_agenda(employee_analysis)
    events.append({
        'type': 'STANDUP',
        'title': 'Daily Team Standup',
        'date': today.strftime('%Y-%m-%d'),
        'time': '09:00',
        'duration': '30 min',
        'agenda': standup_agenda,
        'priority': 'DAILY'
    })
    
    # Product Review (weekly)
    if today.weekday() == 0:  # Monday
        events.append({
            'type': 'PRODUCT_REVIEW',
            'title': 'Weekly Product Review',
            'date': today.strftime('%Y-%m-%d'),
            'time': '14:00',
            'duration': '60 min',
            'focus': 'Inventory vs Requirements Analysis',
            'priority': 'WEEKLY'
        })
    
    # Headhunting trigger
    critical_gaps = [rec for rec in production_requirements['recommendations'] if rec['priority'] == 'HIGH']
    if critical_gaps:
        events.append({
            'type': 'HEADHUNTING',
            'title': 'Urgent: Talent Acquisition Required',
            'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'duration': '45 min',
            'critical_gaps': critical_gaps,
            'priority': 'URGENT'
        })
    
    return events