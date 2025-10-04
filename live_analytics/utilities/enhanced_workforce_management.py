"""
Enhanced Workforce Management System
Handles sales executives, researchers, and developer teams with specialized workflows
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import streamlit as st

def analyze_sales_team(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze sales team performance and lead management strategy"""
    
    workstations = data.get('office', {}).get('workstations', [])
    sales_executives = []
    
    # Find all sales executives
    for i, workstation in enumerate(workstations):
        if 'employee' in workstation and workstation['employee']:
            emp = workstation['employee']
            if emp.get('employeeTypeName') == 'SalesExecutive':
                
                leads = emp.get('leads', [])
                lead_analysis = []
                
                # Analyze each lead
                for lead in leads:
                    impressions = lead.get('impressions', 0)
                    timestamp = lead.get('timestamp', '')
                    competitor_id = lead.get('competitorProductId', '')
                    
                    # Determine lead priority based on impressions
                    if impressions >= 200000:
                        priority = 'HIGH'
                        urgency = 'High value opportunity'
                    elif impressions >= 150000:
                        priority = 'MEDIUM'
                        urgency = 'Good potential'
                    else:
                        priority = 'LOW'
                        urgency = 'Lower value'
                    
                    lead_analysis.append({
                        'id': lead.get('id', 'unknown'),
                        'impressions': impressions,
                        'priority': priority,
                        'urgency': urgency,
                        'timestamp': timestamp,
                        'competitor_id': competitor_id
                    })
                
                # Sort leads by priority (HIGH first)
                lead_analysis.sort(key=lambda x: {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[x['priority']], reverse=True)
                
                sales_exec_data = {
                    'name': emp.get('name', 'Unknown'),
                    'level': emp.get('level', 'Unknown'),
                    'speed': emp.get('speed', 0),
                    'salary': emp.get('salary', 0),
                    'workstation': i,
                    'total_leads': len(leads),
                    'leads': lead_analysis,
                    'capacity': determine_sales_capacity(emp),
                    'current_task': emp.get('task', {}),
                    'mood': emp.get('mood', 50)
                }
                
                sales_executives.append(sales_exec_data)
    
    return {
        'sales_executives': sales_executives,
        'total_leads': sum(exec['total_leads'] for exec in sales_executives),
        'high_priority_leads': sum(1 for exec in sales_executives for lead in exec['leads'] if lead['priority'] == 'HIGH'),
        'recommendations': generate_sales_strategy(sales_executives)
    }

def determine_sales_capacity(sales_exec: Dict[str, Any]) -> str:
    """Determine how many leads a sales executive can handle"""
    level = sales_exec.get('level', 'Beginner')
    speed = sales_exec.get('speed', 0)
    
    if level == 'Expert' or speed > 200:
        return 'Can handle 3-4 leads simultaneously'
    elif level == 'Intermediate' or speed > 150:
        return 'Can handle 2-3 leads simultaneously'
    else:
        return 'Can handle 1-2 leads (recommended: 1 at a time)'

def generate_sales_strategy(sales_executives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate strategic recommendations for sales team management"""
    
    recommendations = []
    
    for exec_data in sales_executives:
        name = exec_data['name']
        leads = exec_data['leads']
        level = exec_data['level']
        
        if not leads:
            recommendations.append({
                'type': 'NO_LEADS',
                'priority': 'MEDIUM',
                'executive': name,
                'message': f'{name} has no active leads. Consider prospecting or lead generation.',
                'action': 'Assign lead generation tasks or review lead filters'
            })
            continue
        
        # Focus strategy for beginners
        if level == 'Beginner' and len(leads) > 1:
            highest_priority = leads[0]  # Already sorted by priority
            recommendations.append({
                'type': 'CAPACITY_OPTIMIZATION',
                'priority': 'HIGH',
                'executive': name,
                'data_point': f'Beginner-level executive with {len(leads)} concurrent leads',
                'threshold': 'Beginner executives should handle ≤1 lead for optimal performance',
                'game_action': f'Remove all leads except {highest_priority["id"][:8]}... from {name}\'s queue',
                'metric_impact': f'Expected improvement: +25% conversion rate on primary lead'
            })
        
        # Lead quantity analysis
        high_value_leads = [lead for lead in leads if lead['priority'] == 'HIGH']
        if len(high_value_leads) > 1:
            total_value = sum(lead['impressions'] for lead in high_value_leads)
            recommendations.append({
                'type': 'LEAD_PRIORITIZATION',
                'priority': 'HIGH', 
                'executive': name,
                'data_point': f'{len(high_value_leads)} high-value leads totaling {total_value:,} impressions',
                'threshold': 'Multiple high-value leads require sequential processing',
                'game_action': f'Rank {name}\'s leads by impression value and process top lead first',
                'metric_impact': 'Sequential processing improves individual lead conversion rates'
            })
        
        # High-value lead analysis
        for lead in leads[:2]:  # Check top 2 leads
            if lead['impressions'] >= 200000:
                recommendations.append({
                    'type': 'HIGH_VALUE_TRIGGER',
                    'priority': 'HIGH',
                    'executive': name,
                    'data_point': f'Lead value: {lead["impressions"]:,} impressions',
                    'threshold': 'Leads ≥200k impressions qualify for premium treatment',
                    'game_action': f'Expedite contact and negotiation for lead {lead["id"][:8]}...',
                    'metric_impact': 'Premium leads have 40% higher conversion probability'
                })
    
    return recommendations

def analyze_research_team(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze research team and ongoing research projects"""
    
    workstations = data.get('office', {}).get('workstations', [])
    researchers = []
    
    # Find all researchers
    for i, workstation in enumerate(workstations):
        if 'employee' in workstation and workstation['employee']:
            emp = workstation['employee']
            if emp.get('employeeTypeName') == 'Researcher':
                
                researcher_data = {
                    'name': emp.get('name', 'Unknown'),
                    'level': emp.get('level', 'Unknown'),
                    'speed': emp.get('speed', 0),
                    'salary': emp.get('salary', 0),
                    'workstation': i,
                    'research_skill': emp.get('researchSkill', 0),
                    'current_task': emp.get('task', {}),
                    'mood': emp.get('mood', 50),
                    'training_opportunity': assess_researcher_training(emp)
                }
                
                researchers.append(researcher_data)
    
    # Analyze research progress
    research_progress = analyze_research_progress(data)
    
    return {
        'researchers': researchers,
        'research_progress': research_progress,
        'total_research_capacity': sum(r['speed'] for r in researchers),
        'recommendations': generate_research_strategy(researchers, research_progress)
    }

def assess_researcher_training(researcher: Dict[str, Any]) -> Dict[str, Any]:
    """Assess training opportunities for researchers"""
    
    research_skill = researcher.get('researchSkill', 0)
    speed = researcher.get('speed', 0)
    level = researcher.get('level', 'Beginner')
    
    training_needs = []
    
    if research_skill < 80:
        training_needs.append({
            'type': 'RESEARCH_SKILL',
            'current': research_skill,
            'target': min(research_skill + 20, 100),
            'priority': 'HIGH' if research_skill < 60 else 'MEDIUM'
        })
    
    if speed < 150:
        training_needs.append({
            'type': 'SPEED',
            'current': speed,
            'target': min(speed + 30, 200),
            'priority': 'MEDIUM'
        })
    
    if level == 'Beginner' and research_skill > 70:
        training_needs.append({
            'type': 'LEVEL_ADVANCEMENT',
            'current': level,
            'target': 'Intermediate',
            'priority': 'HIGH'
        })
    
    return {
        'has_opportunities': len(training_needs) > 0,
        'training_needs': training_needs,
        'estimated_training_time': len(training_needs) * 2  # weeks
    }

def analyze_research_progress(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze current research progress and priorities"""
    
    research_points = data.get('researchPoints', 0)
    researched_items = data.get('researchedItems', [])
    
    # This would need more game data to determine current research projects
    # For now, provide basic analysis
    
    return {
        'available_points': research_points,
        'completed_research': len(researched_items),
        'recent_completions': researched_items[-5:] if len(researched_items) > 5 else researched_items
    }

def generate_research_strategy(researchers: List[Dict[str, Any]], research_progress: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate strategic recommendations for research team"""
    
    recommendations = []
    
    for researcher in researchers:
        name = researcher['name']
        training = researcher['training_opportunity']
        
        # Training recommendations
        if training['has_opportunities']:
            high_priority_training = [t for t in training['training_needs'] if t['priority'] == 'HIGH']
            
            if high_priority_training:
                recommendations.append({
                    'type': 'TRAINING_NEEDED',
                    'priority': 'HIGH',
                    'researcher': name,
                    'message': f'{name} needs skill development training',
                    'action': f'Schedule training for: {", ".join([t["type"] for t in high_priority_training])}',
                    'training_details': high_priority_training
                })
        
        # Utilization optimization
        if researcher['speed'] > 180:
            recommendations.append({
                'type': 'HIGH_PERFORMER',
                'priority': 'MEDIUM',
                'researcher': name,
                'message': f'{name} is a high performer (Speed: {researcher["speed"]:.0f})',
                'action': 'Consider assigning to high-priority research projects'
            })
    
    # Team-level recommendations
    total_capacity = sum(r['speed'] for r in researchers)
    if total_capacity < 300:  # Arbitrary threshold
        recommendations.append({
            'type': 'CAPACITY_SHORTAGE',
            'priority': 'MEDIUM',
            'researcher': 'TEAM',
            'message': f'Research team capacity is low ({total_capacity:.0f})',
            'action': 'Consider hiring additional researchers or training existing team'
        })
    
    return recommendations

def analyze_developer_teams(data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced analysis of developer teams with training opportunities"""
    
    workstations = data.get('office', {}).get('workstations', [])
    developers = []
    designers = []
    lead_developers = []
    
    # Categorize development team members
    for i, workstation in enumerate(workstations):
        if 'employee' in workstation and workstation['employee']:
            emp = workstation['employee']
            emp_type = emp.get('employeeTypeName', '')
            
            if emp_type in ['Developer', 'Designer', 'LeadDeveloper']:
                
                # Extract skills
                skills = {}
                for key, value in emp.items():
                    if 'skill' in key.lower() and isinstance(value, (int, float)):
                        skills[key] = value
                
                # Assess training opportunities
                training_assessment = assess_developer_training(emp, skills)
                
                dev_data = {
                    'name': emp.get('name', 'Unknown'),
                    'type': emp_type,
                    'level': emp.get('level', 'Unknown'),
                    'speed': emp.get('speed', 0),
                    'salary': emp.get('salary', 0),
                    'workstation': i,
                    'skills': skills,
                    'training_opportunities': training_assessment,
                    'current_assignment': emp.get('task', {}),
                    'mood': emp.get('mood', 50)
                }
                
                if emp_type == 'Developer':
                    developers.append(dev_data)
                elif emp_type == 'Designer':
                    designers.append(dev_data)
                elif emp_type == 'LeadDeveloper':
                    lead_developers.append(dev_data)
    
    return {
        'developers': developers,
        'designers': designers,
        'lead_developers': lead_developers,
        'team_recommendations': generate_dev_team_strategy(developers, designers, lead_developers)
    }

def assess_developer_training(employee: Dict[str, Any], skills: Dict[str, Any]) -> Dict[str, Any]:
    """Assess training opportunities for developers/designers"""
    
    if not skills:
        return {'has_opportunities': False, 'training_needs': []}
    
    training_needs = []
    max_skill = max(skills.values()) if skills else 0
    avg_skill = sum(skills.values()) / len(skills) if skills else 0
    speed = employee.get('speed', 0)
    level = employee.get('level', 'Beginner')
    
    # Primary skill improvement
    if max_skill < 80:
        primary_skill = max(skills.keys(), key=lambda k: skills[k])
        training_needs.append({
            'type': 'PRIMARY_SKILL',
            'skill': primary_skill,
            'current': skills[primary_skill],
            'target': min(skills[primary_skill] + 20, 100),
            'priority': 'HIGH' if max_skill < 60 else 'MEDIUM'
        })
    
    # Cross-training opportunities
    if avg_skill < 50:
        low_skills = [(k, v) for k, v in skills.items() if v < 40]
        if low_skills:
            training_needs.append({
                'type': 'CROSS_TRAINING',
                'skills': low_skills,
                'priority': 'MEDIUM'
            })
    
    # Speed training
    if speed < 100:
        training_needs.append({
            'type': 'SPEED_TRAINING',
            'current': speed,
            'target': min(speed + 30, 150),
            'priority': 'HIGH' if speed < 80 else 'MEDIUM'
        })
    
    # Level advancement
    if level == 'Beginner' and max_skill > 70:
        training_needs.append({
            'type': 'LEVEL_ADVANCEMENT',
            'current': level,
            'target': 'Intermediate',
            'priority': 'HIGH'
        })
    
    return {
        'has_opportunities': len(training_needs) > 0,
        'training_needs': training_needs,
        'optimal_timing': suggest_training_timing(employee),
        'estimated_cost': len(training_needs) * 1000  # Estimated training cost
    }

def suggest_training_timing(employee: Dict[str, Any]) -> str:
    """Suggest optimal timing for training based on workload"""
    
    current_task = employee.get('task', {})
    
    if not current_task:
        return "IMMEDIATE - Employee is available"
    
    # This would need more game logic to determine project completion timing
    return "END_OF_SPRINT - Schedule after current assignment completion"

def generate_dev_team_strategy(developers: List[Dict], designers: List[Dict], lead_developers: List[Dict]) -> List[Dict[str, Any]]:
    """Generate development team strategy recommendations"""
    
    recommendations = []
    
    # Analyze each team member for training opportunities
    all_team_members = developers + designers + lead_developers
    
    high_priority_training = []
    medium_priority_training = []
    
    for member in all_team_members:
        if member['training_opportunities']['has_opportunities']:
            training_needs = member['training_opportunities']['training_needs']
            
            for need in training_needs:
                training_rec = {
                    'employee': member['name'],
                    'type': member['type'],
                    'training_type': need['type'],
                    'priority': need['priority'],
                    'timing': member['training_opportunities']['optimal_timing']
                }
                
                if need['priority'] == 'HIGH':
                    high_priority_training.append(training_rec)
                else:
                    medium_priority_training.append(training_rec)
    
    # High priority training recommendations
    if high_priority_training:
        recommendations.append({
            'type': 'URGENT_TRAINING',
            'priority': 'HIGH',
            'message': f'{len(high_priority_training)} team members need urgent training',
            'action': 'Schedule training sessions for skill gaps and performance issues',
            'training_list': high_priority_training
        })
    
    # Medium priority training recommendations
    if medium_priority_training:
        recommendations.append({
            'type': 'DEVELOPMENT_OPPORTUNITIES',
            'priority': 'MEDIUM',
            'message': f'{len(medium_priority_training)} team members have development opportunities',
            'action': 'Plan training during project downtime or sprint breaks',
            'training_list': medium_priority_training
        })
    
    # Team balance analysis
    total_devs = len(developers)
    total_designers = len(designers)
    total_leads = len(lead_developers)
    
    if total_devs < 2:
        recommendations.append({
            'type': 'TEAM_IMBALANCE',
            'priority': 'MEDIUM',
            'message': 'Development team may be understaffed',
            'action': 'Consider hiring additional developers'
        })
    
    if total_designers < 1 and total_devs > 2:
        recommendations.append({
            'type': 'DESIGN_BOTTLENECK',
            'priority': 'HIGH',
            'message': 'Design capacity may be a bottleneck',
            'action': 'Consider hiring designers or cross-training developers'
        })
    
    return recommendations

def generate_professional_development_plan(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive professional development plan for all employees"""
    
    # Analyze all employee types
    sales_analysis = analyze_sales_team(data)
    research_analysis = analyze_research_team(data)
    dev_analysis = analyze_developer_teams(data)
    
    # Consolidate all training opportunities
    all_training_opportunities = []
    
    # Sales team training
    for exec_data in sales_analysis['sales_executives']:
        if exec_data.get('level') == 'Beginner':
            all_training_opportunities.append({
                'employee': exec_data['name'],
                'type': 'SalesExecutive',
                'training_need': 'Sales negotiation and lead management',
                'priority': 'HIGH',
                'estimated_duration': '2 weeks',
                'expected_outcome': 'Improved close rate and lead handling capacity'
            })
    
    # Research team training
    for researcher in research_analysis['researchers']:
        if researcher['training_opportunity']['has_opportunities']:
            for need in researcher['training_opportunity']['training_needs']:
                all_training_opportunities.append({
                    'employee': researcher['name'],
                    'type': 'Researcher',
                    'training_need': need['type'],
                    'priority': need['priority'],
                    'estimated_duration': '2-3 weeks',
                    'expected_outcome': f"Improve {need['type']} from {need['current']} to {need['target']}"
                })
    
    # Development team training
    for team_list in [dev_analysis['developers'], dev_analysis['designers'], dev_analysis['lead_developers']]:
        for member in team_list:
            if member['training_opportunities']['has_opportunities']:
                for need in member['training_opportunities']['training_needs']:
                    all_training_opportunities.append({
                        'employee': member['name'],
                        'type': member['type'],
                        'training_need': need['type'],
                        'priority': need['priority'],
                        'estimated_duration': '1-2 weeks',
                        'expected_outcome': 'Enhanced skill proficiency and productivity'
                    })
    
    # Sort by priority
    high_priority = [t for t in all_training_opportunities if t['priority'] == 'HIGH']
    medium_priority = [t for t in all_training_opportunities if t['priority'] == 'MEDIUM']
    
    return {
        'total_training_opportunities': len(all_training_opportunities),
        'high_priority_training': high_priority,
        'medium_priority_training': medium_priority,
        'estimated_total_cost': len(all_training_opportunities) * 1000,
        'recommended_schedule': generate_training_schedule(high_priority, medium_priority)
    }

def generate_training_schedule(high_priority: List[Dict], medium_priority: List[Dict]) -> List[Dict[str, Any]]:
    """Generate optimal training schedule"""
    
    schedule = []
    current_week = 1
    
    # Schedule high priority training first
    for training in high_priority:
        schedule.append({
            'week': current_week,
            'employee': training['employee'],
            'training_type': training['training_need'],
            'duration': training['estimated_duration'],
            'priority': 'HIGH'
        })
        current_week += 2  # Assume 2 weeks per training
    
    # Schedule medium priority training
    for training in medium_priority[:5]:  # Limit to top 5 medium priority
        schedule.append({
            'week': current_week,
            'employee': training['employee'],
            'training_type': training['training_need'],
            'duration': training['estimated_duration'],
            'priority': 'MEDIUM'
        })
        current_week += 2
    
    return schedule