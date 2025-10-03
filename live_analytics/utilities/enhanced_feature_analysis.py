"""
Enhanced Feature Analysis System
Provides real feature names, production planning, and team assignments
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Feature name mappings based on common Startup Company features
FEATURE_NAME_MAPPINGS = {
    # Common patterns to identify features
    'landing': 'Landing Page',
    'video': 'Video Functionality', 
    'search': 'Search Engine',
    'login': 'Login System',
    'payment': 'Payment Gateway',
    'database': 'Database Layer',
    'api': 'API System',
    'email': 'Email System',
    'upload': 'File Upload',
    'ui': 'User Interface',
    'backend': 'Backend Services',
    'notification': 'Notifications',
    'localization': 'Localization',
    'compression': 'Compression',
    'analytics': 'Analytics',
    'security': 'Security',
    'social': 'Social Features',
    'mobile': 'Mobile App',
    'admin': 'Admin Panel'
}

def identify_feature_name(feature_data: dict, feature_index: int) -> str:
    """Identify the real feature name from feature data"""
    
    # Try to get explicit name first
    explicit_name = feature_data.get('name', '').strip()
    if explicit_name and explicit_name != f'Feature_{feature_index}':
        return explicit_name
    
    # Look at requirements to infer feature type
    requirements = feature_data.get('requirements', {})
    
    # Pattern matching based on requirements
    if 'VideoPlaybackModule' in requirements:
        return 'Video Functionality'
    elif 'AuthenticationModule' in requirements:
        return 'Login System'
    elif 'PaymentGatewayModule' in requirements:
        return 'Payment Gateway'
    elif 'SearchModule' in requirements:
        return 'Search Engine'
    elif 'UiComponent' in requirements and 'BackendComponent' in requirements:
        if 'GraphicsComponent' in requirements:
            return 'Landing Page'
        else:
            return 'Basic Feature'
    elif 'FrontendModule' in requirements:
        return 'Frontend Feature'
    elif 'BackendModule' in requirements:
        return 'Backend Feature'
    
    # Check feature description or other fields
    description = feature_data.get('description', '').lower()
    for keyword, name in FEATURE_NAME_MAPPINGS.items():
        if keyword in description:
            return name
    
    # Fallback to generic name
    return f'Feature {feature_index + 1}'

def analyze_production_queue(data: dict) -> Dict:
    """Analyze current production plans and queue status"""
    production_plans = data.get('productionPlans', [])
    
    analysis = {
        'active_plans': len(production_plans),
        'planned_production': {},
        'plan_details': [],
        'completion_estimates': {}
    }
    
    for plan in production_plans:
        plan_name = plan.get('name', 'Unnamed Plan')
        production = plan.get('production', {})
        
        plan_info = {
            'name': plan_name,
            'id': plan.get('id', ''),
            'components': production,
            'total_items': sum(production.values()) if production else 0,
            'skip_missing': plan.get('skipModulesWithMissingRequirements', False)
        }
        
        analysis['plan_details'].append(plan_info)
        
        # Aggregate planned production
        for component, count in production.items():
            analysis['planned_production'][component] = analysis['planned_production'].get(component, 0) + count
    
    return analysis

def calculate_team_assignments(missing_components: Dict[str, int], employee_data: dict) -> Dict:
    """Calculate optimal team assignments for missing components"""
    
    # Component to employee type mapping
    component_assignments = {
        'UiComponent': 'UI/UX Designer',
        'BackendComponent': 'Backend Developer', 
        'FrontendModule': 'Frontend Developer',
        'GraphicsComponent': 'Graphic Designer',
        'BlueprintComponent': 'Systems Architect',
        'VideoPlaybackModule': 'Media Developer',
        'VideoComponent': 'Media Developer',
        'NetworkComponent': 'Network Engineer',
        'DatabaseModule': 'Database Developer',
        'SecurityModule': 'Security Engineer',
        'ApiModule': 'API Developer',
        'WireframeComponent': 'UI/UX Designer',
        'InterfaceModule': 'Frontend Developer',
        'BackendModule': 'Backend Developer'
    }
    
    assignments = {}
    workload_summary = {}
    
    for component, needed_count in missing_components.items():
        if needed_count <= 0:
            continue
            
        required_role = component_assignments.get(component, 'General Developer')
        
        assignments[component] = {
            'component': component,
            'needed': needed_count,
            'assigned_role': required_role,
            'priority': calculate_component_priority(component, missing_components),
            'estimated_days': estimate_development_time(component, needed_count)
        }
        
        # Track workload by role
        if required_role not in workload_summary:
            workload_summary[required_role] = {'components': 0, 'total_items': 0, 'estimated_days': 0}
        
        workload_summary[required_role]['components'] += 1
        workload_summary[required_role]['total_items'] += needed_count
        workload_summary[required_role]['estimated_days'] += assignments[component]['estimated_days']
    
    return {
        'assignments': assignments,
        'workload_by_role': workload_summary,
        'total_missing_components': sum(missing_components.values()),
        'roles_needed': len(workload_summary)
    }

def calculate_component_priority(component: str, all_missing: Dict[str, int]) -> str:
    """Calculate priority level for component production"""
    
    # High priority components (blockers for multiple features)
    high_priority = ['BackendComponent', 'FrontendModule', 'UiComponent']
    
    # Medium priority (specialized but important)
    medium_priority = ['GraphicsComponent', 'BlueprintComponent', 'InterfaceModule']
    
    if component in high_priority:
        return 'High'
    elif component in medium_priority:
        return 'Medium'
    else:
        return 'Low'

def estimate_development_time(component: str, count: int) -> int:
    """Estimate development time in days"""
    
    # Base time estimates per component type
    base_times = {
        'UiComponent': 1,
        'BackendComponent': 2,
        'FrontendModule': 3,
        'GraphicsComponent': 1,
        'BlueprintComponent': 2,
        'VideoPlaybackModule': 4,
        'VideoComponent': 2,
        'NetworkComponent': 3,
        'InterfaceModule': 2,
        'BackendModule': 4,
        'WireframeComponent': 1
    }
    
    base_time = base_times.get(component, 2)  # Default 2 days
    return base_time * count

def get_comprehensive_feature_analysis(data: dict) -> Dict:
    """Get comprehensive analysis including names, production, and assignments"""
    
    feature_instances = data.get('featureInstances', [])
    inventory = data.get('inventory', {})
    
    analysis = {
        'features': [],
        'missing_components': {},
        'production_analysis': analyze_production_queue(data),
        'team_assignments': {},
        'feature_summary': {
            'total': len(feature_instances),
            'ready_to_build': 0,
            'blocked': 0,
            'partially_ready': 0
        }
    }
    
    # Analyze each feature
    for i, feature in enumerate(feature_instances):
        feature_name = identify_feature_name(feature, i)
        requirements = feature.get('requirements', {})
        
        feature_analysis = {
            'id': i,
            'name': feature_name,
            'original_name': feature.get('name', f'Feature_{i}'),
            'requirements': requirements,
            'missing_components': {},
            'status': 'unknown',
            'readiness_score': 0,
            'blocking_components': []
        }
        
        # Check component availability
        total_needed = 0
        total_available = 0
        
        for component, needed in requirements.items():
            available = inventory.get(component, 0)
            total_needed += needed
            total_available += min(available, needed)
            
            if available < needed:
                shortage = needed - available
                feature_analysis['missing_components'][component] = shortage
                feature_analysis['blocking_components'].append(component)
                
                # Add to global missing components
                analysis['missing_components'][component] = analysis['missing_components'].get(component, 0) + shortage
        
        # Calculate readiness
        if total_needed > 0:
            feature_analysis['readiness_score'] = (total_available / total_needed) * 100
        else:
            feature_analysis['readiness_score'] = 100
            
        # Determine status
        if feature_analysis['readiness_score'] >= 100:
            feature_analysis['status'] = 'ready'
            analysis['feature_summary']['ready_to_build'] += 1
        elif feature_analysis['readiness_score'] >= 50:
            feature_analysis['status'] = 'partially_ready'
            analysis['feature_summary']['partially_ready'] += 1
        else:
            feature_analysis['status'] = 'blocked'
            analysis['feature_summary']['blocked'] += 1
        
        analysis['features'].append(feature_analysis)
    
    # Calculate team assignments for missing components
    analysis['team_assignments'] = calculate_team_assignments(
        analysis['missing_components'], 
        data.get('employees', {})
    )
    
    return analysis