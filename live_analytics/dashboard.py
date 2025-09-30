import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    
    st.divider()
    
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
        
        # Inactive features
        inactive_features = [f for f in feature_analysis['feature_details'] if not f['activated']]
        if inactive_features:
            recommendations.append({
                'priority': 'Low',
                'action': f"Activate {inactive_features[0]['name']}",
                'reason': f"Feature ready but not active ({inactive_features[0]['completion_ratio']:.1f}% complete)",
                'impact': 'User Value & Revenue'
            })
        
        if recommendations:
            for i, rec in enumerate(recommendations):
                priority_color = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}[rec['priority']]
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
