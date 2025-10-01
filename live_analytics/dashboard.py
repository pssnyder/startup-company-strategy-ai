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
    page_title="Momentum AI - Phoenix Dashboard",
    page_icon="🚀",
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

# --- Page Navigation ---
def main():
    st.sidebar.title("🚀 Phoenix Dashboard")
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
    tab1, tab2, tab3 = st.tabs(["🌲 Dependency Tree", "📊 Tier Analysis", "⚙️ Production Flow"])
    
    with tab1:
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
                        title='Development Dependency Tree<br><sub>Green=Tier 1 (No deps), Yellow=Tier 2, Orange=Tier 3, Red=Tier 4</sub>',
                        titlefont_size=16,
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
    
    with tab2:
        st.subheader("Tier Distribution Analysis")
        
        # Analyze tier distribution
        tier_data = {}
        for node in dependency_graph.nodes():
            tier = dependency_graph.nodes[node].get('tier', 1)
            node_type = dependency_graph.nodes[node].get('type', 'Unknown')
            
            if tier not in tier_data:
                tier_data[tier] = {'Components': 0, 'Modules': 0, 'UI': 0, 'System': 0, 'items': []}
            
            tier_data[tier][node_type] += 1
            tier_data[tier]['items'].append(node)
        
        # Display tier breakdown
        for tier in sorted(tier_data.keys()):
            tier_info = tier_data[tier]
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.metric(f"**Tier {tier}**", f"{sum(tier_info[k] for k in ['Components', 'Modules', 'UI', 'System'])}")
                st.write(f"Components: {tier_info['Components']}")
                st.write(f"Modules: {tier_info['Modules']}")
                st.write(f"UI Elements: {tier_info['UI']}")
                st.write(f"System: {tier_info['System']}")
            
            with col2:
                st.write(f"**Tier {tier} Items:**")
                items_per_row = 4
                items = tier_info['items']
                for i in range(0, len(items), items_per_row):
                    row_items = items[i:i+items_per_row]
                    st.write(" • ".join(row_items))
    
    with tab3:
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
