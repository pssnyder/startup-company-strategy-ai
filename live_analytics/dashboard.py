import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Import our enhanced systems
from utilities.live_file_sync import (
    load_game_data, 
    get_environment_status,
    is_running_locally,
    verify_data_sources
)
from utilities.enhanced_feature_analysis import get_comprehensive_feature_analysis
from utilities.workforce_management import (
    analyze_employee_work_queues, 
    analyze_production_requirements,
    generate_standup_agenda,
    generate_calendar_events,
    calculate_optimal_team_composition
)
from utilities.enhanced_workforce_management import (
    analyze_sales_team,
    analyze_research_team,
    analyze_developer_teams,
    generate_professional_development_plan
)
from utilities.data_center_monitoring import analyze_data_center_performance
from utilities.focused_team_management import analyze_manageable_team_members
from utilities.static_evaluation_engine import run_static_evaluation
from utilities.smart_recruitment import (
    analyze_hiring_needs,
    filter_candidates_by_role,
    get_top_candidates_for_role,
    generate_instant_hire_suggestion
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Momentum AI - Project Phoenix",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Live Data Loading ---
def load_live_data():
    """Load data with live file sync support"""
    try:
        return load_game_data()
    except Exception as e:
        st.error(f"Error loading game data: {e}")
        # Show debugging information for deployment issues
        with st.expander("🔧 Deployment Debug Info", expanded=True):
            st.write("**Error Details:**")
            st.write(f"• {str(e)}")
            st.write("**Environment:**")
            st.write(f"• Current working directory: {Path.cwd()}")
            st.write(f"• Script directory: {Path(__file__).parent}")
            
            # Check for backup file manually
            backup_paths = [
                Path("save_data/sg_momentum ai.json"),
                Path("live_analytics/save_data/sg_momentum ai.json"),
                Path(__file__).parent / "save_data" / "sg_momentum ai.json"
            ]
            st.write("**Backup File Search:**")
            for path in backup_paths:
                exists = path.exists()
                st.write(f"• {path.absolute()} - {'✅ FOUND' if exists else '❌ NOT FOUND'}")
        
        return None

@st.cache_data(ttl=30)  # Cache for 30 seconds to allow for real-time updates
def load_data():
    """Legacy function - redirects to live data loading"""
    return load_live_data()

data = load_data()

# --- Business Intelligence Functions ---
def analyze_product_performance(data):
    """Analyze product performance metrics and generate insights."""
    products = data.get('progress', {}).get('products', {})
    if not products:
        return None
    
    main_product_id = next(iter(products), None)
    if not main_product_id:
        return None
        
    product = products[main_product_id]
    
    # Extract key metrics
    users = product.get('users', {})
    stats = product.get('stats', {})
    
    analysis = {
        'total_users': users.get('total', 0),
        'satisfaction': users.get('satisfaction', 0),
        'conversion_rate': users.get('conversionRate', 0),
        'potential_users': users.get('potentialUsers', 0),
        'quality': stats.get('quality', 0),
        'efficiency': stats.get('efficiency', 0),
        'valuation': stats.get('valuation', 0),
        'performance_state': stats.get('performance', {}).get('state', 'Unknown')
    }
    
    # Generate insights
    insights = []
    
    # User acquisition insights
    if analysis['potential_users'] > 0:
        market_penetration = (analysis['total_users'] / analysis['potential_users']) * 100
        analysis['market_penetration'] = market_penetration
        
        if market_penetration < 10:
            insights.append({
                'type': 'opportunity',
                'title': 'Low Market Penetration',
                'message': f"Current market share: {market_penetration:.1f}%",
                'metric': 'Market penetration below 10% threshold',
                'action_type': 'MARKETING_EXPANSION'
            })
        elif market_penetration > 50:
            insights.append({
                'type': 'success',
                'title': 'Strong Market Position',
                'message': f"Current market share: {market_penetration:.1f}%",
                'metric': 'Market penetration above 50% threshold',
                'action_type': 'RETENTION_OPTIMIZATION'
            })
    
    # Satisfaction thresholds
    if analysis['satisfaction'] < 60:
        insights.append({
            'type': 'critical',
            'title': 'User Satisfaction Below Target',
            'message': f"Current satisfaction: {analysis['satisfaction']}%",
            'metric': 'Below 60% satisfaction threshold',
            'action_type': 'QUALITY_IMPROVEMENT_REQUIRED'
        })
    elif analysis['satisfaction'] > 80:
        insights.append({
            'type': 'success',
            'title': 'High User Satisfaction',
            'message': f"Current satisfaction: {analysis['satisfaction']}%",
            'metric': 'Above 80% satisfaction threshold',
            'action_type': 'SATISFACTION_MAINTAINED'
        })
    
    # Quality vs Efficiency ratio analysis
    if analysis['quality'] > 0 and analysis['efficiency'] > 0:
        qe_ratio = analysis['quality'] / analysis['efficiency']
        insights.append({
            'type': 'metric',
            'title': 'Quality/Efficiency Ratio',
            'message': f"Q/E Ratio: {qe_ratio:.2f}",
            'metric': f"Quality: {analysis['quality']}, Efficiency: {analysis['efficiency']}",
            'action_type': 'RATIO_TRACKED' if 0.5 <= qe_ratio <= 3 else 'RATIO_IMBALANCED'
        })
    
    analysis['insights'] = insights
    return analysis

def analyze_feature_development(data):
    """Analyze feature development progress and dependencies."""
    features = data.get('featureInstances', [])
    inventory = data.get('inventory', {})
    
    if not features:
        return None
    
    analysis = {
        'total_features': len(features),
        'active_features': len([f for f in features if f.get('activated', False)]),
        'feature_details': [],
        'component_needs': {},
        'development_priorities': []
    }
    
    for feature in features:
        requirements = feature.get('requirements', {})
        quality = feature.get('quality', {})
        efficiency = feature.get('efficiency', {})
        
        feature_analysis = {
            'name': feature.get('featureName', 'Unknown'),
            'activated': feature.get('activated', False),
            'current_quality': quality.get('current', 0),
            'max_quality': quality.get('max', 0),
            'current_efficiency': efficiency.get('current', 0),
            'max_efficiency': efficiency.get('max', 0),
            'requirements': requirements,
            'completion_ratio': 0,
            'missing_components': {}
        }
        
        # Check component availability vs requirements
        total_required = sum(requirements.values()) if requirements else 0
        total_available = 0
        
        for component, needed in requirements.items():
            available = inventory.get(component, 0)
            total_available += min(available, needed)
            
            if available < needed:
                feature_analysis['missing_components'][component] = needed - available
        
        if total_required > 0:
            feature_analysis['completion_ratio'] = (total_available / total_required) * 100
        
        # Calculate upgrade potential
        quality_potential = (feature_analysis['max_quality'] - feature_analysis['current_quality']) / feature_analysis['max_quality'] * 100 if feature_analysis['max_quality'] > 0 else 0
        efficiency_potential = (feature_analysis['max_efficiency'] - feature_analysis['current_efficiency']) / feature_analysis['max_efficiency'] * 100 if feature_analysis['max_efficiency'] > 0 else 0
        
        feature_analysis['quality_potential'] = quality_potential
        feature_analysis['efficiency_potential'] = efficiency_potential
        feature_analysis['upgrade_priority'] = (quality_potential + efficiency_potential) / 2
        
        analysis['feature_details'].append(feature_analysis)
    
    # Sort features by upgrade priority
    analysis['feature_details'].sort(key=lambda x: x['upgrade_priority'], reverse=True)
    
    # Aggregate component needs
    for feature in analysis['feature_details']:
        for component, shortage in feature['missing_components'].items():
            analysis['component_needs'][component] = analysis['component_needs'].get(component, 0) + shortage
    
    return analysis

def build_dependency_tree(data):
    """Build comprehensive dependency tree for all game items."""
    # Define known component dependencies based on game mechanics
    dependencies = {
        # Basic Components (Tier 1 - No dependencies)
        'BlueprintComponent': [],
        'UiComponent': [],
        'GraphicsComponent': [],
        'BackendComponent': [],
        'NetworkComponent': [],
        'DatabaseComponent': [],
        'SemanticComponent': [],
        'EncryptionComponent': [],
        'FilesystemComponent': [],
        'VideoComponent': [],
        'SmtpComponent': [],
        'I18nComponent': [],
        'SearchAlgorithmComponent': [],
        'CompressionComponent': [],
        'VirtualHardware': [],
        'OperatingSystem': [],
        'Firewall': [],
        'WireframeComponent': [],
        
        # Research Components (Tier 1)
        'Copywriting': [],
        'TextFormat': [],
        'ImageFormat': [],
        'VideoFormat': [],
        'AudioFormat': [],
        'ContractAgreement': [],
        'Survey': [],
        'UserFeedback': [],
        'PhoneInterview': [],
        'AnalyticsResearch': [],
        'BehaviorObservation': [],
        'AbTesting': [],
        'DocumentationComponent': [],
        'ProcessManagement': [],
        'ContinuousIntegration': [],
        'CronJob': [],
        
        # Modules (Tier 2 - Depend on components)
        'InterfaceModule': ['UiComponent', 'GraphicsComponent'],
        'FrontendModule': ['UiComponent', 'GraphicsComponent', 'NetworkComponent'],
        'BackendModule': ['BackendComponent', 'DatabaseComponent'],
        'InputModule': ['UiComponent', 'BackendComponent'],
        'StorageModule': ['DatabaseComponent', 'FilesystemComponent'],
        'ContentManagementModule': ['BackendModule', 'StorageModule', 'InterfaceModule'],
        'SeoModule': ['BackendModule', 'SearchAlgorithmComponent'],
        'AuthenticationModule': ['BackendModule', 'EncryptionComponent'],
        'PaymentGatewayModule': ['BackendModule', 'EncryptionComponent', 'NetworkComponent'],
        'VideoPlaybackModule': ['VideoComponent', 'FrontendModule'],
        'EmailModule': ['SmtpComponent', 'BackendModule'],
        'LocalizationModule': ['I18nComponent', 'BackendModule'],
        'SearchModule': ['SearchAlgorithmComponent', 'BackendModule'],
        'BandwidthCompressionModule': ['CompressionComponent', 'NetworkComponent'],
        'DatabaseLayer': ['DatabaseComponent', 'BackendComponent'],
        'NotificationModule': ['BackendModule', 'NetworkComponent'],
        'ApiClientModule': ['NetworkComponent', 'BackendModule'],
        'CodeOptimizationModule': ['BackendModule', 'ProcessManagement'],
        
        # Advanced Modules (Tier 3 - Depend on other modules)
        'VirtualContainer': ['OperatingSystem', 'VirtualHardware', 'BackendModule'],
        'Cluster': ['VirtualContainer', 'NetworkComponent'],
        'SwarmManagement': ['Cluster', 'ProcessManagement'],
        
        # UI Elements (Tier 2)
        'UiElement': ['UiComponent'],
        'UiSet': ['UiElement', 'GraphicsComponent'],
        'ResponsiveUi': ['UiSet', 'FrontendModule'],
        'DesignGuidelines': ['ResponsiveUi', 'WireframeComponent']
    }
    
    # Build dependency graph
    G = nx.DiGraph()
    
    # Add nodes with tier classification
    for item, deps in dependencies.items():
        tier = calculate_dependency_tier(item, dependencies)
        G.add_node(item, tier=tier, type=classify_item_type(item))
        
        # Add edges for dependencies
        for dep in deps:
            G.add_edge(dep, item)
    
    return G, dependencies

def calculate_dependency_tier(item, dependencies, visited=None):
    """Calculate the tier level of an item based on its dependency depth."""
    if visited is None:
        visited = set()
    
    if item in visited:
        return 0  # Circular dependency fallback
    
    visited.add(item)
    
    deps = dependencies.get(item, [])
    if not deps:
        return 1  # Base tier for items with no dependencies
    
    max_dep_tier = max((calculate_dependency_tier(dep, dependencies, visited.copy()) for dep in deps), default=0)
    return max_dep_tier + 1

def classify_item_type(item):
    """Classify items by type for visual organization."""
    if 'Module' in item:
        return 'Module'
    elif 'Component' in item:
        return 'Component'
    elif 'Ui' in item or 'Element' in item:
        return 'UI'
    else:
        return 'System'

def analyze_team_hierarchy(data):
    """Analyze current team structure and recommend tier assignments."""
    employees = []
    
    # Extract employees from workstations
    workstations = data.get('office', {}).get('workstations', [])
    for ws in workstations:
        employee = ws.get('employee')
        if employee:
            employees.append(employee)
    
    # Analyze team composition
    team_analysis = {
        'total_employees': len(employees),
        'employee_details': [],
        'tier_recommendations': {},
        'coverage_analysis': {},
        'hierarchy_issues': []
    }
    
    for emp in employees:
        role = emp.get('employeeTypeName', 'Unknown')
        level = emp.get('level', 'Beginner')
        speed = emp.get('speed', 0)
        
        # Determine recommended tier based on role and level
        recommended_tier = determine_employee_tier(role, level, speed)
        
        emp_analysis = {
            'name': emp.get('name', 'Unknown'),
            'role': role,
            'level': level,
            'speed': speed,
            'recommended_tier': recommended_tier,
            'current_queue': len(emp.get('queue', [])),
            'complexity_rating': calculate_complexity_rating(role, level, speed)
        }
        
        team_analysis['employee_details'].append(emp_analysis)
    
    # Analyze tier coverage
    tier_counts = {}
    for emp in team_analysis['employee_details']:
        tier = emp['recommended_tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    team_analysis['tier_coverage'] = tier_counts
    
    # Generate hierarchy recommendations
    team_analysis['hierarchy_recommendations'] = generate_hierarchy_recommendations(tier_counts, team_analysis['employee_details'])
    
    return team_analysis

def determine_employee_tier(role, level, speed):
    """Determine appropriate tier assignment for an employee."""
    base_tier = 1
    
    # Role-based tier adjustment
    if role in ['Developer', 'Designer']:
        base_tier = 1
    elif role in ['LeadDeveloper', 'LeadDesigner']:
        base_tier = 2
    elif role in ['Researcher']:
        base_tier = 2
    elif role in ['ChiefExecutiveOfficer']:
        base_tier = 3
    
    # Level adjustment
    if level == 'Intermediate':
        base_tier += 1
    elif level == 'Expert':
        base_tier += 2
    
    # Speed adjustment (high performers can handle higher complexity)
    if speed > 150:
        base_tier += 1
    elif speed > 100:
        base_tier += 0.5
    
    return min(int(base_tier), 4)  # Cap at tier 4

def calculate_complexity_rating(role, level, speed):
    """Calculate overall complexity rating for an employee."""
    role_score = {'Developer': 3, 'Designer': 3, 'LeadDeveloper': 5, 'LeadDesigner': 5, 'Researcher': 4, 'ChiefExecutiveOfficer': 6}.get(role, 1)
    level_score = {'Beginner': 1, 'Intermediate': 2, 'Expert': 3}.get(level, 1)
    speed_score = min(speed / 50, 4)  # Normalize speed to 0-4 scale
    
    return (role_score + level_score + speed_score) / 3

def generate_hierarchy_recommendations(tier_counts, employee_details):
    """Generate recommendations for optimal team hierarchy."""
    recommendations = []
    
    # Check for tier 1 coverage (essential for dependency chains)
    tier_1_count = tier_counts.get(1, 0)
    if tier_1_count < 2:
        recommendations.append({
            'priority': 'Critical',
            'issue': 'Insufficient Tier 1 Workers',
            'recommendation': f'Hire {2 - tier_1_count} more junior developers/designers for component production',
            'impact': 'Dependency chain bottlenecks will block all higher-tier work'
        })
    
    # Check tier balance
    total_employees = sum(tier_counts.values())
    if total_employees > 0:
        tier_1_ratio = tier_1_count / total_employees
        if tier_1_ratio < 0.4:
            recommendations.append({
                'priority': 'High',
                'issue': 'Tier Imbalance',
                'recommendation': 'Increase proportion of Tier 1 workers to 40-50% of team',
                'impact': 'Higher tiers will be starved of dependencies'
            })
    
    # Check for leadership coverage
    tier_3_plus = sum(tier_counts.get(i, 0) for i in range(3, 5))
    if tier_3_plus == 0 and total_employees > 3:
        recommendations.append({
            'priority': 'Medium',
            'issue': 'No Senior Leadership',
            'recommendation': 'Promote or hire senior-level talent for complex module development',
            'impact': 'Advanced features and modules cannot be developed efficiently'
        })
    
    return recommendations

# --- WSJF Scoring and Executive Task Management ---
def calculate_wsjf_score(feature, business_value, time_criticality, effort_estimate, risk_reduction=1):
    """
    Calculate WSJF (Weighted Shortest Job First) score for feature prioritization.
    WSJF = (Business Value + Time Criticality + Risk Reduction) / Effort
    """
    numerator = business_value + time_criticality + risk_reduction
    return numerator / max(effort_estimate, 1)  # Avoid division by zero

def analyze_feature_priorities(data):
    """Analyze current features and calculate WSJF scores for prioritization."""
    features = []
    
    # Get current feature instances (actual game data structure)
    feature_instances = data.get('featureInstances', [])
    products_list = data.get('products', [])
    
    # Create a product lookup for feature mapping
    product_lookup = {product.get('id'): product for product in products_list}
    
    for feature in feature_instances:
        # Find the corresponding product
        product_id = feature.get('productId')
        product = product_lookup.get(product_id, {})
        
        # Calculate business value based on market demand and revenue potential
        business_value = calculate_business_value(feature, product, data)
        # Calculate time criticality based on market position and competition
        time_criticality = calculate_time_criticality(feature, product, data)
        # Estimate effort based on feature complexity
        effort_estimate = estimate_feature_effort(feature, data)
        # Calculate risk reduction based on technical debt and dependencies
        risk_reduction = calculate_risk_reduction(feature, data)
        
        wsjf_score = calculate_wsjf_score(feature, business_value, time_criticality, effort_estimate, risk_reduction)
        
        # Calculate feature progress based on efficiency vs max efficiency
        efficiency = feature.get('efficiency', {})
        current_efficiency = efficiency.get('current', 0)
        max_efficiency = efficiency.get('max', 1)
        progress = (current_efficiency / max_efficiency) * 100 if max_efficiency > 0 else 0
        
        features.append({
            'name': feature.get('featureName', 'Unknown Feature'),
            'product': product.get('name', 'Unknown Product'),
            'business_value': business_value,
            'time_criticality': time_criticality,
            'effort_estimate': effort_estimate,
            'risk_reduction': risk_reduction,
            'wsjf_score': wsjf_score,
            'status': progress,
            'dependencies': list(feature.get('requirements', {}).keys()),
            'activated': feature.get('activated', False),
            'quality': feature.get('quality', {}).get('current', 0),
            'price_per_month': feature.get('pricePerMonth', 0)
        })
    
    # Also analyze development items in employee queues as potential features
    workstations = data.get('office', {}).get('workstations', [])
    for ws in workstations:
        employee = ws.get('employee')
        if employee:
            queue = employee.get('queue', [])
            for queue_item in queue:
                component = queue_item.get('component', {})
                if component.get('state') != 'Completed':  # Only include active development
                    # Treat development items as potential features
                    business_value = calculate_dev_business_value(component, data)
                    time_criticality = calculate_dev_time_criticality(component, queue_item, data)
                    effort_estimate = estimate_dev_effort(component, queue_item, data)
                    risk_reduction = calculate_dev_risk_reduction(component, data)
                    
                    wsjf_score = calculate_wsjf_score(component, business_value, time_criticality, effort_estimate, risk_reduction)
                    
                    # Calculate progress
                    total_minutes = queue_item.get('totalMinutes', 1)
                    completed_minutes = queue_item.get('completedMinutes', 0)
                    progress = (completed_minutes / total_minutes) * 100 if total_minutes > 0 else 0
                    
                    features.append({
                        'name': f"{component.get('name', 'Unknown Component')} (Dev)",
                        'product': 'Development Pipeline',
                        'business_value': business_value,
                        'time_criticality': time_criticality,
                        'effort_estimate': effort_estimate,
                        'risk_reduction': risk_reduction,
                        'wsjf_score': wsjf_score,
                        'status': progress,
                        'dependencies': list(component.get('requirements', {}).keys()),
                        'activated': False,
                        'quality': 0,
                        'price_per_month': 0,
                        'employee': employee.get('name', 'Unknown'),
                        'state': queue_item.get('state', 'Unknown')
                    })
    
    # Sort by WSJF score (highest first)
    features.sort(key=lambda x: x['wsjf_score'], reverse=True)
    return features

def calculate_business_value(feature, product, data):
    """Calculate business value score (1-10 scale)."""
    # Base value from feature revenue potential
    price_per_month = feature.get('pricePerMonth', 0)
    base_value = min(price_per_month / 100, 3) if price_per_month > 0 else 2
    
    # Add value for feature activation status
    activation_value = 3 if feature.get('activated', False) else 1
    
    # Add value for feature quality (higher quality = more business value)
    quality = feature.get('quality', {}).get('current', 0)
    quality_value = min(quality / 1000, 3)  # Normalize quality
    
    # Add value for product user base (from product stats if available)
    product_value = 0
    if product:
        # Try to get user statistics from the product
        stats = product.get('stats', {})
        if stats:
            registered_users = stats.get('registeredUsers', [])
            if registered_users:
                latest_users = registered_users[-1].get('amount', 0)
                product_value = min(latest_users / 10000, 2)  # Normalize users
    
    return min(base_value + activation_value + quality_value + product_value, 10)

def calculate_time_criticality(feature, product, data):
    """Calculate time criticality score (1-10 scale)."""
    # Higher criticality for activated features (users depend on them)
    activation_urgency = 6 if feature.get('activated', False) else 3
    
    # Higher criticality for features with many requirements (blocking others)
    requirements = feature.get('requirements', {})
    blocking_factor = min(len(requirements) * 0.5, 3)
    
    # Higher criticality for features with low efficiency (need improvement)
    efficiency = feature.get('efficiency', {})
    current_eff = efficiency.get('current', 1)
    max_eff = efficiency.get('max', 1)
    efficiency_ratio = current_eff / max_eff if max_eff > 0 else 1
    efficiency_urgency = 3 if efficiency_ratio < 0.5 else 1  # Low efficiency = high urgency
    
    # Product-based urgency (if product has users, features are more critical)
    product_urgency = 0
    if product:
        stats = product.get('stats', {})
        if stats:
            registered_users = stats.get('registeredUsers', [])
            if registered_users and len(registered_users) > 0:
                latest_users = registered_users[-1].get('amount', 0)
                product_urgency = min(latest_users / 5000, 2)  # More users = higher urgency
    
    return min(activation_urgency + blocking_factor + efficiency_urgency + product_urgency, 10)

def estimate_feature_effort(feature, data):
    """Estimate development effort (1-10 scale, higher = more effort)."""
    # Base effort from feature requirements complexity
    requirements = feature.get('requirements', {})
    base_effort = len(requirements) + 1
    
    # Add effort based on feature complexity (efficiency ratio indicates complexity)
    efficiency = feature.get('efficiency', {})
    max_eff = efficiency.get('max', 1)
    complexity_effort = min(max_eff / 1000, 3)  # Higher max efficiency = more complex feature
    
    # Effort modifier based on team capability
    team_modifier = calculate_team_capability_modifier(data)
    
    total_effort = (base_effort + complexity_effort) * team_modifier
    return min(total_effort, 10)

def calculate_risk_reduction(feature, data):
    """Calculate risk reduction value (1-10 scale)."""
    feature_name = feature.get('featureName', '').lower()
    
    # Higher value for features that reduce technical debt
    debt_reduction = 2 if 'optimization' in feature_name or 'refactor' in feature_name else 1
    
    # Higher value for features that improve system stability
    stability_improvement = 3 if any(keyword in feature_name for keyword in ['security', 'backend', 'infrastructure']) else 1
    
    # Higher value for activated features (they reduce business risk)
    business_risk = 3 if feature.get('activated', False) else 1
    
    # Higher value for features with good quality (reduce technical risk)
    quality = feature.get('quality', {}).get('current', 0)
    quality_risk = min(quality / 2000, 2)  # Higher quality = more risk reduction
    
    return min(debt_reduction + stability_improvement + business_risk + quality_risk, 10)

def calculate_team_capability_modifier(data):
    """Calculate team capability modifier for effort estimation."""
    employees = []
    workstations = data.get('office', {}).get('workstations', [])
    for ws in workstations:
        employee = ws.get('employee')
        if employee:
            employees.append(employee)
    
    if not employees:
        return 2.0  # High effort if no team
    
    # Calculate average team skill level
    total_skill = sum(emp.get('speed', 10) for emp in employees)
    avg_skill = total_skill / len(employees)
    
    # Convert to effort modifier (higher skill = lower effort)
    return max(1.0, 3.0 - (avg_skill / 50))

# Development item analysis functions
def calculate_dev_business_value(component, data):
    """Calculate business value for development items."""
    component_name = component.get('name', '').lower()
    
    # Higher value for user-facing components
    if 'ui' in component_name or 'interface' in component_name or 'frontend' in component_name:
        return 7
    # Medium value for core functionality
    elif 'backend' in component_name or 'network' in component_name:
        return 6
    # Lower value for supporting components
    elif 'component' in component.get('type', '').lower():
        return 4
    # Higher value for modules (more complex features)
    elif 'module' in component.get('type', '').lower():
        return 8
    else:
        return 5

def calculate_dev_time_criticality(component, queue_item, data):
    """Calculate time criticality for development items."""
    # Higher criticality for items currently being worked on
    state = queue_item.get('state', '')
    if state == 'Running':
        base_criticality = 8
    elif state == 'Completed':
        return 1  # Low criticality for completed items
    else:
        base_criticality = 5
    
    # Higher criticality for items that unblock other development
    component_type = component.get('type', '').lower()
    if 'component' in component_type:
        return base_criticality + 2  # Components unlock modules
    else:
        return base_criticality

def estimate_dev_effort(component, queue_item, data):
    """Estimate effort for development items."""
    # Use actual time data from the game
    total_minutes = queue_item.get('totalMinutes', 60)
    
    # Convert to effort scale (1-10)
    # Normalize based on typical component times (120-1260 minutes observed)
    effort_score = min(total_minutes / 126, 10)  # 126 minutes = effort score of 1
    
    return max(1, effort_score)

def calculate_dev_risk_reduction(component, data):
    """Calculate risk reduction for development items."""
    component_name = component.get('name', '').lower()
    
    # Higher risk reduction for foundational components
    if 'component' in component.get('type', '').lower():
        return 6  # Components reduce technical debt
    # Medium risk reduction for modules
    elif 'module' in component.get('type', '').lower():
        return 4
    # Higher risk reduction for security/stability related items
    elif 'security' in component_name or 'backend' in component_name:
        return 7
    else:
        return 3

def generate_executive_tasks(data):
    """Generate intelligent executive calendar tasks based on current business state."""
    tasks = []
    
    # Get prioritized features for development tasks
    priority_features = analyze_feature_priorities(data)[:3]  # Top 3 priorities
    
    # Dev Team Stand-Up tasks
    if priority_features:
        dev_details = generate_dev_standup_details(priority_features, data)
        tasks.append({
            'type': 'Dev Team Stand-Up',
            'title': 'Dev Team Stand-Up',
            'priority': 'High',
            'category': 'Development',
            'details': dev_details,
            'icon': '👥'
        })
    
    # Sales and Marketing tasks
    sales_tasks = generate_sales_tasks(data)
    tasks.extend(sales_tasks)
    
    # HR and People Management tasks
    hr_tasks = generate_hr_tasks(data)
    tasks.extend(hr_tasks)
    
    # Operations and Facilities tasks
    ops_tasks = generate_operations_tasks(data)
    tasks.extend(ops_tasks)
    
    # Recruiting tasks
    recruiting_tasks = generate_recruiting_tasks(data)
    tasks.extend(recruiting_tasks)
    
    return tasks

# Advanced Work Queue Management Functions
def analyze_work_queue_coverage(data):
    """Analyze which components/modules are being worked on and identify gaps."""
    coverage_analysis = {
        'active_assignments': {},  # component_name -> employee_name
        'unassigned_requirements': [],  # requirements not in any queue
        'team_workload': {},  # employee_name -> queue_info
        'automation_suggestions': []  # specific assignment recommendations
    }
    
    # Get all employees and their current work queues
    workstations = data.get('office', {}).get('workstations', [])
    for ws in workstations:
        employee = ws.get('employee')
        if employee:
            emp_name = employee.get('name', 'Unknown')
            queue = employee.get('queue', [])
            
            # Analyze employee's current workload
            coverage_analysis['team_workload'][emp_name] = {
                'employee': employee,
                'queue_size': len(queue),
                'active_tasks': [],
                'completed_tasks': [],
                'tier': determine_employee_tier(
                    employee.get('employeeTypeName', 'Developer'),
                    employee.get('level', 'Beginner'),
                    employee.get('speed', 0)
                )
            }
            
            # Track what each employee is working on
            for queue_item in queue:
                component = queue_item.get('component', {})
                component_name = component.get('name', 'Unknown')
                state = queue_item.get('state', 'Unknown')
                
                if state == 'Running':
                    coverage_analysis['active_assignments'][component_name] = emp_name
                    coverage_analysis['team_workload'][emp_name]['active_tasks'].append({
                        'component': component_name,
                        'progress': queue_item.get('completedMinutes', 0) / max(queue_item.get('totalMinutes', 1), 1) * 100,
                        'tier_required': classify_task_tier(component_name)
                    })
                elif state == 'Completed':
                    coverage_analysis['team_workload'][emp_name]['completed_tasks'].append(component_name)
    
    return coverage_analysis

def identify_unassigned_requirements(data, coverage_analysis):
    """Identify high-priority components/modules that need to be assigned to workers."""
    unassigned_requirements = []
    
    # Get high-priority features and their requirements
    priority_features = analyze_feature_priorities(data)[:3]  # Top 3 priorities
    
    for feature in priority_features:
        requirements = feature.get('dependencies', [])
        for requirement in requirements:
            # Check if this requirement is currently being worked on
            if requirement not in coverage_analysis['active_assignments']:
                # This requirement is not assigned to anyone - find the best worker
                suggested_worker = find_optimal_worker_for_requirement(requirement, coverage_analysis, data)
                
                unassigned_requirements.append({
                    'requirement': requirement,
                    'feature': feature['name'],
                    'priority_score': feature['wsjf_score'],
                    'suggested_worker': suggested_worker,
                    'tier_needed': classify_task_tier(requirement),
                    'action': f"Add {requirement} to {suggested_worker['name']}'s work queue" if suggested_worker else f"Need to hire Tier {classify_task_tier(requirement)} worker for {requirement}"
                })
    
    return unassigned_requirements

def find_optimal_worker_for_requirement(requirement, coverage_analysis, data):
    """Find the best available worker for a specific requirement."""
    required_tier = classify_task_tier(requirement)
    
    # Find all workers capable of handling this tier
    capable_workers = []
    for emp_name, workload_info in coverage_analysis['team_workload'].items():
        worker_tier = workload_info['tier']
        if worker_tier >= required_tier:
            capable_workers.append({
                'name': emp_name,
                'tier': worker_tier,
                'queue_size': workload_info['queue_size'],
                'active_tasks_count': len(workload_info['active_tasks']),
                'workload_score': workload_info['queue_size'] + len(workload_info['active_tasks'])
            })
    
    if not capable_workers:
        return None
    
    # Sort by workload (ascending) and tier capability (descending for tie-breaking)
    capable_workers.sort(key=lambda x: (x['workload_score'], -x['tier']))
    
    return capable_workers[0] if capable_workers else None

def generate_automation_suggestions(unassigned_requirements, coverage_analysis):
    """Generate specific automation suggestions for work queue management."""
    suggestions = []
    
    for req in unassigned_requirements:
        if req['suggested_worker']:
            suggestions.append({
                'type': 'assignment',
                'action': f"Assign {req['requirement']} to {req['suggested_worker']['name']}",
                'priority': 'HIGH' if req['priority_score'] > 7 else 'MEDIUM',
                'rationale': f"Required for {req['feature']} (WSJF: {req['priority_score']:.2f})",
                'worker': req['suggested_worker']['name'],
                'component': req['requirement'],
                'tier_match': req['suggested_worker']['tier'] >= req['tier_needed']
            })
        else:
            suggestions.append({
                'type': 'hiring',
                'action': f"Hire Tier {req['tier_needed']} worker for {req['requirement']}",
                'priority': 'HIGH',
                'rationale': f"No available workers for {req['feature']} requirement",
                'component': req['requirement'],
                'tier_needed': req['tier_needed']
            })
    
    return suggestions

def generate_dev_standup_details(priority_features, data):
    """Generate automated work queue management strategy for dev team standup."""
    
    # Analyze current work queue coverage
    coverage_analysis = analyze_work_queue_coverage(data)
    
    # Identify unassigned high-priority requirements
    unassigned_requirements = identify_unassigned_requirements(data, coverage_analysis)
    
    # Generate automation suggestions
    automation_suggestions = generate_automation_suggestions(unassigned_requirements, coverage_analysis)
    
    details = {
        'coverage_analysis': coverage_analysis,
        'unassigned_requirements': unassigned_requirements,
        'automation_suggestions': automation_suggestions,
        'team_status': {},
        'immediate_actions': []
    }
    
    # Analyze team status and generate immediate actions
    for emp_name, workload in coverage_analysis['team_workload'].items():
        active_tasks = workload['active_tasks']
        queue_size = workload['queue_size']
        
        # Determine team member status
        if len(active_tasks) == 0 and queue_size == 0:
            status = "IDLE - Ready for new assignments"
            priority = "HIGH"
        elif len(active_tasks) > 0:
            status = f"ACTIVE - Working on {len(active_tasks)} tasks"
            priority = "LOW"
        elif queue_size > 3:
            status = f"OVERLOADED - {queue_size} items in queue"
            priority = "MEDIUM"
        else:
            status = f"QUEUED - {queue_size} items pending"
            priority = "LOW"
        
        details['team_status'][emp_name] = {
            'status': status,
            'priority': priority,
            'tier': workload['tier'],
            'active_tasks': active_tasks,
            'queue_size': queue_size
        }
    
    # Generate immediate action items
    for suggestion in automation_suggestions:
        if suggestion['type'] == 'assignment':
            details['immediate_actions'].append({
                'action': f"🎯 ADD TO QUEUE: {suggestion['component']}",
                'worker': suggestion['worker'],
                'priority': suggestion['priority'],
                'reason': suggestion['rationale']
            })
        elif suggestion['type'] == 'hiring':
            details['immediate_actions'].append({
                'action': f"👥 HIRE: Tier {suggestion['tier_needed']} Worker",
                'component': suggestion['component'],
                'priority': suggestion['priority'],
                'reason': suggestion['rationale']
            })
    
    return details

def find_best_team_member_for_task(task, team_members):
    """Find the best team member for a specific task based on tier and workload."""
    if not team_members:
        return None
    
    # Classify task complexity
    task_tier = classify_task_tier(task)
    
    # Find members capable of handling this tier
    capable_members = [m for m in team_members if m['recommended_tier'] >= task_tier]
    
    if not capable_members:
        return None
    
    # Sort by current queue size (ascending) and complexity rating (descending)
    capable_members.sort(key=lambda x: (x['current_queue'], -x['complexity_rating']))
    
    return capable_members[0]

def classify_task_tier(task):
    """Classify task complexity tier based on name."""
    task_lower = task.lower()
    if 'component' in task_lower:
        return 1
    elif 'module' in task_lower:
        return 2
    elif 'system' in task_lower or 'integration' in task_lower:
        return 3
    else:
        return 2  # Default to tier 2

def generate_sales_tasks(data):
    """Generate sales and marketing related tasks."""
    tasks = []
    
    # Check for advertising opportunities
    products = data.get('products', [])
    for product in products:
        if len(product.get('buyers', [])) < 5:  # Low buyer count
            sales_rep = find_sales_team_member(data)
            if sales_rep:
                tasks.append({
                    'type': 'Sales Meeting',
                    'title': f'Meeting with {sales_rep} - {product.get("name", "Product")} Marketing',
                    'priority': 'Medium',
                    'category': 'Sales',
                    'details': {
                        'product': product.get('name'),
                        'current_buyers': len(product.get('buyers', [])),
                        'suggested_ad_budget': calculate_suggested_ad_budget(product),
                        'target_segments': identify_target_segments(product, data),
                        'sales_rep': sales_rep
                    },
                    'icon': '💰'
                })
    
    return tasks

def generate_hr_tasks(data):
    """Generate HR and people management tasks."""
    tasks = []
    
    # Check employee satisfaction and needs
    employees = []
    workstations = data.get('office', {}).get('workstations', [])
    for ws in workstations:
        employee = ws.get('employee')
        if employee:
            employees.append(employee)
    
    # Check for low morale or unmet demands
    low_morale_employees = [emp for emp in employees if emp.get('mood', 100) < 70]
    
    if low_morale_employees:
        tasks.append({
            'type': 'HR Policy Review',
            'title': 'HR Policy Review - Employee Satisfaction',
            'priority': 'High',
            'category': 'Human Resources',
            'details': {
                'affected_employees': [emp.get('name', 'Unknown') for emp in low_morale_employees],
                'morale_issues': analyze_morale_issues(low_morale_employees),
                'recommended_actions': generate_morale_recommendations(low_morale_employees, data),
                'budget_impact': calculate_morale_budget_impact(low_morale_employees)
            },
            'icon': '👤'
        })
    
    return tasks

def generate_operations_tasks(data):
    """Generate operations and facilities related tasks."""
    tasks = []
    
    # Check office capacity and furniture needs
    office = data.get('office', {})
    workstations = office.get('workstations', [])
    
    # Calculate space utilization
    total_workstations = len(workstations)
    occupied_workstations = len([ws for ws in workstations if ws.get('employee')])
    utilization = occupied_workstations / max(total_workstations, 1)
    
    if utilization > 0.8:  # High utilization
        tasks.append({
            'type': 'Facilities Planning',
            'title': 'Facilities Upgrade - Office Expansion',
            'priority': 'Medium',
            'category': 'Operations',
            'details': {
                'current_capacity': total_workstations,
                'utilization_rate': f"{utilization:.1%}",
                'recommended_expansion': calculate_office_expansion_needs(data),
                'furniture_needs': identify_furniture_needs(workstations),
                'estimated_cost': estimate_expansion_cost(data)
            },
            'icon': '🏢'
        })
    
    return tasks

def generate_recruiting_tasks(data):
    """Generate recruiting and hiring related tasks."""
    tasks = []
    
    # Check for hiring needs based on team analysis
    team_analysis = analyze_team_hierarchy(data)
    tier_coverage = team_analysis.get('tier_coverage', {})
    
    # Check for tier gaps
    for tier in [1, 2, 3, 4]:
        if tier_coverage.get(tier, 0) < 2:  # Need at least 2 people per tier
            tasks.append({
                'type': 'Recruiting',
                'title': f'Recruiting - Tier {tier} Specialist',
                'priority': 'High' if tier <= 2 else 'Medium',
                'category': 'Recruiting',
                'details': {
                    'target_tier': tier,
                    'current_coverage': tier_coverage.get(tier, 0),
                    'recommended_roles': get_recommended_roles_for_tier(tier),
                    'budget_range': calculate_hiring_budget_range(tier, data),
                    'skills_needed': get_skills_for_tier(tier),
                    'urgency_reason': get_tier_urgency_reason(tier, team_analysis)
                },
                'icon': '🎯'
            })
    
    return tasks

# Helper functions for task generation
def find_sales_team_member(data):
    """Find a sales team member name."""
    employees = []
    workstations = data.get('office', {}).get('workstations', [])
    for ws in workstations:
        employee = ws.get('employee')
        if employee and 'sales' in employee.get('employeeTypeName', '').lower():
            return employee.get('name', 'Sales Team Member')
    return 'Sales Team Member'  # Default if no sales person found

def calculate_suggested_ad_budget(product):
    """Calculate suggested advertising budget for a product."""
    base_budget = min(product.get('price', 1000) * 0.1, 5000)  # 10% of price, max 5000
    return int(base_budget)

def identify_target_segments(product, data):
    """Identify target market segments for advertising."""
    segments = ['Tech Enthusiasts', 'Business Professionals', 'General Consumers']
    # Simple logic - could be enhanced with more sophisticated analysis
    return segments[:2]  # Return top 2 segments

def analyze_morale_issues(low_morale_employees):
    """Analyze what's causing low morale."""
    issues = []
    for emp in low_morale_employees:
        mood = emp.get('mood', 100)
        if mood < 50:
            issues.append(f"{emp.get('name', 'Employee')}: Critical morale ({mood}%)")
        elif mood < 70:
            issues.append(f"{emp.get('name', 'Employee')}: Low morale ({mood}%)")
    return issues

def generate_morale_recommendations(low_morale_employees, data):
    """Generate recommendations to improve employee morale."""
    recommendations = [
        "Review salary packages and consider raises",
        "Implement team building activities",
        "Upgrade office amenities and furniture",
        "Provide professional development opportunities",
        "Review workload distribution"
    ]
    return recommendations[:3]  # Return top 3 recommendations

def calculate_morale_budget_impact(low_morale_employees):
    """Calculate estimated budget impact of morale improvements."""
    base_cost_per_employee = 2000  # Base cost for improvements per employee
    return len(low_morale_employees) * base_cost_per_employee

def calculate_office_expansion_needs(data):
    """Calculate office expansion requirements."""
    employees = []
    workstations = data.get('office', {}).get('workstations', [])
    for ws in workstations:
        employee = ws.get('employee')
        if employee:
            employees.append(employee)
    
    current_capacity = len(workstations)
    current_employees = len(employees)
    recommended_capacity = int(current_employees * 1.5)  # 50% buffer
    
    return max(recommended_capacity - current_capacity, 2)

def identify_furniture_needs(workstations):
    """Identify furniture and equipment needs."""
    needs = []
    for ws in workstations:
        if ws.get('employee') and not ws.get('furniture', {}).get('desk'):
            needs.append("Additional desks")
        if ws.get('employee') and not ws.get('furniture', {}).get('chair'):
            needs.append("Ergonomic chairs")
    
    # Remove duplicates and add standard needs
    unique_needs = list(set(needs))
    if len(unique_needs) == 0:
        unique_needs = ["Upgraded workstations", "Additional monitors", "Office decorations"]
    
    return unique_needs

def estimate_expansion_cost(data):
    """Estimate cost of office expansion."""
    expansion_needs = calculate_office_expansion_needs(data)
    cost_per_workstation = 5000
    return expansion_needs * cost_per_workstation

def get_recommended_roles_for_tier(tier):
    """Get recommended employee roles for each tier."""
    tier_roles = {
        1: ["Developer", "Designer"],
        2: ["Developer", "Designer"],
        3: ["Lead Developer", "Lead Designer"],
        4: ["Lead Developer", "Lead Designer", "Researcher"]
    }
    return tier_roles.get(tier, ["Developer"])

def calculate_hiring_budget_range(tier, data):
    """Calculate budget range for hiring at specific tier."""
    base_salaries = {1: 50000, 2: 70000, 3: 100000, 4: 150000}
    base_salary = base_salaries.get(tier, 60000)
    return f"${base_salary:,} - ${int(base_salary * 1.3):,}"

def get_skills_for_tier(tier):
    """Get required skills for each tier."""
    tier_skills = {
        1: ["Basic programming", "Component development"],
        2: ["Module development", "Integration skills"],
        3: ["System architecture", "Team leadership"],
        4: ["Advanced systems", "Research & innovation"]
    }
    return tier_skills.get(tier, ["General development"])

def get_tier_urgency_reason(tier, team_analysis):
    """Get urgency reason for hiring at specific tier."""
    tier_reasons = {
        1: "Critical for basic component development",
        2: "Essential for module integration",
        3: "Required for complex system development",
        4: "Needed for advanced feature development"
    }
    return tier_reasons.get(tier, "Required for team balance")

# --- Page Navigation ---
def main():
    # Note: File monitoring disabled to prevent auto-refresh
    # User will manually refresh when they want to see updates
    # if is_running_locally():
    #     if 'file_observer' not in st.session_state:
    #         st.session_state.file_observer = setup_live_monitoring()

    st.sidebar.title("🐦‍🔥 Project Phoenix")
    st.sidebar.markdown("---")
    
    # Data Source Debug Panel (expandable)
    with st.sidebar.expander("🔧 Data Source Debug", expanded=False):
        if st.button("🔍 Verify Data Sources"):
            verification = verify_data_sources()
            st.json(verification)
    
    pages = {
        "🏠 Executive Overview": show_executive_overview,
        "📦 Product Management": show_product_management,
        "👥 Human Resources": show_human_resources,
        "🔬 Research & Development": show_research_development,
        "📅 Daily Standup": show_daily_standup,
        "📋 Production Planning": show_production_planning,
        "�️ Data Center Monitoring": show_data_center_monitoring,
        "�💼 Sales Team Meeting": show_sales_team_meeting
    }
    
    selected_page = st.sidebar.selectbox("Navigate to:", list(pages.keys()))
    
    # Load data once for all pages
    data = load_data()
    
    if data:
        # Show data freshness indicator
        game_date = data.get('date', 'Unknown')
        if game_date != 'Unknown':
            try:
                parsed_date = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                st.sidebar.success(f"📊 Data as of: {parsed_date.strftime('%Y-%m-%d %H:%M')}")
            except:
                st.sidebar.info(f"📊 Game Date: {game_date}")
        
        # Execute selected page
        pages[selected_page](data)
    else:
        st.error("❌ Could not load game data. Please check the data pipeline.")

def show_executive_overview(data):
    """Executive dashboard with high-level KPIs and alerts."""
    st.title("🏠 Executive Overview")
    st.markdown("**Real-time strategic overview of Momentum AI**")
    
    # --- Live Sync Status ---
    env_status = get_environment_status()
    
    col_env1, col_env2, col_env3 = st.columns([3, 2, 1])
    
    with col_env1:
        if env_status['auto_sync']:
            st.success(f"🔄 **{env_status['data_source']}**")
        elif env_status['backup_available']:
            if env_status['live_file_available']:
                st.warning(f"📁 **{env_status['data_source']}** (Live file sync disabled)")
            else:
                st.info(f"☁️ **{env_status['data_source']}**")
        else:
            st.error("❌ **No Data Source Available**")
    
    with col_env2:
        st.caption(f"📅 **Data as of:** {env_status['last_updated']}")
        if env_status.get('data_source_detail'):
            with st.expander("📋 Source Details"):
                st.code(env_status['data_source_detail'], language=None)
    
    with col_env3:
        if st.button("🔄 Refresh", help="Refresh dashboard data"):
            st.cache_data.clear()
            # Clear session state data source to force reload
            if 'data_source' in st.session_state:
                del st.session_state.data_source
            st.rerun()
    
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    balance = data.get('balance', 0)
    research_points = data.get('researchPoints', 0)
    
    # Extract product data safely
    total_users = 0
    valuation = 0
    products = data.get('progress', {}).get('products', {})
    if products:
        main_product_id = next(iter(products), None)
        if main_product_id:
            main_product = products[main_product_id]
            total_users = main_product.get('users', {}).get('total', 0)
            valuation = main_product.get('stats', {}).get('valuation', 0)
    
    col1.metric("💰 Balance", f"${balance:,.2f}")
    col2.metric("💡 Research Points", f"{research_points}")
    col3.metric("👥 Total Users", f"{int(total_users):,}")
    col4.metric("🏦 Valuation", f"${valuation:,.2f}")
    
    st.divider()
    
    # --- Strategic Insights ---
    st.header("🎯 Strategic Insights")
    
    product_analysis = analyze_product_performance(data)
    if product_analysis and product_analysis.get('insights'):
        for insight in product_analysis['insights']:
            if insight['type'] == 'critical':
                st.error(f"🚨 **{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'warning':
                st.warning(f"⚠️ **{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'opportunity':
                st.info(f"💡 **{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'success':
                st.success(f"✅ **{insight['title']}**: {insight['message']}")
            elif insight['type'] == 'metric':
                st.info(f"📊 **{insight['title']}**: {insight['message']}")
            
            # Display data-driven metrics instead of abstract actions
            with st.expander(f"Metric Details: {insight['title']}", expanded=False):
                st.markdown(f"**Measurement**: {insight['metric']}")
                st.markdown(f"**Action Category**: {insight['action_type']}")
                
                # Show specific data thresholds that triggered this insight
                if insight['action_type'] == 'MARKETING_EXPANSION':
                    st.markdown("• **Threshold**: Market penetration <10%")
                    st.markdown("• **Game Action**: Increase marketing budget allocation")
                elif insight['action_type'] == 'QUALITY_IMPROVEMENT_REQUIRED':
                    st.markdown("• **Threshold**: Satisfaction <60%") 
                    st.markdown("• **Game Action**: Assign developers to bug fixes and feature improvements")
                elif insight['action_type'] == 'RATIO_IMBALANCED':
                    st.markdown("• **Threshold**: Quality/Efficiency ratio outside 0.5-3.0 range")
                    st.markdown("• **Game Action**: Rebalance work queue priorities")
    else:
        st.info("No strategic insights available yet. Continue operations to generate data.")
    
    st.divider()
    
    # --- Executive Calendar & Business Tasks ---
    st.header("📅 Executive Calendar - Today's Business Tasks")
    st.markdown("*AI-generated action items based on current business intelligence*")
    
    # Generate executive tasks
    executive_tasks = generate_executive_tasks(data)
    
    if executive_tasks:
        # Organize tasks by priority
        high_priority = [t for t in executive_tasks if t.get('priority') == 'High']
        medium_priority = [t for t in executive_tasks if t.get('priority') == 'Medium']
        low_priority = [t for t in executive_tasks if t.get('priority') == 'Low']
        
        # Display high priority tasks first
        if high_priority:
            st.subheader("🔥 High Priority")
            for task in high_priority:
                with st.expander(f"{task['icon']} {task['title']}", expanded=False):
                    st.markdown(f"**Category:** {task['category']}")
                    st.markdown(f"**Priority:** {task['priority']}")
                    
                    # Display task-specific details
                    if task['type'] == 'Dev Team Stand-Up':
                        display_dev_standup_details(task['details'])
                    elif task['type'] == 'Sales Meeting':
                        display_sales_meeting_details(task['details'])
                    elif task['type'] == 'HR Policy Review':
                        display_hr_policy_details(task['details'])
                    elif task['type'] == 'Facilities Planning':
                        display_facilities_details(task['details'])
                    elif task['type'] == 'Recruiting':
                        display_recruiting_details(task['details'])
        
        # Display medium priority tasks
        if medium_priority:
            st.subheader("⚡ Medium Priority")
            for task in medium_priority:
                with st.expander(f"{task['icon']} {task['title']}", expanded=False):
                    st.markdown(f"**Category:** {task['category']}")
                    st.markdown(f"**Priority:** {task['priority']}")
                    
                    # Display task-specific details
                    if task['type'] == 'Sales Meeting':
                        display_sales_meeting_details(task['details'])
                    elif task['type'] == 'Facilities Planning':
                        display_facilities_details(task['details'])
                    elif task['type'] == 'Recruiting':
                        display_recruiting_details(task['details'])
    
    else:
        st.info("No executive tasks generated. System will create tasks as business conditions change.")

# Task detail display functions
def display_dev_standup_details(details):
    """Display automated work queue management strategy."""
    st.markdown("### 🤖 Automated Work Queue Management")
    st.markdown("*AI-driven development strategy - ready for execution*")
    
    # Immediate Actions Section
    if details.get('immediate_actions'):
        st.subheader("🚀 Immediate Actions Required")
        
        high_priority_actions = [action for action in details['immediate_actions'] if action['priority'] == 'HIGH']
        medium_priority_actions = [action for action in details['immediate_actions'] if action['priority'] == 'MEDIUM']
        
        if high_priority_actions:
            st.markdown("**🔥 HIGH PRIORITY:**")
            for action in high_priority_actions:
                if 'worker' in action:
                    st.error(f"**{action['action']}** → {action['worker']}")
                    st.markdown(f"   💡 *{action['reason']}*")
                else:
                    st.warning(f"**{action['action']}** for {action['component']}")
                    st.markdown(f"   💡 *{action['reason']}*")
        
        if medium_priority_actions:
            st.markdown("**⚡ MEDIUM PRIORITY:**")
            for action in medium_priority_actions:
                st.info(f"**{action['action']}** → {action.get('worker', 'TBD')}")
                st.markdown(f"   💡 *{action['reason']}*")
    else:
        st.success("✅ **All high-priority components are assigned!** Team is optimally allocated.")
    
    # Team Status Overview
    if details.get('team_status'):
        st.subheader("👥 Team Status Overview")
        
        # Create columns for team status
        team_members = list(details['team_status'].items())
        if len(team_members) <= 2:
            cols = st.columns(len(team_members))
        else:
            cols = st.columns(3)
        
        for i, (emp_name, status_info) in enumerate(team_members):
            with cols[i % len(cols)]:
                status = status_info['status']
                priority = status_info['priority']
                
                if priority == "HIGH":
                    st.error(f"**{emp_name}** (Tier {status_info['tier']})")
                elif priority == "MEDIUM":
                    st.warning(f"**{emp_name}** (Tier {status_info['tier']})")
                else:
                    st.success(f"**{emp_name}** (Tier {status_info['tier']})")
                
                st.write(f"Status: {status}")
                
                if status_info['active_tasks']:
                    st.write("🔄 Active Work:")
                    for task in status_info['active_tasks'][:2]:  # Show top 2 tasks
                        progress = task['progress']
                        st.write(f"  • {task['component']} ({progress:.0f}%)")
    
    # Work Queue Coverage Analysis
    if details.get('coverage_analysis'):
        st.subheader("📋 Work Queue Coverage Analysis")
        
        coverage = details['coverage_analysis']
        active_assignments = coverage.get('active_assignments', {})
        
        if active_assignments:
            st.markdown("**� Currently Active Assignments:**")
            for component, worker in active_assignments.items():
                st.write(f"• **{component}** → {worker}")
        else:
            st.warning("⚠️ No active development work detected!")
    
    # Unassigned Requirements
    if details.get('unassigned_requirements'):
        st.subheader("🎯 Unassigned High-Priority Requirements")
        
        for req in details['unassigned_requirements'][:5]:  # Show top 5
            with st.expander(f"🔧 {req['requirement']} (Priority: {req['priority_score']:.2f})"):
                st.write(f"**Required for:** {req['feature']}")
                st.write(f"**Tier needed:** {req['tier_needed']}")
                if req['suggested_worker']:
                    st.success(f"**Suggested assignment:** {req['suggested_worker']['name']}")
                    st.write(f"**Action:** {req['action']}")
                else:
                    st.error("**Action:** Need to hire qualified worker")
                    st.write(f"**Required:** {req['action']}")
    
    # Automation Intelligence Summary
    st.subheader("🧠 AI Strategy Summary")
    total_suggestions = len(details.get('automation_suggestions', []))
    assignment_suggestions = len([s for s in details.get('automation_suggestions', []) if s['type'] == 'assignment'])
    hiring_suggestions = len([s for s in details.get('automation_suggestions', []) if s['type'] == 'hiring'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Actions", total_suggestions)
    with col2:
        st.metric("Queue Assignments", assignment_suggestions)
    with col3:
        st.metric("Hiring Needs", hiring_suggestions)
    
    if total_suggestions == 0:
        st.info("🎯 **Perfect Alignment!** Your team is optimally assigned to high-priority work.")
    else:
        st.warning(f"📋 **{total_suggestions} actions needed** to optimize development pipeline.")

def display_sales_meeting_details(details):
    """Display detailed Sales Meeting information."""
    st.markdown("### 💼 Sales Strategy Meeting")
    
    st.markdown(f"**🎯 Product Focus:** {details.get('product', 'N/A')}")
    st.markdown(f"**📊 Current Buyers:** {details.get('current_buyers', 0)}")
    st.markdown(f"**💰 Suggested Ad Budget:** ${details.get('suggested_ad_budget', 0):,}")
    
    if details.get('target_segments'):
        st.markdown("**🎯 Target Market Segments:**")
        for segment in details['target_segments']:
            st.markdown(f"- {segment}")
    
    st.markdown(f"**👤 Sales Rep:** {details.get('sales_rep', 'TBD')}")

def display_hr_policy_details(details):
    """Display detailed HR Policy information."""
    st.markdown("### 👥 HR Policy Review Meeting")
    
    if details.get('affected_employees'):
        st.markdown("**🚨 Affected Employees:**")
        for emp in details['affected_employees']:
            st.markdown(f"- {emp}")
    
    if details.get('morale_issues'):
        st.markdown("**⚠️ Morale Issues:**")
        for issue in details['morale_issues']:
            st.markdown(f"- {issue}")
    
    if details.get('recommended_actions'):
        st.markdown("**💡 Recommended Actions:**")
        for action in details['recommended_actions']:
            st.markdown(f"- {action}")
    
    st.markdown(f"**💰 Estimated Budget Impact:** ${details.get('budget_impact', 0):,}")

def display_facilities_details(details):
    """Display detailed Facilities Planning information."""
    st.markdown("### 🏢 Facilities Planning Meeting")
    
    st.markdown(f"**📊 Current Capacity:** {details.get('current_capacity', 0)} workstations")
    st.markdown(f"**📈 Utilization Rate:** {details.get('utilization_rate', '0%')}")
    st.markdown(f"**➕ Recommended Expansion:** {details.get('recommended_expansion', 0)} additional workstations")
    
    if details.get('furniture_needs'):
        st.markdown("**🪑 Furniture & Equipment Needs:**")
        for need in details['furniture_needs']:
            st.markdown(f"- {need}")
    
    st.markdown(f"**💰 Estimated Cost:** ${details.get('estimated_cost', 0):,}")

def display_recruiting_details(details):
    """Display detailed Recruiting information."""
    st.markdown("### 🎯 Recruiting Strategy")
    
    st.markdown(f"**🎚️ Target Tier:** {details.get('target_tier', 'N/A')}")
    st.markdown(f"**📊 Current Coverage:** {details.get('current_coverage', 0)} employees")
    st.markdown(f"**💰 Budget Range:** {details.get('budget_range', 'TBD')}")
    st.markdown(f"**⚡ Urgency:** {details.get('urgency_reason', 'Team expansion')}")
    
    if details.get('recommended_roles'):
        st.markdown("**👤 Recommended Roles:**")
        for role in details['recommended_roles']:
            st.markdown(f"- {role}")
    
    if details.get('skills_needed'):
        st.markdown("**🔧 Required Skills:**")
        for skill in details['skills_needed']:
            st.markdown(f"- {skill}")

def show_product_management(data):
    """Advanced product management analytics and planning."""
    st.title("📦 Product Management")
    st.markdown("**Data-driven product strategy and development planning**")
    
    # --- Product Performance Analysis ---
    st.header("📊 Product Performance Analysis")
    
    product_analysis = analyze_product_performance(data)
    if product_analysis:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Market Penetration", 
                f"{product_analysis.get('market_penetration', 0):.1f}%",
                help="Percentage of potential users acquired"
            )
            st.metric("User Satisfaction", f"{product_analysis['satisfaction']}%")
        
        with col2:
            st.metric("Product Quality", f"{product_analysis['quality']}")
            st.metric("Product Efficiency", f"{product_analysis['efficiency']}")
        
        with col3:
            st.metric("Conversion Rate", f"{product_analysis['conversion_rate']}%")
            st.metric("Performance State", product_analysis['performance_state'])
    
    st.divider()
    
    # --- Enhanced Feature Development Analysis ---
    st.header("🚀 Feature Development Intelligence")
    feature_analysis = get_comprehensive_feature_analysis(data)
    
    # Feature Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Features", feature_analysis['feature_summary']['total'])
    with col2:
        st.metric("Ready to Build", feature_analysis['feature_summary']['ready_to_build'], 
                 delta=None, help="Features with all components available")
    with col3:
        st.metric("Partially Ready", feature_analysis['feature_summary']['partially_ready'],
                 help="Features missing some components")
    with col4:
        st.metric("Blocked", feature_analysis['feature_summary']['blocked'],
                 delta=feature_analysis['feature_summary']['blocked'] * -1 if feature_analysis['feature_summary']['blocked'] > 0 else None,
                 help="Features missing many components")
    
    # Feature Status Table
    if feature_analysis['features']:
        st.subheader("📋 Feature Status Overview")
        
        feature_data = []
        for feature in feature_analysis['features']:
            missing_count = len(feature['missing_components'])
            missing_list = ', '.join(feature['blocking_components'][:3])  # Show first 3
            if len(feature['blocking_components']) > 3:
                missing_list += f" (+{len(feature['blocking_components']) - 3} more)"
            
            feature_data.append({
                'Feature Name': feature['name'],
                'Status': feature['status'].replace('_', ' ').title(),
                'Readiness': f"{feature['readiness_score']:.0f}%",
                'Missing Components': missing_count,
                'Blocking Components': missing_list if missing_list else "None"
            })
        
        df = pd.DataFrame(feature_data)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Readiness": st.column_config.ProgressColumn(
                    "Readiness",
                    help="Percentage of required components available",
                    min_value=0,
                    max_value=100,
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Current development status",
                )
            }
        )
    
    # Team Assignment Analysis
    if feature_analysis['missing_components']:
        st.subheader("👥 Team Assignment Recommendations")
        
        assignments = feature_analysis['team_assignments']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Component Production Assignments:**")
            
            assignment_data = []
            for component, assignment in assignments['assignments'].items():
                assignment_data.append({
                    'Component': component,
                    'Needed': assignment['needed'],
                    'Assigned Role': assignment['assigned_role'],
                    'Priority': assignment['priority'],
                    'Est. Days': assignment['estimated_days']
                })
            
            assign_df = pd.DataFrame(assignment_data)
            st.dataframe(assign_df, use_container_width=True)
        
        with col2:
            st.markdown("**Workload by Role:**")
            
            for role, workload in assignments['workload_by_role'].items():
                with st.container():
                    st.markdown(f"**{role}**")
                    st.markdown(f"- {workload['components']} components")
                    st.markdown(f"- {workload['total_items']} total items")
                    st.markdown(f"- ~{workload['estimated_days']} days")
                    st.markdown("---")
    
    # Production Queue Status
    production = feature_analysis['production_analysis']
    if production['active_plans'] > 0:
        st.subheader("⚙️ Current Production Queue")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            for plan in production['plan_details']:
                with st.expander(f"📋 {plan['name']} ({plan['total_items']} items)"):
                    for component, count in plan['components'].items():
                        st.markdown(f"- {component}: {count}")
        
        with col2:
            st.metric("Active Plans", production['active_plans'])
            planned_total = sum(production['planned_production'].values())
            st.metric("Total Planned Items", planned_total)
    
    st.divider()
    
    # --- Development Dependency Tree ---
    st.header("🌳 Development Dependency Tree")
    
    dependency_graph, dependencies = build_dependency_tree(data)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 WSJF Priority", "🌲 Dependency Tree", "📊 Tier Analysis", "⚙️ Production Flow"])
    
    with tab1:
        st.subheader("📊 WSJF Feature Priority Analysis")
        st.markdown("*Weighted Shortest Job First scoring for strategic feature prioritization*")
        
        priority_features = analyze_feature_priorities(data)
        if priority_features:
            # Show top features table
            feature_df = pd.DataFrame(priority_features[:10])  # Top 10 features
            feature_df = feature_df[['name', 'product', 'wsjf_score', 'business_value', 'time_criticality', 'effort_estimate', 'status']]
            feature_df.columns = ['Feature', 'Product', 'WSJF Score', 'Business Value', 'Time Criticality', 'Effort Estimate', 'Progress %']
            
            st.dataframe(
                feature_df,
                use_container_width=True,
                column_config={
                    "WSJF Score": st.column_config.ProgressColumn(
                        "WSJF Score",
                        help="Weighted Shortest Job First priority score",
                        min_value=0,
                        max_value=10,
                    ),
                    "Progress %": st.column_config.ProgressColumn(
                        "Progress %",
                        help="Feature completion percentage",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
            # WSJF Score visualization
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    feature_df.head(5), 
                    x='WSJF Score', 
                    y='Feature',
                    orientation='h',
                    title='Top 5 Features by WSJF Score',
                    color='WSJF Score',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Business value vs effort scatter plot
                fig2 = px.scatter(
                    feature_df,
                    x='Effort Estimate',
                    y='Business Value',
                    size='WSJF Score',
                    color='Time Criticality',
                    hover_name='Feature',
                    title='Value vs Effort Analysis',
                    color_continuous_scale='Reds'
                )
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Strategic recommendations
            st.subheader("🎯 Strategic Recommendations")
            top_feature = priority_features[0]
            st.success(f"**Highest Priority:** {top_feature['name']} (WSJF: {top_feature['wsjf_score']:.2f})")
            st.info(f"**Focus Area:** {top_feature['product']} - Business Value: {top_feature['business_value']:.1f}/10")
            
            # Show development pipeline items separately
            dev_items = [f for f in priority_features if 'Dev)' in f['name']]
            if dev_items:
                st.subheader("🔧 Development Pipeline Priority")
                for item in dev_items[:3]:
                    with st.expander(f"⚙️ {item['name']} - WSJF: {item['wsjf_score']:.2f}"):
                        st.write(f"**Assigned to:** {item.get('employee', 'Unassigned')}")
                        st.write(f"**Status:** {item.get('state', 'Unknown')}")
                        st.write(f"**Progress:** {item['status']:.1f}%")
                        st.write(f"**Dependencies:** {', '.join(item['dependencies']) if item['dependencies'] else 'None'}")
        else:
            st.info("No features found for WSJF analysis.")
    
    with tab2:
        st.subheader("🌳 Hierarchical Dependency Tree")
        st.markdown("*Select a product/feature to see its complete dependency chain from top to bottom*")
        
        # Product/Feature selector - use enhanced feature analysis
        available_features = []
        if feature_analysis and feature_analysis['features']:
            available_features = [f['name'] for f in feature_analysis['features']]
        
        # Fallback to basic extraction if enhanced analysis failed
        if not available_features and data and 'featureInstances' in data:
            available_features = [f.get('name', f'Feature_{i}') for i, f in enumerate(data['featureInstances'])]
        
        # Add some key products for demo purposes if no features available
        if not available_features:
            available_features = ['Video Feature', 'Login System', 'Payment Gateway', 'Search Engine', 'Content Management']
        
        selected_feature = st.selectbox(
            "Select a Product/Feature to analyze:",
            available_features,
            help="Choose a product or feature to see its complete dependency hierarchy"
        )
        
        if selected_feature:
            dependency_tree_data = build_hierarchical_dependency_tree(selected_feature, dependencies)
            
            if dependency_tree_data:
                # Create hierarchical visualization using Plotly treemap or tree structure
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = create_dependency_tree_visualization(dependency_tree_data, selected_feature)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader(f"📋 Build Sequence for {selected_feature}")
                    
                    # Show build sequence from bottom to top
                    build_sequence = get_build_sequence(dependency_tree_data)
                    
                    for phase, items in build_sequence.items():
                        with st.expander(f"🔧 {phase}", expanded=True):
                            for i, item in enumerate(items, 1):
                                tier = get_item_tier(item, dependencies)
                                tier_color = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}.get(tier, "⚪")
                                st.write(f"{i}. {tier_color} **{item}** (Tier {tier})")
                    
                    st.info("💡 **Build from bottom up**: Start with Tier 1 components, then modules, then integration.")
            
            else:
                st.warning(f"No dependency data available for '{selected_feature}'. This may be a basic component with no dependencies.")
        
        # Show component legend
        st.divider()
        st.subheader("🏷️ Component Tier Legend")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("🟢 **Tier 1**  \nBasic Components  \n(No dependencies)")
        with col2:
            st.markdown("🟡 **Tier 2**  \nSimple Modules  \n(Few dependencies)")
        with col3:
            st.markdown("🟠 **Tier 3**  \nComplex Modules  \n(Multiple deps)")
        with col4:
            st.markdown("🔴 **Tier 4**  \nAdvanced Systems  \n(Many dependencies)")


def extract_real_feature_dependencies():
    """Extract real feature dependencies from save file."""
    try:
        with open('save_data/sg_momentum ai.json', 'r') as f:
            data = json.load(f)
        
        # Extract inventory
        inventory = data.get('inventory', {})
        
        # Extract feature requirements
        feature_dependencies = {}
        feature_instances = data.get('featureInstances', [])
        
        for i, feature_data in enumerate(feature_instances):
            feature_name = feature_data.get('name', f'Feature_{i}')
            requirements = feature_data.get('requirements', {})
            
            if requirements:
                # Convert requirements dict to list of components needed
                deps = []
                for component, count in requirements.items():
                    if count > 0:
                        deps.append(component)
                feature_dependencies[feature_name] = deps
            
        return feature_dependencies, inventory
    except Exception as e:
        st.error(f"Error loading feature dependencies: {e}")
        return {}, {}

def build_hierarchical_dependency_tree(feature_name, dependencies):
    """Build a hierarchical tree structure for a specific feature using real save data."""
    
    # Get real dependencies from save file
    real_dependencies, inventory = extract_real_feature_dependencies()
    
    # Use real dependencies if available, fallback to provided dependencies
    feature_deps = real_dependencies.get(feature_name, dependencies.get(feature_name, []))
    
    if not feature_deps:
        return None

    def build_tree_recursive(item, visited=None):
        """Recursively build dependency tree with inventory information."""
        if visited is None:
            visited = set()
        
        if item in visited:
            return {"name": item, "children": [], "circular": True}
        
        visited.add(item)
        
        # Get inventory count for this component
        available_count = inventory.get(item, 0)
        
        # For components, check if there are sub-dependencies
        item_deps = dependencies.get(item, [])
        children = []
        
        for dep in item_deps:
            child_tree = build_tree_recursive(dep, visited.copy())
            children.append(child_tree)
        
        return {
            "name": item,
            "children": children,
            "tier": get_item_tier(item, dependencies),
            "type": classify_item_type(item),
            "available": available_count,
            "status": "available" if available_count > 0 else "needed"
        }
    
    # Build tree for each dependency
    trees = []
    for dep in feature_deps:
        tree = build_tree_recursive(dep)
        trees.append(tree)
    
    return {
        "name": feature_name,
        "children": trees,
        "tier": len(feature_deps) + 2,
        "type": "Feature",
        "total_dependencies": len(feature_deps)
    }


def create_dependency_tree_visualization(tree_data, feature_name):
    """Create a hierarchical tree visualization using Plotly."""
    
    # Flatten tree to get all nodes and their relationships
    def flatten_tree(node, parent=None, level=0, x_pos=0.0):
        nodes = []
        edges = []
        
        # Add current node with inventory information
        node_info = {
            'name': node['name'],
            'level': level,
            'tier': node.get('tier', 1),
            'type': node.get('type', 'Unknown'),
            'x': x_pos,
            'parent': parent,
            'available': node.get('available', 0),
            'status': node.get('status', 'unknown')
        }
        nodes.append(node_info)
        
        # Add edge to parent
        if parent:
            edges.append({'from': parent, 'to': node['name']})
        
        # Process children
        children = node.get('children', [])
        if children:
            child_width = 1.0 / len(children) if len(children) > 1 else 1.0
            for i, child in enumerate(children):
                child_x = x_pos + (i - len(children)/2 + 0.5) * child_width
                child_nodes, child_edges = flatten_tree(child, node['name'], level + 1, child_x)
                nodes.extend(child_nodes)
                edges.extend(child_edges)
        
        return nodes, edges
    
    nodes, edges = flatten_tree(tree_data)
    
    # Create positions
    max_level = max(node['level'] for node in nodes) if nodes else 0
    
    # Prepare edge traces
    edge_x = []
    edge_y = []
    
    # Create a position lookup
    pos_lookup = {node['name']: (node['x'], -node['level']) for node in nodes}
    
    for edge in edges:
        if edge['from'] in pos_lookup and edge['to'] in pos_lookup:
            x0, y0 = pos_lookup[edge['from']]
            x1, y1 = pos_lookup[edge['to']]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Prepare node traces with inventory information
    node_x = [node['x'] for node in nodes]
    node_y = [-node['level'] for node in nodes]
    node_text = []
    node_hover = []
    node_colors = []
    
    for node in nodes:
        # Create display text with inventory count
        display_name = node['name'].replace('Component', '').replace('Module', '')
        if node.get('available', 0) > 0:
            display_name += f"({node['available']})"
        node_text.append(display_name)
        
        # Create hover text with full information
        hover_text = f"{node['name']}<br>Tier {node['tier']}<br>Level {node['level']}<br>Type: {node['type']}"
        if 'available' in node:
            hover_text += f"<br>Available: {node['available']}"
            hover_text += f"<br>Status: {node['status']}"
        node_hover.append(hover_text)
        
        # Color by availability status
        if node['type'] == 'Feature':
            node_colors.append('#4CAF50')  # Green for features
        elif node.get('status') == 'available':
            node_colors.append('#81C784')  # Light green for available components
        elif node.get('status') == 'needed':
            node_colors.append('#F44336')  # Red for needed components
        else:
            # Fallback to tier coloring
            tier_colors = {1: '#90EE90', 2: '#FFD700', 3: '#FFA500', 4: '#FF6347', 5: '#9370DB'}
            node_colors.append(tier_colors.get(node['tier'], '#808080'))
    
    # Size by level (root larger)
    node_sizes = [30 if node['level'] == 0 else 20 if node['level'] == 1 else 15 for node in nodes]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        hovertext=node_hover,
        textposition="middle center",
        textfont=dict(size=10, color='black'),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='black')
        )
    )
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text=f'Live Dependency Status for {feature_name}<br><sub>Real inventory: Green=Available, Red=Needed (counts shown)</sub>',
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=40, l=40, r=40, t=80),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
            plot_bgcolor='rgba(0,0,0,0)'
        )
    )
    
    return fig


