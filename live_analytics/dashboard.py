import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="Momentum AI - Project Phoenix",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads the save game data from the local JSON file."""
    save_file_path = Path(__file__).parent / "save_data" / "sg_momentum ai.json"
    try:
        with open(save_file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error(f"Error: The save file was not found at {save_file_path}. Please ensure the file exists.")
        return None
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode the JSON from {save_file_path}. The file might be corrupted.")
        return None

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
                'message': f"Only {market_penetration:.1f}% of potential users acquired. Strong growth opportunity.",
                'action': 'Consider increasing marketing spend or improving conversion rate.'
            })
        elif market_penetration > 50:
            insights.append({
                'type': 'success',
                'title': 'Strong Market Position',
                'message': f"Captured {market_penetration:.1f}% of potential market.",
                'action': 'Focus on retention and monetization strategies.'
            })
    
    # Satisfaction insights
    if analysis['satisfaction'] < 60:
        insights.append({
            'type': 'critical',
            'title': 'User Satisfaction Critical',
            'message': f"Satisfaction at {analysis['satisfaction']}% - users may churn.",
            'action': 'Immediate focus on product quality and performance improvements.'
        })
    elif analysis['satisfaction'] > 80:
        insights.append({
            'type': 'success',
            'title': 'High User Satisfaction',
            'message': f"Excellent satisfaction at {analysis['satisfaction']}%.",
            'action': 'Leverage satisfaction for viral growth and premium features.'
        })
    
    # Quality vs Efficiency balance
    if analysis['quality'] > 0 and analysis['efficiency'] > 0:
        qe_ratio = analysis['quality'] / analysis['efficiency']
        if qe_ratio > 3:
            insights.append({
                'type': 'optimization',
                'title': 'Quality Over-Investment',
                'message': f"Quality ({analysis['quality']}) significantly exceeds efficiency ({analysis['efficiency']}).",
                'action': 'Consider focusing on efficiency improvements for better ROI.'
            })
        elif qe_ratio < 0.5:
            insights.append({
                'type': 'warning',
                'title': 'Efficiency Over Quality',
                'message': f"Efficiency ({analysis['efficiency']}) much higher than quality ({analysis['quality']}).",
                'action': 'Balance with quality improvements to maintain user satisfaction.'
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
    st.sidebar.title("🐦‍🔥 Project Phoenix")
    st.sidebar.markdown("---")
    
    pages = {
        "🏠 Executive Overview": show_executive_overview,
        "📦 Product Management": show_product_management,
        "👥 Human Resources": show_human_resources,
        "🔬 Research & Development": show_research_development
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
    
    # --- Key Metrics ---
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
            
            with st.expander(f"Recommended Action: {insight['title']}"):
                st.write(insight['action'])
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
    
    # --- Development Dependency Tree ---
    st.header("🌳 Development Dependency Tree")
    
    dependency_graph, dependencies = build_dependency_tree(data)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 WSJF Priority", "🌲 Dependency Tree", "📊 Tier Analysis", "⚙️ Production Flow"])
    
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
        st.subheader("Component & Module Dependencies")
        
        # Create interactive dependency visualization
        pos = nx.spring_layout(dependency_graph, k=3, iterations=50)
        
        # Prepare data for plotly
        edge_x = []
        edge_y = []
        for edge in dependency_graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(x=edge_x, y=edge_y,
                               line=dict(width=0.5, color='#888'),
                               hoverinfo='none',
                               mode='lines')
        
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in dependency_graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get node attributes
            tier = dependency_graph.nodes[node].get('tier', 1)
            node_type = dependency_graph.nodes[node].get('type', 'Unknown')
            
            node_text.append(f"{node}<br>Tier {tier}<br>Type: {node_type}")
            
            # Color by tier
            tier_colors = {1: '#90EE90', 2: '#FFD700', 3: '#FFA500', 4: '#FF6347'}
            node_color.append(tier_colors.get(tier, '#808080'))
            
            # Size by dependencies
            deps_count = len(list(dependency_graph.predecessors(node)))
            node_size.append(max(10 + deps_count * 3, 15))
        
        node_trace = go.Scatter(x=node_x, y=node_y,
                               mode='markers+text',
                               hoverinfo='text',
                               text=[node.replace('Component', '').replace('Module', '') for node in dependency_graph.nodes()],
                               hovertext=node_text,
                               textposition="middle center",
                               marker=dict(size=node_size,
                                         color=node_color,
                                         line=dict(width=2, color='black')))
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                        title=dict(
                            text='Development Dependency Tree<br><sub>Green=Tier 1 (No deps), Yellow=Tier 2, Orange=Tier 3, Red=Tier 4</sub>',
                            font=dict(size=16)
                        ),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="Node size indicates dependency count. Click and drag to explore.",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002 ) ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600))
        
        st.plotly_chart(fig, use_container_width=True)
    
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
    
    # Recruitment Intelligence section (moved from main dashboard)
    st.header("🎯 Recruitment Intelligence")
    candidates = data.get("candidates", [])
    if candidates:
        candidate_list = []
        for c in candidates:
            negotiation = c.get("negotiation", {})
            expected_salary = "N/A"
            if negotiation and negotiation.get("completed") is False:
                candidate_offers = [o.get("total") for o in negotiation.get("offers", []) if o.get("fromCandidate")]
                if candidate_offers:
                    expected_salary = candidate_offers[-1]

            candidate_list.append({
                "Name": c.get("name"),
                "Role": c.get("employeeTypeName"),
                "Level": c.get("level"),
                "Speed": c.get("speed"),
                "Current Salary": c.get('salary', 0),
                "Expected Salary": expected_salary
            })
        
        df_candidates = pd.DataFrame(candidate_list)
        st.dataframe(df_candidates, use_container_width=True,
                       column_config={
                           "Current Salary": st.column_config.NumberColumn(format="$%d"),
                           "Expected Salary": st.column_config.NumberColumn(format="$%d"),
                       })
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

if __name__ == "__main__":
    main()
