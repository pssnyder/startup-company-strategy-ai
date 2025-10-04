"""
Focused Team Management System
Separates team members by their management needs and workflow types
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import streamlit as st

def analyze_manageable_team_members(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze only team members with adjustable work queues for daily standup"""
    
    workstations = data.get('office', {}).get('workstations', [])
    
    # Roles that have adjustable work queues for daily standup
    manageable_roles = ['Developer', 'Designer', 'LeadDeveloper', 'Marketer', 'SysAdmin']
    
    # Filter out CEO and other special roles
    excluded_names = ['Alex Corbin']  # CEO
    
    manageable_team = []
    
    for i, workstation in enumerate(workstations):
        if 'employee' in workstation and workstation['employee']:
            emp = workstation['employee']
            name = emp.get('name', '')
            role = emp.get('employeeTypeName', '')
            
            # Include only manageable roles and exclude CEO
            if role in manageable_roles and name not in excluded_names:
                
                # Extract skills for work queue analysis
                skills = {}
                for key, value in emp.items():
                    if 'skill' in key.lower() and isinstance(value, (int, float)):
                        skills[key] = value
                
                # Determine current work assignment
                current_assignment = analyze_current_assignment(emp, data)
                
                # Calculate work queue capacity
                queue_capacity = calculate_queue_capacity(emp, skills)
                
                team_member = {
                    'name': name,
                    'role': role,
                    'level': emp.get('level', 'Beginner'),
                    'speed': emp.get('speed', 0),
                    'salary': emp.get('salary', 0),
                    'workstation': i,
                    'skills': skills,
                    'current_assignment': current_assignment,
                    'queue_capacity': queue_capacity,
                    'mood': emp.get('mood', 50),
                    'effectiveness': emp.get('effectiveness', 100),
                    'training_status': assess_training_readiness(emp, skills)
                }
                
                manageable_team.append(team_member)
    
    return {
        'team_members': manageable_team,
        'total_capacity': sum(tm['queue_capacity']['total_capacity'] for tm in manageable_team),
        'work_distribution': analyze_work_distribution(manageable_team),
        'queue_recommendations': generate_queue_recommendations(manageable_team)
    }