def get_build_sequence(tree_data):
    """Generate build sequence from dependency tree."""
    def collect_items_by_tier(node, items_by_tier=None):
        if items_by_tier is None:
            items_by_tier = {}
        
        tier = node.get('tier', 1)
        if tier not in items_by_tier:
            items_by_tier[tier] = []
        
        if node['name'] not in items_by_tier[tier]:
            items_by_tier[tier].append(node['name'])
        
        for child in node.get('children', []):
            collect_items_by_tier(child, items_by_tier)
        
        return items_by_tier
    
    items_by_tier = collect_items_by_tier(tree_data)
    
    # Create build phases
    build_sequence = {}
    
    for tier in sorted(items_by_tier.keys()):
        items = items_by_tier[tier]
        if tier == 1:
            phase_name = "Phase 1: Core Components"
        elif tier == 2:
            phase_name = "Phase 2: Basic Modules"
        elif tier == 3:
            phase_name = "Phase 3: Complex Modules"
        elif tier == 4:
            phase_name = "Phase 4: Advanced Systems"
        else:
            phase_name = f"Phase {tier}: Integration & Features"
        
        build_sequence[phase_name] = items
    
    return build_sequence


def get_item_tier(item, dependencies):
    """Get the tier level of an item."""
    return calculate_dependency_tier(item, dependencies)
    
    with tab3:
        st.subheader("Tier Distribution Analysis")
        
        # Analyze tier distribution
        tier_data = {}
        for node in dependency_graph.nodes():
            tier = dependency_graph.nodes[node].get('tier', 1)
            node_type = dependency_graph.nodes[node].get('type', 'Unknown')
            
            if tier not in tier_data:
                tier_data[tier] = {'Component': 0, 'Module': 0, 'UI': 0, 'System': 0, 'items': []}
            
            tier_data[tier][node_type] += 1
            tier_data[tier]['items'].append(node)
        
        # Display tier breakdown
        for tier in sorted(tier_data.keys()):
            tier_info = tier_data[tier]
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.metric(f"**Tier {tier}**", f"{sum(tier_info[k] for k in ['Component', 'Module', 'UI', 'System'])}")
                st.write(f"Components: {tier_info['Component']}")
                st.write(f"Modules: {tier_info['Module']}")
                st.write(f"UI Elements: {tier_info['UI']}")
                st.write(f"System: {tier_info['System']}")
            
            with col2:
                st.write(f"**Tier {tier} Items:**")
                items_per_row = 4
                items = tier_info['items']
                for i in range(0, len(items), items_per_row):
                    row_items = items[i:i+items_per_row]
                    st.write(" • ".join(row_items))
    
    with tab4:
        st.subheader("Production Flow Optimization")
        
        # Current inventory analysis
        inventory = data.get('inventory', {})
        
        st.write("**Current Inventory vs Dependency Requirements:**")
        
        inventory_df = pd.DataFrame([
            {
                'Item': item,
                'Current Stock': inventory.get(item, 0),
                'Tier': dependency_graph.nodes[item].get('tier', 1) if item in dependency_graph.nodes else 'Unknown',
                'Type': dependency_graph.nodes[item].get('type', 'Unknown') if item in dependency_graph.nodes else 'Unknown'
            }
            for item in sorted(set(list(inventory.keys()) + list(dependency_graph.nodes())))
            if item in inventory or item in dependency_graph.nodes
        ])
        
        # Filter and sort by tier for production planning
        inventory_df = inventory_df.sort_values(['Tier', 'Type', 'Item'])
        
        st.dataframe(
            inventory_df,
            use_container_width=True,
            column_config={
                "Current Stock": st.column_config.NumberColumn(
                    "Current Stock",
                    help="Available inventory",
                    format="%d"
                ),
                "Tier": st.column_config.NumberColumn(
                    "Tier",
                    help="Dependency tier (1=no deps, higher=more complex)",
                    format="%d"
                )
            }
        )
    
    st.divider()
    
    # --- Team Hierarchy Analysis ---
    st.header("👥 Team Hierarchy & Dependency Coverage")
    
    team_analysis = analyze_team_hierarchy(data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Team Structure")
        
        if team_analysis['employee_details']:
            team_df = pd.DataFrame([
                {
                    'Employee': emp['name'],
                    'Role': emp['role'],
                    'Level': emp['level'],
                    'Speed': emp['speed'],
                    'Recommended Tier': emp['recommended_tier'],
                    'Complexity Rating': f"{emp['complexity_rating']:.1f}",
                    'Queue Items': emp['current_queue']
                }
                for emp in team_analysis['employee_details']
            ])
            
            st.dataframe(
                team_df,
                use_container_width=True,
                column_config={
                    "Speed": st.column_config.NumberColumn(format="%d"),
                    "Recommended Tier": st.column_config.NumberColumn(
                        "Recommended Tier",
                        help="1=Basic components, 2=Simple modules, 3=Complex modules, 4=Advanced systems",
                        format="%d"
                    ),
                    "Complexity Rating": st.column_config.NumberColumn(format="%.1f")
                }
            )
        else:
            st.info("No employees found in current save data.")
    
    with col2:
        st.subheader("Tier Coverage Analysis")
        
        if team_analysis['tier_coverage']:
            tier_coverage_df = pd.DataFrame([
                {'Tier': tier, 'Employees': count}
                for tier, count in sorted(team_analysis['tier_coverage'].items())
            ])
            
            fig = px.bar(
                tier_coverage_df,
                x='Tier',
                y='Employees',
                title="Team Distribution by Tier",
                color='Employees',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Hierarchy Recommendations")
        
        if team_analysis.get('hierarchy_recommendations'):
            for rec in team_analysis['hierarchy_recommendations']:
                if rec['priority'] == 'Critical':
                    st.error(f"🚨 **{rec['issue']}**")
                elif rec['priority'] == 'High':
                    st.warning(f"⚠️ **{rec['issue']}**")
                else:
                    st.info(f"💡 **{rec['issue']}**")
                
                st.write(f"*Recommendation*: {rec['recommendation']}")
                st.write(f"*Impact*: {rec['impact']}")
                st.write("")
        else:
            st.success("✅ Team hierarchy appears well-balanced!")
    
    st.divider()
    
    # --- Feature Development Pipeline ---
    st.header("🔧 Feature Development Pipeline")
    
    feature_analysis = analyze_feature_development(data)
    if feature_analysis:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Feature Status & Priorities")
            
            # Create feature DataFrame
            feature_df = pd.DataFrame([
                {
                    'Feature': f['name'],
                    'Status': '🟢 Active' if f['activated'] else '🔴 Inactive',
                    'Quality': f['current_quality'],
                    'Efficiency': f['current_efficiency'],
                    'Completion': f'{f["completion_ratio"]:.1f}%',
                    'Upgrade Priority': f'{f["upgrade_priority"]:.1f}%'
                }
                for f in feature_analysis['feature_details']
            ])
            
            st.dataframe(
                feature_df,
                use_container_width=True,
                column_config={
                    "Completion": st.column_config.ProgressColumn(
                        "Completion",
                        help="Component availability vs requirements",
                        min_value=0,
                        max_value=100,
                    ),
                    "Upgrade Priority": st.column_config.ProgressColumn(
                        "Upgrade Priority",
                        help="Potential for quality/efficiency improvements",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
        
        with col2:
            st.subheader("Component Requirements")
            
            if feature_analysis['component_needs']:
                component_df = pd.DataFrame([
                    {'Component': comp, 'Shortage': shortage}
                    for comp, shortage in feature_analysis['component_needs'].items()
                ])
                
                st.dataframe(component_df, use_container_width=True)
                
                # Production priority chart
                fig = px.bar(
                    component_df,
                    x='Shortage',
                    y='Component',
                    orientation='h',
                    title="Production Priorities",
                    color='Shortage',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ All component requirements met!")
    
    # --- Development Recommendations ---
    st.header("🎯 Development Recommendations")
    
    if feature_analysis:
        recommendations = []
        
        # Priority feature upgrades
        top_features = [f for f in feature_analysis['feature_details'] if f['upgrade_priority'] > 50]
        if top_features:
            for feature in top_features[:3]:  # Top 3
                recommendations.append({
                    'priority': 'High',
                    'action': f"Upgrade {feature['name']}",
                    'reason': f"High upgrade potential ({feature['upgrade_priority']:.1f}%)",
                    'impact': 'Product Quality & Efficiency'
                })
        
        # Component production needs
        if feature_analysis['component_needs']:
            top_component = max(feature_analysis['component_needs'].items(), key=lambda x: x[1])
            recommendations.append({
                'priority': 'Medium',
                'action': f"Increase {top_component[0]} production",
                'reason': f"Shortage of {top_component[1]} units blocking feature development",
                'impact': 'Feature Completion'
            })
        
        # Team hierarchy recommendations
        if team_analysis.get('hierarchy_recommendations'):
            for rec in team_analysis['hierarchy_recommendations'][:2]:  # Top 2
                recommendations.append({
                    'priority': rec['priority'],
                    'action': rec['recommendation'],
                    'reason': rec['issue'],
                    'impact': rec['impact']
                })
        
        if recommendations:
            for i, rec in enumerate(recommendations):
                priority_color = {'Critical': '🔴', 'High': '�', 'Medium': '�', 'Low': '🟢'}.get(rec['priority'], '⚪')
                st.write(f"{priority_color} **{rec['priority']} Priority**: {rec['action']}")
                st.write(f"   *Reason*: {rec['reason']}")
                st.write(f"   *Impact*: {rec['impact']}")
                st.write("")
        else:
            st.info("No specific recommendations at this time. System is operating optimally.")

def show_human_resources(data):
    """Human resources analytics and recruitment intelligence."""
    st.title("👥 Human Resources")
    st.markdown("**Talent acquisition and workforce optimization**")
    
    # Smart Hiring Analysis (NEW)
    st.header("🎯 Strategic Hiring Analysis")
    hiring_analysis = analyze_hiring_needs(data)
    
    if hiring_analysis['urgent_needs']:
        st.subheader("🚨 Urgent Hiring Needs")
        for need in hiring_analysis['urgent_needs']:
            st.error(f"**{need['role']}**: {need['reason']}")
            st.write(f"Focus: {need['component_focus']}")
    
    if hiring_analysis['hiring_priorities']:
        st.subheader("📋 Hiring Priority Queue")
        for priority in hiring_analysis['hiring_priorities'][:5]:  # Show top 5
            urgency_icon = {'URGENT': '🚨', 'HIGH': '⚡', 'MEDIUM': '📋'}[priority['urgency']]
            st.write(f"{urgency_icon} **{priority['role']}** - {priority['reason']}")
    
    # Instant Hire Suggestions
    candidates = data.get("candidates", [])
    if candidates and hiring_analysis['urgent_needs']:
        st.subheader("⚡ Instant Hire Recommendations")
        instant_hire_suggestions = generate_instant_hire_suggestion(hiring_analysis, candidates)
        
        if instant_hire_suggestions['has_suggestions']:
            for suggestion in instant_hire_suggestions['suggestions']:
                candidate = suggestion['recommended_candidate']
                need = suggestion['need']
                
                with st.expander(f"🎯 Hire {candidate['name']} for {need['role']}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Candidate:** {candidate['name']}")
                        st.write(f"**Speed:** {candidate['speed']}")
                        st.write(f"**Level:** {candidate['level']}")
                        st.write(f"**Expected Salary:** ${candidate['expected_salary']:,}")
                    
                    with col2:
                        st.write(f"**Addresses:** {need['component_focus']}")
                        st.write(f"**Urgency:** {need['urgency']}")
                        recommendation = candidate['hire_recommendation']['overall_recommendation']
                        rec_color = {'INSTANT_HIRE': '🟢', 'STRONG_CANDIDATE': '🟡', 'CONSIDER': '🟠'}.get(recommendation, '⚪')
                        st.write(f"**Recommendation:** {rec_color} {recommendation}")
                    
                    st.success(f"💡 {suggestion['justification']}")
                    
                    if st.button(f"💰 Instant Hire {candidate['name']}", key=f"hire_{candidate['name']}"):
                        st.success(f"✅ Would hire {candidate['name']} for ${candidate['expected_salary']:,} (Feature not implemented)")
        else:
            st.info("No instant hire candidates available for urgent needs.")
    
    # Targeted Recruitment by Role
    if hiring_analysis['recommended_actions']:
        st.header("🔍 Targeted Recruitment")
        
        for action in hiring_analysis['recommended_actions']:
            role = action['role']
            
            with st.expander(f"{action['message']}", expanded=False):
                st.write(f"**Focus:** {action['focus']}")
                st.write(f"**Timeline:** {action['timeline']}")
                st.write(f"**Reason:** {action['reason']}")
                
                if candidates:
                    # Show filtered candidates for this role
                    role_candidates = get_top_candidates_for_role(candidates, role, 3)
                    
                    if role_candidates:
                        st.write(f"**Top {role} Candidates:**")
                        
                        for i, candidate in enumerate(role_candidates):
                            rec = candidate['hire_recommendation']['overall_recommendation']
                            rec_icon = {'INSTANT_HIRE': '🟢', 'STRONG_CANDIDATE': '🟡', 'CONSIDER': '🟠', 'PASS': '🔴'}[rec]
                            
                            st.write(f"{i+1}. {rec_icon} **{candidate['name']}** - Speed: {candidate['speed']}, Salary: ${candidate['expected_salary']:,}")
                    else:
                        st.write(f"❌ No {role} candidates available")
    
    # Professional Development section
    st.header("📚 Professional Development")
    dev_plan = generate_professional_development_plan(data)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Training Opportunities", dev_plan['total_training_opportunities'])
    with col2:
        st.metric("High Priority Training", len(dev_plan['high_priority_training']))
    with col3:
        st.metric("Estimated Cost", f"${dev_plan['estimated_total_cost']:,}")
    
    # High Priority Training
    if dev_plan['high_priority_training']:
        st.subheader("🚨 Urgent Training Needs")
        for training in dev_plan['high_priority_training']:
            with st.expander(f"{training['employee']} - {training['training_need']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Role:** {training['type']}")
                    st.write(f"**Priority:** {training['priority']}")
                with col2:
                    st.write(f"**Duration:** {training['estimated_duration']}")
                    st.write(f"**Outcome:** {training['expected_outcome']}")
    
    # Training Schedule
    if dev_plan['recommended_schedule']:
        st.subheader("📅 Recommended Training Schedule")
        schedule_df = pd.DataFrame(dev_plan['recommended_schedule'])
        st.dataframe(schedule_df, use_container_width=True)
    
    # Current Team Analysis
    st.header("👥 Current Team Analysis")
    
    # Sales Team
    sales_analysis = analyze_sales_team(data)
    if sales_analysis['sales_executives']:
        st.subheader("💼 Sales Team")
        for exec_data in sales_analysis['sales_executives']:
            with st.expander(f"🎯 {exec_data['name']} - Sales Executive", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Level:** {exec_data['level']}")
                    st.write(f"**Speed:** {exec_data['speed']}")
                    st.write(f"**Salary:** ${exec_data['salary']:,}")
                with col2:
                    st.write(f"**Active Leads:** {exec_data['total_leads']}")
                    st.write(f"**Capacity:** {exec_data['capacity']}")
                
                if exec_data['leads']:
                    st.write("**Lead Portfolio:**")
                    for i, lead in enumerate(exec_data['leads']):
                        priority_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}[lead['priority']]
                        st.write(f"{priority_icon} Lead {i+1}: {lead['impressions']:,} impressions ({lead['priority']} priority)")
    
    # Research Team
    research_analysis = analyze_research_team(data)
    if research_analysis['researchers']:
        st.subheader("🔬 Research Team")
        for researcher in research_analysis['researchers']:
            with st.expander(f"🧪 {researcher['name']} - Researcher", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Level:** {researcher['level']}")
                    st.write(f"**Speed:** {researcher['speed']:.0f}")
                    st.write(f"**Salary:** ${researcher['salary']:,}")
                with col2:
                    st.write(f"**Research Skill:** {researcher.get('research_skill', 'N/A')}")
                    training = researcher['training_opportunity']
                    if training['has_opportunities']:
                        st.write(f"**Training Needed:** ⚠️ {len(training['training_needs'])} areas")
                    else:
                        st.write("**Training Status:** ✅ Up to date")
    
    # Development Team
    dev_analysis = analyze_developer_teams(data)
    all_devs = dev_analysis['developers'] + dev_analysis['designers'] + dev_analysis['lead_developers']
    
    if all_devs:
        st.subheader("💻 Development Team")
        for dev in all_devs:
            role_icon = {'Developer': '👨‍💻', 'Designer': '🎨', 'LeadDeveloper': '👨‍💼'}
            icon = role_icon.get(dev['type'], '👤')
            
            with st.expander(f"{icon} {dev['name']} - {dev['type']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Level:** {dev['level']}")
                    st.write(f"**Speed:** {dev['speed']:.0f}")
                    st.write(f"**Salary:** ${dev['salary']:,}")
                with col2:
                    if dev['skills']:
                        st.write("**Skills:**")
                        for skill, value in dev['skills'].items():
                            st.write(f"  {skill}: {value}")
                    
                    training = dev['training_opportunities']
                    if training['has_opportunities']:
                        st.write(f"**Training Opportunities:** {len(training['training_needs'])}")
                    else:
                        st.write("**Training Status:** ✅ Optimal")
    
    # General Recruitment Intelligence section
    st.header("📊 Recruitment Market Analysis")
    if candidates:
        candidate_list = []
        for c in candidates:
            # Fixed: Salary field is actually their expected salary for instant hire
            expected_salary = c.get('salary', 0)
            
            candidate_list.append({
                "Name": c.get("name"),
                "Role": c.get("employeeTypeName"),
                "Level": c.get("level"),
                "Speed": c.get("speed"),
                "Expected Salary": expected_salary  # This is what they want to be hired
            })
        
        df_candidates = pd.DataFrame(candidate_list)
        st.dataframe(df_candidates, use_container_width=True,
                       column_config={
                           "Expected Salary": st.column_config.NumberColumn(format="$%d"),
                       })
        
        # Recruitment market analysis
        st.subheader("� Market Analysis by Role")
        
        # Analyze candidate market
        role_summary = {}
        for candidate in candidates:
            role = candidate.get('employeeTypeName', 'Unknown')
            if role not in role_summary:
                role_summary[role] = {'count': 0, 'avg_salary': 0, 'salaries': []}
            
            role_summary[role]['count'] += 1
            role_summary[role]['salaries'].append(candidate.get('salary', 0))
        
        for role, stats in role_summary.items():
            if stats['salaries']:
                avg_salary = sum(stats['salaries']) / len(stats['salaries'])
                min_salary = min(stats['salaries'])
                max_salary = max(stats['salaries'])
                
                st.write(f"**{role}**: {stats['count']} available")
                st.write(f"  💰 Salary range: ${min_salary:,} - ${max_salary:,} (avg: ${avg_salary:,.0f})")
    else:
        st.info("No active candidates to display.")

def show_research_development(data):
    """Research and development planning and progress tracking."""
    st.title("🔬 Research & Development")
    st.markdown("**Technology advancement and innovation pipeline**")
    
    # Research Progress section (moved from main dashboard)
    researched_items = data.get("researchedItems", [])
    
    st.subheader("🎓 Unlocked Technologies")
    if researched_items:
        # Display in multiple columns for better readability
        num_columns = 4
        cols = st.columns(num_columns)
        for i, item in enumerate(sorted(researched_items)):
            cols[i % num_columns].markdown(f"- {item}")
    else:
        st.info("No research completed yet.")

def show_daily_standup(data):
    """Daily standup agenda with focused team management - only work queue adjustable roles."""
    st.title("📅 Daily Standup")
    st.markdown("**Team status for developers, designers, marketers, and SysAdmins with adjustable work queues**")
    st.markdown("*Excludes researchers (training-focused) and CEO (executive meetings)*")
    st.markdown("---")
    
    # Use focused team management to get only manageable team members
    team_analysis = analyze_manageable_team_members(data)
    
    if not team_analysis['manageable_team']:
        st.warning("No team members with adjustable work queues found.")
        return
    
    # Overview metrics
    st.header("📊 Team Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_members = len(team_analysis['manageable_team'])
        st.metric("Team Members", total_members)
    
    with col2:
        available_members = len([m for m in team_analysis['manageable_team'] if m['availability'] == 'Available'])
        st.metric("Available", available_members)
    
    with col3:
        avg_productivity = sum(m['productivity_score'] for m in team_analysis['manageable_team']) / total_members
        st.metric("Avg Productivity", f"{avg_productivity:.1f}%")
    
    with col4:
        high_priority_tasks = team_analysis['high_priority_assignments']
        st.metric("High Priority Tasks", len(high_priority_tasks))
    
    # High Priority Assignments
    if team_analysis['high_priority_assignments']:
        st.header("🚨 High Priority Assignments")
        
        for assignment in team_analysis['high_priority_assignments']:
            st.error(f"**{assignment['component']}** → **{assignment['assigned_to']}**")
            st.markdown(f"   📝 *{assignment['reason']}*")
    
    # Team Member Status
    st.header("� Individual Status Updates")
    
    # Group by role for better organization
    roles = {}
    for member in team_analysis['manageable_team']:
        role = member['role']
        if role not in roles:
            roles[role] = []
        roles[role].append(member)
    
    for role, members in roles.items():
        st.subheader(f"🏷️ {role}s ({len(members)})")
        
        for member in members:
            status_icon = {
                'Available': '�',
                'Busy': '🟡', 
                'Assigned': '�',
                'Training': '�'
            }.get(member['availability'], '⚪')
            
            with st.expander(f"{status_icon} {member['name']} (Level {member['level']})", expanded=False):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Status:** {member['availability']}")
                    st.markdown(f"**Specialization:** {member['specialization']}")
                    st.markdown(f"**Current Task:** {member['current_assignment']}")
                    
                    # Productivity bar
                    productivity = member['productivity_score']
                    productivity_bar = '█' * int(productivity / 20) + '░' * (5 - int(productivity / 20))
                    st.markdown(f"**Productivity:** {productivity_bar} ({productivity:.1f}%)")
                
                with col2:
                    # Work queue recommendations
                    if member['work_queue_recommendations']:
                        st.markdown("**Queue Recommendations:**")
                        for rec in member['work_queue_recommendations']:
                            priority_color = {
                                'HIGH': '🔴',
                                'MEDIUM': '🟡',
                                'LOW': '🟢'
                            }.get(rec['priority'], '⚪')
                            
                            st.markdown(f"{priority_color} {rec['task']} ({rec['priority']})")
                    else:
                        st.success("✅ Optimally assigned")
    
    # Team Capacity Analysis
    st.header("📈 Team Capacity Analysis")
    
    capacity_data = team_analysis['capacity_analysis']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Role Distribution")
        
        # Create role distribution chart
        role_counts = {}
        for member in team_analysis['manageable_team']:
            role = member['role']
            role_counts[role] = role_counts.get(role, 0) + 1
        
        if role_counts:
            role_df = pd.DataFrame([
                {'Role': role, 'Count': count}
                for role, count in role_counts.items()
            ])
            
            fig = px.pie(role_df, values='Count', names='Role', 
                        title='Team Composition')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Capacity Utilization")
        
        # Show capacity by role
        for role in capacity_data:
            role_info = capacity_data[role]
            utilization = role_info['utilization']
            
            if utilization >= 90:
                st.error(f"🔴 **{role}**: {utilization:.1f}% (Overloaded)")
            elif utilization >= 75:
                st.warning(f"🟡 **{role}**: {utilization:.1f}% (High Load)")
            else:
                st.success(f"🟢 **{role}**: {utilization:.1f}% (Good)")
    
    # Action Items Summary
    st.header("✅ Action Items")
    
    action_items = []
    
    # Generate action items based on team analysis
    for assignment in team_analysis['high_priority_assignments']:
        action_items.append(f"🚨 **URGENT**: {assignment['assigned_to']} focus on {assignment['component']}")
    
    for role, info in capacity_data.items():
        if info['utilization'] > 90:
            action_items.append(f"⚡ **{role} Team**: Reduce workload or add capacity")
        elif info['utilization'] < 40:
            action_items.append(f"💡 **{role} Team**: Available for additional tasks")
    
    # Check for training opportunities
    for member in team_analysis['manageable_team']:
        if member['level'] < 3 and member['availability'] == 'Available':
            action_items.append(f"📚 **{member['name']}**: Consider training to improve skills")
    
    if action_items:
        for item in action_items:
            st.write(item)
    else:
        st.success("🎉 No immediate action items - team is optimally balanced!")
    
    # Standup Meeting Notes Template
    st.header("📝 Meeting Notes Template")
    
    with st.expander("📋 Standup Notes", expanded=False):
        st.markdown("### Team Standup - " + datetime.now().strftime("%Y-%m-%d"))
        st.markdown("**Attendees:**")
        for member in team_analysis['manageable_team']:
            st.markdown(f"- {member['name']} ({member['role']})")
        
        st.markdown("\n**High Priority Items:**")
        for assignment in team_analysis['high_priority_assignments']:
            st.markdown(f"- {assignment['component']} (Assigned: {assignment['assigned_to']})")
        
        st.markdown("\n**Team Capacity:**")
        for role, info in capacity_data.items():
            st.markdown(f"- {role}: {info['utilization']:.1f}% utilization")
        
        st.markdown("\n**Next Steps:**")
        st.markdown("- [ ] Complete high-priority assignments")
        st.markdown("- [ ] Monitor team capacity levels")
        st.markdown("- [ ] Address any overloaded team members")

def show_production_planning(data):
    """Production capacity analysis and work queue optimization."""
    st.title("📋 Production Planning")
    st.markdown("**Capacity analysis and workflow optimization**")
    
    # Analyze production requirements
    production_requirements = analyze_production_requirements(data)
    
    # Show production status overview
    st.header("📊 Production Status Overview")
    features_summary = production_requirements['features_summary']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔄 In Development", features_summary['in_development'])
    with col2:
        st.metric("⏳ Needs Development", features_summary['needs_development'])
    with col3:
        st.metric("🎨 Needs Art", features_summary['needs_art'])
    with col4:
        st.metric("✅ Completed", features_summary['completed'])
    
    # Capacity analysis
    st.header("⚡ Capacity Analysis")
    capacity_analysis = production_requirements['capacity_analysis']
    
    # Create capacity visualization
    skills = list(capacity_analysis.keys())
    demand_values = [capacity_analysis[skill]['demand'] for skill in skills]
    available_values = [capacity_analysis[skill]['available'] for skill in skills]
    utilization_values = [capacity_analysis[skill]['utilization'] for skill in skills]
    
    # Capacity chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Demand',
        x=skills,
        y=demand_values,
        marker_color='lightcoral'
    ))
    
    fig.add_trace(go.Bar(
        name='Available',
        x=skills,
        y=available_values,
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title="Skill Demand vs Available Capacity",
        xaxis_title="Skills",
        yaxis_title="Capacity Units",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Utilization chart
    fig_util = go.Figure(data=[
        go.Bar(x=skills, y=utilization_values, marker_color='green')
    ])
    
    fig_util.update_layout(
        title="Skill Utilization Rates",
        xaxis_title="Skills",
        yaxis_title="Utilization %",
        yaxis=dict(range=[0, 150])  # Show up to 150% to highlight overutilization
    )
    
    # Add reference line at 100%
    fig_util.add_hline(y=100, line_dash="dash", line_color="red", 
                       annotation_text="100% Capacity")
    
    st.plotly_chart(fig_util, use_container_width=True)
    
    # Recommendations
    st.header("💡 Work Queue Recommendations")
    recommendations = production_requirements['recommendations']
    
    if recommendations:
        # Group recommendations by priority
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        medium_priority = [r for r in recommendations if r['priority'] == 'MEDIUM']
        low_priority = [r for r in recommendations if r['priority'] == 'LOW']
        
        if high_priority:
            st.subheader("🚨 High Priority Actions")
            for rec in high_priority:
                st.error(f"**{rec['type']}**: {rec['message']}")
                st.write(f"Impact: {rec['impact']}")
                st.write("")
        
        if medium_priority:
            st.subheader("⚠️ Medium Priority Actions")
            for rec in medium_priority:
                st.warning(f"**{rec['type']}**: {rec['message']}")
                st.write(f"Impact: {rec['impact']}")
                st.write("")
        
        if low_priority:
            st.subheader("💡 Low Priority Optimizations")
            for rec in low_priority:
                st.info(f"**{rec['type']}**: {rec['message']}")
                st.write(f"Impact: {rec['impact']}")
                st.write("")
    else:
        st.success("🎉 Production capacity is well-balanced! No immediate actions required.")

def show_sales_team_meeting(data):
    """Sales team meeting with Annie's lead management and negotiation strategy."""
    st.title("💼 Sales Team Meeting")
    st.markdown("**Lead management, negotiation strategy, and sales optimization**")
    
    # Analyze sales team
    sales_analysis = analyze_sales_team(data)
    
    if not sales_analysis['sales_executives']:
        st.warning("No sales executives found in the team.")
        return
    
    # Sales team overview
    st.header("📊 Sales Team Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sales Executives", len(sales_analysis['sales_executives']))
    with col2:
        st.metric("Total Active Leads", sales_analysis['total_leads'])
    with col3:
        st.metric("High Priority Leads", sales_analysis['high_priority_leads'])
    
    # Individual sales executive analysis
    for exec_data in sales_analysis['sales_executives']:
        st.header(f"🎯 {exec_data['name']} - Sales Executive Analysis")
        
        # Executive summary
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Executive Profile")
            st.write(f"**Level:** {exec_data['level']}")
            st.write(f"**Speed:** {exec_data['speed']}")
            st.write(f"**Salary:** ${exec_data['salary']:,}")
            st.write(f"**Mood:** {exec_data['mood']:.1f}%")
        
        with col2:
            st.subheader("💼 Current Workload")
            st.write(f"**Active Leads:** {exec_data['total_leads']}")
            st.write(f"**Capacity Assessment:** {exec_data['capacity']}")
            
            # Capacity visualization
            if exec_data['level'] == 'Beginner':
                max_recommended = 1
            elif exec_data['level'] == 'Intermediate':
                max_recommended = 2
            else:
                max_recommended = 3
            
            capacity_usage = (exec_data['total_leads'] / max_recommended) * 100
            st.progress(min(capacity_usage / 100, 1.0), text=f"Capacity Usage: {capacity_usage:.0f}%")
        
        # Lead portfolio analysis
        if exec_data['leads']:
            st.subheader("📈 Lead Portfolio Management")
            
            # Create lead analysis table
            lead_data = []
            for i, lead in enumerate(exec_data['leads']):
                # Try to map competitor IDs to company names (simplified)
                company_names = {
                    'd454a2f2-bded-4b09fdfsg': 'Oregano Corp',
                    '88885275-55bb-42d8-a8d8-5999032a5d95': 'Indie Shows',
                    '1ce30d18-ca93-4299-9160-dab4e1bd9711': 'Greenbook Ltd'
                }
                
                company_name = company_names.get(lead['competitor_id'], f"Company {i+1}")
                
                lead_data.append({
                    'Company': company_name,
                    'Impressions': f"{lead['impressions']:,}",
                    'Priority': lead['priority'],
                    'Value Assessment': lead['urgency'],
                    'Last Contact': lead['timestamp'][:10] if lead['timestamp'] else 'N/A'
                })
            
            df_leads = pd.DataFrame(lead_data)
            st.dataframe(df_leads, use_container_width=True)
            
            # Lead prioritization strategy
            st.subheader("🎯 Recommended Lead Strategy")
            
            if exec_data['level'] == 'Beginner' and len(exec_data['leads']) > 1:
                highest_lead = exec_data['leads'][0]  # Already sorted by priority
                company_name = company_names.get(highest_lead['competitor_id'], 'Top Lead')
                
                st.warning(f"**Focus Strategy Recommended**: {exec_data['name']} should focus exclusively on **{company_name}** ({highest_lead['impressions']:,} impressions)")
                st.write("**Rationale**: Beginner-level executives perform better with single-lead focus")
                st.write("**Action Plan**:")
                st.write("1. ✅ Prioritize all communication with this lead")
                st.write("2. ⏸️ Put other leads on hold or reassign")
                st.write("3. 🎯 Develop tailored proposal for this client")
                st.write("4. 📅 Schedule follow-up meeting within 48 hours")
            
            # Individual lead recommendations
            st.subheader("📋 Lead-by-Lead Action Plan")
            
            for i, lead in enumerate(exec_data['leads']):
                company_name = company_names.get(lead['competitor_id'], f"Company {i+1}")
                
                with st.expander(f"{lead['priority']} Priority: {company_name} ({lead['impressions']:,} impressions)", expanded=i==0):
                    
                    # Display quantitative lead data only
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Lead Value", f"{lead['impressions']:,} impressions")
                    with col2:
                        st.metric("Priority Level", lead['priority'])
                    with col3:
                        # Calculate contact urgency based on data
                        if lead['priority'] == 'HIGH':
                            st.metric("Contact Within", "24 hours", delta="URGENT")
                        elif lead['priority'] == 'MEDIUM':
                            st.metric("Contact Within", "3-5 days", delta="Normal")
                        else:
                            st.metric("Contact Within", "Weekly check", delta="Low")
                    
                    # Data-driven action based on impression thresholds
                    st.markdown("**Data-Driven Actions:**")
                    if lead['impressions'] >= 200000:
                        st.info("📊 High-value lead detected (>200k impressions)")
                        st.markdown("• **Action**: Schedule immediate contact")
                        st.markdown("• **Data Point**: Premium client tier qualified")
                    elif lead['impressions'] >= 50000:
                        st.info("📊 Medium-value lead (50k-200k impressions)")
                        st.markdown("• **Action**: Contact within 3 business days")
                        st.markdown("• **Data Point**: Standard client tier")
                    else:
                        st.info("� Standard lead (<50k impressions)")
                        st.markdown("• **Action**: Weekly nurture sequence")
                        st.markdown("• **Data Point**: Entry-level client tier")
        
        else:
            st.info(f"{exec_data['name']} currently has no active leads.")
            
            # Data-driven lead generation metrics instead of abstract advice
            st.markdown("**Lead Generation Status:**")
            st.markdown("• **Current Pipeline**: 0 active leads")
            st.markdown("• **Required Action**: Initiate prospecting activities")
            st.markdown("• **Target**: Generate 3-5 qualified leads per week")
    
    # Replace abstract recommendations with data-driven metrics
    if sales_analysis.get('team_metrics'):
        st.header("� Sales Performance Metrics")
        
        # Calculate actual performance data
        total_pipeline_value = sum(
            sum(lead['impressions'] for lead in exec_data['leads'])
            for exec_data in sales_analysis['sales_executives']
        )
        active_leads_count = sum(
            len(exec_data['leads']) 
            for exec_data in sales_analysis['sales_executives']
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Pipeline Value", f"{total_pipeline_value:,} impressions")
        with col2:
            st.metric("Active Leads", active_leads_count)
        with col3:
            avg_lead_value = total_pipeline_value / max(active_leads_count, 1)
            st.metric("Average Lead Value", f"{avg_lead_value:,.0f} impressions")
    
    # Sales performance metrics
    st.header("📈 Sales Performance Metrics")
    
    # Calculate team performance indicators based on actual data
    total_impressions = sum(
        sum(lead['impressions'] for lead in exec_data['leads']) 
        for exec_data in sales_analysis['sales_executives']
    )
    
    avg_lead_value = total_impressions / max(sales_analysis.get('total_leads', 1), 1)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pipeline Value", f"{total_impressions:,} impressions")
    with col2:
        st.metric("Average Lead Value", f"{avg_lead_value:,.0f} impressions")
    with col3:
        # This would need more game data for actual conversion rates
        st.metric("Pipeline Health", "⚡ Active")
    
    # Action items summary
    st.header("✅ Action Items Summary")
    
    action_items = []
    for exec_data in sales_analysis['sales_executives']:
        name = exec_data['name']
        
        if not exec_data['leads']:
            action_items.append(f"🔍 **{name}**: Begin immediate lead generation activities")
        elif exec_data['level'] == 'Beginner' and len(exec_data['leads']) > 1:
            action_items.append(f"🎯 **{name}**: Focus on highest-priority lead only")
        
        for lead in exec_data['leads']:
            if lead['priority'] == 'HIGH':
                action_items.append(f"🚨 **{name}**: Contact high-priority lead within 24 hours")
                break
    
    if action_items:
        for item in action_items:
            st.write(item)
    else:
        st.success("🎉 No immediate action items. Team is operating optimally!")

def show_data_center_monitoring(data):
    """Display comprehensive data center monitoring and server performance"""
    
    st.title("🖥️ Data Center Monitoring")
    st.markdown("*Real-time server performance, CU optimization, and SysAdmin task management*")
    st.markdown("---")
    
    # Get data center analysis
    dc_analysis = analyze_data_center_performance(data)
    
    # Overview metrics
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cu_usage = dc_analysis['cu_analysis']['current_cu']
        max_cu = dc_analysis['cu_analysis']['max_cu']
        st.metric("CU Usage", f"{cu_usage:,}", f"/ {max_cu:,} max")
    
    with col2:
        utilization = dc_analysis['cu_analysis']['utilization_rate']
        status = dc_analysis['cu_analysis']['status']
        color = {"OPTIMAL": "🟢", "GOOD": "🔵", "WARNING": "🟡", "CRITICAL": "🔴"}
        st.metric("Server Utilization", f"{utilization:.1f}%", f"{color.get(status, '⚪')} {status}")
    
    with col3:
        efficiency = dc_analysis['cu_analysis']['efficiency_score']
        st.metric("System Efficiency", f"{efficiency:.0f}%")
    
    with col4:
        health_score = dc_analysis['hardware_status']['health_score']
        health_status = dc_analysis['hardware_status']['health_status']
        st.metric("Hardware Health", f"{health_score}%", health_status)
    
    # Performance alerts
    if dc_analysis['performance_alerts']:
        st.header("🚨 Performance Alerts")
        
        for alert in dc_analysis['performance_alerts']:
            if alert['level'] == 'CRITICAL':
                st.error(f"🔴 **CRITICAL**: {alert['message']}")
                st.markdown(f"   📋 {alert['details']}")
                st.markdown(f"   🎯 **Action Required**: {alert['recommended_action']}")
            elif alert['level'] == 'WARNING':
                st.warning(f"🟡 **WARNING**: {alert['message']}")
                st.markdown(f"   📋 {alert['details']}")
                st.markdown(f"   💡 **Recommendation**: {alert['recommended_action']}")
    else:
        st.success("✅ No performance alerts - all systems operating normally")
    
    # CU Analysis Section
    st.header("⚡ Compute Unit (CU) Analysis")
    
    cu_data = dc_analysis['cu_analysis']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 CU Utilization")
        
        # Create a gauge chart for CU usage
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = cu_data['utilization_rate'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CU Utilization %"},
            delta = {'reference': 75},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "yellow"},
                    {'range': [75, 90], 'color': "orange"},
                    {'range': [90, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💡 CU Recommendations")
        
        if cu_data['recommended_actions']:
            for rec in cu_data['recommended_actions']:
                if rec['priority'] == 'URGENT':
                    st.error(f"🚨 **{rec['priority']}**: {rec['action']}")
                elif rec['priority'] == 'HIGH':
                    st.warning(f"⚡ **{rec['priority']}**: {rec['action']}")
                else:
                    st.info(f"💡 **{rec['priority']}**: {rec['action']}")
                
                st.markdown(f"   📝 *{rec['reason']}*")
                st.markdown(f"   🏷️ Task Type: {rec['task_type']}")
        else:
            st.success("✅ CU utilization is optimal - no immediate actions needed")
    
    # Hardware Status Section
    st.header("🔧 Hardware Status")
    
    hardware_data = dc_analysis['hardware_status']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Component Inventory")
        
        if hardware_data['component_inventory']:
            inventory_df = pd.DataFrame([
                {'Component Type': comp_type, 'Quantity': quantity}
                for comp_type, quantity in hardware_data['component_inventory'].items()
            ])
            
            fig = px.bar(inventory_df, x='Component Type', y='Quantity', 
                        title='Hardware Component Inventory')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hardware components detected in inventory")
    
    with col2:
        st.subheader("⚠️ Hardware Issues")
        
        if hardware_data['health_issues']:
            for issue in hardware_data['health_issues']:
                if issue['severity'] == 'HIGH':
                    st.error(f"🔴 **{issue['type']}**: {issue['component']}")
                else:
                    st.warning(f"🟡 **{issue['type']}**: {issue['component']}")
                
                st.markdown(f"   📊 Current: {issue['current']} | Required: {issue['required']}")
        else:
            st.success("✅ All hardware components are adequately stocked")
    
    # SysAdmin Tasks Section
    st.header("👨‍💻 SysAdmin Tasks")
    
    sysadmin_tasks = dc_analysis['sysadmin_tasks']
    
    if sysadmin_tasks:
        # Categorize tasks by priority
        high_priority = [task for task in sysadmin_tasks if task['priority'] == 'HIGH']
        medium_priority = [task for task in sysadmin_tasks if task['priority'] == 'MEDIUM'] 
        low_priority = [task for task in sysadmin_tasks if task['priority'] == 'LOW']
        
        if high_priority:
            st.subheader("🚨 High Priority Tasks")
            for task in high_priority:
                with st.expander(f"🔥 {task['task_type']}", expanded=True):
                    st.markdown(f"**Description:** {task['description']}")
                    st.markdown(f"**Estimated Time:** {task['estimated_time']}")
                    st.markdown(f"**Expected Outcome:** {task['expected_outcome']}")
                    
                    if task['components_needed']:
                        st.markdown("**Components Needed:**")
                        for component in task['components_needed']:
                            st.markdown(f"   • {component}")
        
        if medium_priority:
            st.subheader("⚡ Medium Priority Tasks")
            for task in medium_priority:
                with st.expander(f"🔧 {task['task_type']}", expanded=False):
                    st.markdown(f"**Description:** {task['description']}")
                    st.markdown(f"**Estimated Time:** {task['estimated_time']}")
                    st.markdown(f"**Expected Outcome:** {task['expected_outcome']}")
                    
                    if task['components_needed']:
                        st.markdown("**Components Needed:**")
                        for component in task['components_needed']:
                            st.markdown(f"   • {component}")
        
        if low_priority:
            st.subheader("🔄 Low Priority Tasks")
            for task in low_priority:
                with st.expander(f"🛠️ {task['task_type']}", expanded=False):
                    st.markdown(f"**Description:** {task['description']}")
                    st.markdown(f"**Estimated Time:** {task['estimated_time']}")
                    st.markdown(f"**Expected Outcome:** {task['expected_outcome']}")
    else:
        st.info("No SysAdmin tasks identified - system is running optimally")
    
    # Optimization Opportunities
    st.header("🚀 Optimization Opportunities")
    
    opportunities = dc_analysis['optimization_opportunities']
    
    if opportunities:
        for opp in opportunities:
            with st.expander(f"💡 {opp['opportunity']} ({opp['category']})", expanded=False):
                st.markdown(f"**Description:** {opp['description']}")
                st.markdown(f"**Expected Benefit:** {opp['expected_benefit']}")
                st.markdown(f"**Implementation:** {opp['implementation']}")
    else:
        st.success("✅ System is optimally configured - no immediate optimization opportunities identified")
    
    # Cost Analysis (if applicable)
    if 'team_members' in data:
        st.header("💰 Cost Analysis")
        
        from utilities.data_center_monitoring import calculate_server_cost_analysis
        cost_analysis = calculate_server_cost_analysis(dc_analysis['server_metrics'], data)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Monthly Cost", f"${cost_analysis['current_monthly_cost']:,.0f}")
        
        with col2:
            potential_savings = cost_analysis['potential_monthly_savings']
            st.metric("Potential Monthly Savings", f"${potential_savings:,.0f}")
        
        with col3:
            roi = cost_analysis['optimization_roi']['roi_percentage']
            st.metric("Optimization ROI", f"{roi:.1f}%")
        
        if potential_savings > 0:
            st.info(f"💡 **SysAdmin ROI**: Hiring a SysAdmin could save ${potential_savings*12:,.0f} annually")
    
    # Real-time status footer
    st.markdown("---")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"*Last updated: {current_time} | Data Center Monitoring System v1.0*")

def show_static_evaluation(data):
    """Display static evaluation engine results with data-driven insights"""
    
    st.title("🎯 Static Evaluation Engine")
    st.markdown("*Quantitative threshold analysis and actionable game commands*")
    st.markdown("---")
    
    # Run static evaluation
    evaluation_result = run_static_evaluation(data)
    
    # Overview metrics
    st.header("📊 Evaluation Summary")
    
    summary = evaluation_result['evaluation_summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Metrics Calculated", summary['total_metrics_calculated'])
    
    with col2:
        st.metric("Threshold Alerts", summary['total_threshold_alerts'])
    
    with col3:
        st.metric("Critical Actions", summary['critical_actions_required'])
    
    with col4:
        status_color = "🔴" if summary['evaluation_status'] == 'CRITICAL' else "🟢"
        st.metric("System Status", f"{status_color} {summary['evaluation_status']}")
    
    # Calculated Metrics Section
    st.header("🔢 Calculated Metrics")
    st.markdown("*Raw data converted to quantitative business metrics*")
    
    metrics = evaluation_result['calculated_metrics']
    
    # Production Metrics
    with st.expander("⚙️ Production Metrics", expanded=True):
        prod_metrics = metrics['production_rates']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ui_rate = prod_metrics['ui_component_rate']
            st.metric("UI Component Rate", f"{ui_rate:.3f} /hour")
        
        with col2:
            total_components = prod_metrics['total_components']
            st.metric("Total Components", total_components)
        
        with col3:
            dev_productivity = prod_metrics['developer_productivity']
            st.metric("Developer Productivity", f"{dev_productivity:.3f}")
    
    # Team Utilization
    with st.expander("👥 Team Utilization", expanded=True):
        util_metrics = metrics['team_utilization']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            overall_util = util_metrics['overall_utilization']
            st.metric("Overall Utilization", f"{overall_util:.1f}%")
        
        with col2:
            total_employees = util_metrics['total_employees']
            st.metric("Total Employees", total_employees)
        
        with col3:
            assigned_employees = util_metrics['assigned_employees']
            st.metric("Assigned Employees", assigned_employees)
        
        # Role breakdown
        if util_metrics['by_role']:
            st.markdown("**Utilization by Role:**")
            for role, role_data in util_metrics['by_role'].items():
                utilization = role_data['utilization_percent']
                st.write(f"• **{role}**: {utilization:.1f}% ({role_data['assigned']}/{role_data['total']})")
    
    # Financial Runway
    with st.expander("💰 Financial Analysis", expanded=True):
        financial_metrics = metrics['financial_runway']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_cash = financial_metrics['current_cash']
            st.metric("Current Cash", f"${current_cash:,}")
        
        with col2:
            runway_days = financial_metrics['runway_days']
            if runway_days == float('inf'):
                st.metric("Runway", "∞ days")
            else:
                st.metric("Runway", f"{runway_days:.1f} days")
        
        with col3:
            monthly_burn = financial_metrics['monthly_burn_rate']
            st.metric("Monthly Burn", f"${monthly_burn:,}")
    
    # Threshold Analysis Section
    st.header("⚠️ Threshold Analysis")
    st.markdown("*Automated detection of metrics breaching defined thresholds*")
    
    threshold_analysis = evaluation_result['threshold_analysis']
    
    total_alerts = sum(len(alerts) for alerts in threshold_analysis.values())
    
    if total_alerts > 0:
        for category, alerts in threshold_analysis.items():
            if alerts:
                category_name = category.replace('_', ' ').title()
                st.subheader(f"📊 {category_name}")
                
                for alert in alerts:
                    severity_colors = {
                        'CRITICAL': '🔴',
                        'HIGH': '🟡',
                        'MEDIUM': '🔵',
                        'LOW': '🟢'
                    }
                    
                    severity_icon = severity_colors.get(alert['severity'], '⚪')
                    
                    with st.expander(f"{severity_icon} {alert['metric']} - {alert['severity']}", expanded=alert['severity'] in ['CRITICAL', 'HIGH']):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Current Value**: {alert['current_value']}")
                            st.markdown(f"**Threshold**: {alert['threshold']}")
                            st.markdown(f"**Status**: {alert['status']}")
                        
                        with col2:
                            st.markdown(f"**Trigger Condition**: {alert['trigger_condition']}")
                            st.markdown(f"**Severity Level**: {alert['severity']}")
    else:
        st.success("✅ All metrics within acceptable thresholds")
    
    # Actionable Outputs Section
    st.header("🎮 Actionable Game Commands")
    st.markdown("*Specific in-game actions generated from threshold analysis*")
    
    actionable_outputs = evaluation_result['actionable_outputs']
    
    if actionable_outputs:
        # Group by priority
        critical_actions = [a for a in actionable_outputs if a['priority'] == 'CRITICAL']
        high_actions = [a for a in actionable_outputs if a['priority'] == 'HIGH']
        medium_actions = [a for a in actionable_outputs if a['priority'] == 'MEDIUM']
        low_actions = [a for a in actionable_outputs if a['priority'] == 'LOW']
        
        if critical_actions:
            st.subheader("🚨 Critical Actions")
            for action in critical_actions:
                with st.expander(f"🔴 {action['game_command']}", expanded=True):
                    display_action_details(action)
        
        if high_actions:
            st.subheader("🟡 High Priority Actions")
            for action in high_actions:
                with st.expander(f"🟡 {action['game_command']}", expanded=True):
                    display_action_details(action)
        
        if medium_actions:
            st.subheader("🔵 Medium Priority Actions")
            for action in medium_actions:
                with st.expander(f"🔵 {action['game_command']}", expanded=False):
                    display_action_details(action)
        
        if low_actions:
            st.subheader("🟢 Low Priority Actions")
            for action in low_actions:
                with st.expander(f"🟢 {action['game_command']}", expanded=False):
                    display_action_details(action)
    else:
        st.success("✅ No immediate actions required - all systems optimal")
    
    # Data Pipeline Info
    st.header("🔄 Data Pipeline Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Input Data**")
        st.markdown(f"• Timestamp: {evaluation_result['input_data_timestamp']}")
        st.markdown(f"• Raw data fields processed: {len(data)}")
        
    with col2:
        st.markdown("**Processing Results**")
        st.markdown(f"• Metrics calculated: {summary['total_metrics_calculated']}")
        st.markdown(f"• Alerts generated: {summary['total_threshold_alerts']}")
        st.markdown(f"• Actions created: {len(actionable_outputs)}")
    
    # Next Evaluation Timing
    next_eval = summary['next_evaluation_recommended']
    if next_eval == 'IMMEDIATE':
        st.error("⚡ **Next Evaluation**: IMMEDIATE - Critical issues detected")
    elif next_eval == 'HOURLY':
        st.info("🕐 **Next Evaluation**: Hourly monitoring recommended")
    else:
        st.success("✅ **Next Evaluation**: Standard schedule")

def display_action_details(action):
    """Display detailed information about a specific action"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Action Type**: {action['action_type']}")
        st.markdown(f"**Specific Action**: {action['specific_action']}")
        st.markdown(f"**Target Metric**: {action['target_metric']}")
        
    with col2:
        st.markdown(f"**Current Value**: {action['current_value']}")
        st.markdown(f"**Target Value**: {action['target_value']}")
        st.markdown(f"**Priority**: {action['priority']}")
    
    # Implementation details
    if 'implementation' in action:
        st.markdown("**Implementation Steps**:")
        impl = action['implementation']
        
        for key, value in impl.items():
            if key.startswith('step_'):
                step_num = key.replace('step_', '')
                st.markdown(f"   {step_num}. {value}")
            elif key == 'expected_result':
                st.markdown(f"**Expected Result**: {value}")
    
    # Show game command prominently
    st.code(action['game_command'], language='text')

if __name__ == "__main__":
    main()