def analyze_current_assignment(employee: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze what the employee is currently working on"""
    
    # Check if employee has a current task or assignment
    current_task = employee.get('task', {})
    
    if current_task:
        return {
            'has_assignment': True,
            'task_type': current_task.get('type', 'Unknown'),
            'description': current_task.get('description', 'Working on assignment'),
            'progress': current_task.get('progress', 0),
            'estimated_completion': estimate_completion_time(current_task, employee)
        }
    else:
        return {
            'has_assignment': False,
            'status': 'Available for new assignment',
            'ready_for_work': True
        }

def calculate_queue_capacity(employee: Dict[str, Any], skills: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate how much work this employee can handle in their queue"""
    
    speed = employee.get('speed', 0)
    level = employee.get('level', 'Beginner')
    
    # Base capacity calculation
    level_multiplier = {'Beginner': 1.0, 'Intermediate': 1.5, 'Advanced': 2.0, 'Expert': 2.5}.get(level, 1.0)
    speed_factor = speed / 100  # Normalize speed
    
    base_capacity = speed_factor * level_multiplier
    
    # Skill-based capacity modifiers
    if skills:
        max_skill = max(skills.values())
        skill_modifier = 1 + (max_skill / 200)  # Bonus for high skills
    else:
        skill_modifier = 1.0
    
    total_capacity = base_capacity * skill_modifier
    
    return {
        'total_capacity': total_capacity,
        'concurrent_tasks': min(int(total_capacity / 0.5), 3),  # Max 3 concurrent tasks
        'efficiency_rating': 'High' if total_capacity > 2.0 else 'Medium' if total_capacity > 1.5 else 'Low',
        'recommended_workload': calculate_recommended_workload(total_capacity)
    }

def calculate_recommended_workload(capacity: float) -> str:
    """Recommend optimal workload based on capacity"""
    
    if capacity >= 2.5:
        return "Can handle 2-3 major features or 3-4 smaller tasks"
    elif capacity >= 2.0:
        return "Can handle 1-2 major features or 2-3 smaller tasks"
    elif capacity >= 1.5:
        return "Can handle 1 major feature or 2 smaller tasks"
    else:
        return "Should focus on 1 task at a time"

def assess_training_readiness(employee: Dict[str, Any], skills: Dict[str, Any]) -> Dict[str, Any]:
    """Assess if employee is ready for training during downtime"""
    
    current_assignment = employee.get('task', {})
    has_active_work = bool(current_assignment)
    
    # Check skill gaps
    training_needs = []
    if skills:
        max_skill = max(skills.values())
        avg_skill = sum(skills.values()) / len(skills)
        
        if max_skill < 80:
            training_needs.append('Primary skill improvement')
        if avg_skill < 50:
            training_needs.append('Cross-skill development')
    
    speed = employee.get('speed', 0)
    if speed < 120:
        training_needs.append('Speed training')
    
    return {
        'ready_for_training': not has_active_work and len(training_needs) > 0,
        'training_needs': training_needs,
        'optimal_timing': 'Now' if not has_active_work else 'After current assignment',
        'estimated_duration': len(training_needs) * 3  # days
    }

def analyze_work_distribution(team_members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze how work is distributed across the team"""
    
    role_distribution = {}
    capacity_utilization = {}
    
    for member in team_members:
        role = member['role']
        
        if role not in role_distribution:
            role_distribution[role] = {'count': 0, 'total_capacity': 0, 'busy_count': 0}
        
        role_distribution[role]['count'] += 1
        role_distribution[role]['total_capacity'] += member['queue_capacity']['total_capacity']
        
        if member['current_assignment']['has_assignment']:
            role_distribution[role]['busy_count'] += 1
    
    # Calculate utilization rates
    for role, stats in role_distribution.items():
        if stats['count'] > 0:
            capacity_utilization[role] = {
                'utilization_rate': (stats['busy_count'] / stats['count']) * 100,
                'avg_capacity': stats['total_capacity'] / stats['count'],
                'available_members': stats['count'] - stats['busy_count']
            }
    
    return {
        'role_distribution': role_distribution,
        'capacity_utilization': capacity_utilization,
        'bottlenecks': identify_capacity_bottlenecks(capacity_utilization)
    }

def identify_capacity_bottlenecks(utilization: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """Identify roles that are bottlenecks"""
    
    bottlenecks = []
    
    for role, stats in utilization.items():
        if stats['utilization_rate'] > 80:  # High utilization
            bottlenecks.append({
                'role': role,
                'issue': f"High utilization ({stats['utilization_rate']:.0f}%)",
                'severity': 'HIGH' if stats['utilization_rate'] > 90 else 'MEDIUM',
                'recommendation': f"Consider hiring additional {role} or redistributing work"
            })
        elif stats['available_members'] == 0:  # Everyone busy
            bottlenecks.append({
                'role': role,
                'issue': "All team members are busy",
                'severity': 'HIGH',
                'recommendation': f"Prioritize {role} tasks or consider additional resources"
            })
    
    return bottlenecks

def generate_queue_recommendations(team_members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate recommendations for work queue management"""
    
    recommendations = []
    
    # Analyze individual members
    for member in team_members:
        name = member['name']
        capacity = member['queue_capacity']
        assignment = member['current_assignment']
        training = member['training_status']
        
        # Overloaded members
        if capacity['efficiency_rating'] == 'Low' and assignment['has_assignment']:
            recommendations.append({
                'type': 'REDUCE_WORKLOAD',
                'member': name,
                'priority': 'HIGH',
                'message': f"{name} may be overloaded - consider reducing queue",
                'action': f"Review {name}'s current assignments and redistribute if possible"
            })
        
        # Underutilized members
        if capacity['efficiency_rating'] == 'High' and not assignment['has_assignment']:
            recommendations.append({
                'type': 'ADD_WORK',
                'member': name,
                'priority': 'MEDIUM',
                'message': f"{name} has high capacity and is available",
                'action': f"Assign priority tasks to {name} - can handle {capacity['recommended_workload']}"
            })
        
        # Training opportunities
        if training['ready_for_training']:
            recommendations.append({
                'type': 'SCHEDULE_TRAINING',
                'member': name,
                'priority': 'LOW',
                'message': f"{name} is ready for skill development",
                'action': f"Schedule training: {', '.join(training['training_needs'])}"
            })
    
    return recommendations

def analyze_research_team_performance(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze research team performance and research point generation"""
    
    workstations = data.get('office', {}).get('workstations', [])
    researchers = []
    
    for workstation in workstations:
        if 'employee' in workstation and workstation['employee']:
            emp = workstation['employee']
            if emp.get('employeeTypeName') == 'Researcher':
                researchers.append({
                    'name': emp.get('name'),
                    'speed': emp.get('speed', 0),
                    'level': emp.get('level', 'Beginner'),
                    'research_skill': emp.get('researchSkill', 0),
                    'salary': emp.get('salary', 0),
                    'mood': emp.get('mood', 50)
                })
    
    # Calculate research points per day
    total_research_speed = sum(r['speed'] for r in researchers)
    daily_research_points = calculate_daily_research_generation(total_research_speed, researchers)
    
    # Analyze research priorities
    current_research_points = data.get('researchPoints', 0)
    research_priorities = determine_research_priorities(current_research_points, daily_research_points)
    
    return {
        'researchers': researchers,
        'total_researchers': len(researchers),
        'total_research_speed': total_research_speed,
        'daily_research_points': daily_research_points,
        'current_research_points': current_research_points,
        'research_priorities': research_priorities,
        'training_recommendations': generate_research_training_recommendations(researchers, daily_research_points)
    }

def calculate_daily_research_generation(total_speed: float, researchers: List[Dict[str, Any]]) -> float:
    """Calculate estimated research points generated per day"""
    
    # Base calculation: speed translates to research points
    # This is a simplified calculation - actual game mechanics may vary
    base_points_per_day = total_speed * 0.1  # Adjust multiplier based on actual game data
    
    # Factor in skill levels
    skill_bonus = 0
    for researcher in researchers:
        research_skill = researcher.get('research_skill', 0)
        skill_bonus += research_skill * 0.01  # Bonus from high research skills
    
    return base_points_per_day + skill_bonus

def determine_research_priorities(current_points: int, daily_generation: float) -> List[Dict[str, Any]]:
    """Determine research priorities based on points and generation rate"""
    
    priorities = []
    
    # Research items and their costs (example - would need actual game data)
    research_items = [
        {'name': 'Basic Algorithm', 'cost': 50, 'priority': 'HIGH'},
        {'name': 'Advanced UI', 'cost': 150, 'priority': 'MEDIUM'},
        {'name': 'Security Framework', 'cost': 200, 'priority': 'HIGH'},
        {'name': 'AI Components', 'cost': 300, 'priority': 'MEDIUM'},
        {'name': 'Cloud Integration', 'cost': 500, 'priority': 'LOW'}
    ]
    
    for item in research_items:
        cost = item['cost']
        days_to_afford = cost / max(daily_generation, 1)
        
        if current_points >= cost:
            urgency = 'AVAILABLE_NOW'
        elif days_to_afford <= 7:
            urgency = 'AVAILABLE_SOON'
        elif days_to_afford <= 30:
            urgency = 'MEDIUM_TERM'
        else:
            urgency = 'LONG_TERM'
        
        priorities.append({
            'item': item['name'],
            'cost': cost,
            'priority': item['priority'],
            'urgency': urgency,
            'days_to_afford': days_to_afford
        })
    
    return priorities

def generate_research_training_recommendations(researchers: List[Dict[str, Any]], daily_generation: float) -> List[Dict[str, Any]]:
    """Generate training recommendations to improve research speed"""
    
    recommendations = []
    
    # Analyze if research generation is too slow
    if daily_generation < 20:  # Threshold for slow research
        recommendations.append({
            'type': 'SPEED_UP_RESEARCH',
            'priority': 'HIGH',
            'message': f"Research generation is slow ({daily_generation:.1f} points/day)",
            'action': "Consider training researchers or hiring additional research staff"
        })
    
    # Individual researcher recommendations
    for researcher in researchers:
        name = researcher['name']
        speed = researcher['speed']
        research_skill = researcher.get('research_skill', 0)
        
        if speed < 150:
            recommendations.append({
                'type': 'SPEED_TRAINING',
                'member': name,
                'priority': 'MEDIUM',
                'message': f"{name} could benefit from speed training ({speed} current)",
                'action': f"Train {name} to improve research output"
            })
        
        if research_skill < 80:
            recommendations.append({
                'type': 'SKILL_TRAINING',
                'member': name,
                'priority': 'HIGH',
                'message': f"{name} needs research skill improvement ({research_skill} current)",
                'action': f"Focus on research skill training for {name}"
            })
    
    return recommendations

def estimate_completion_time(task: Dict[str, Any], employee: Dict[str, Any]) -> str:
    """Estimate when current task will be completed"""
    
    progress = task.get('progress', 0)
    remaining_work = 1 - progress
    speed = employee.get('speed', 100)
    
    # Simplified calculation
    estimated_hours = (remaining_work * 40) / (speed / 100)  # Assuming 40 hour base work
    
    if estimated_hours < 8:
        return "Today"
    elif estimated_hours < 24:
        return "Tomorrow"
    elif estimated_hours < 120:  # 5 days
        return f"{int(estimated_hours / 8)} working days"
    else:
        return "Next week+"