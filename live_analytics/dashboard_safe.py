"""
Safe version of dashboard.py - minimal version to test without loops
"""

import streamlit as st
import json
import os
from pathlib import Path
import time

# Configure page
st.set_page_config(
    page_title="Startup Company Analytics - Safe Mode",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_safe_data():
    """Load data without live sync to avoid loops"""
    try:
        # Try to load from local backup first
        save_data_dir = Path(__file__).parent / "save_data"
        main_file = save_data_dir / "sg_momentum ai.json"
        
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.title("🏢 Startup Company Analytics - Safe Mode")
    st.info("🔧 Running in safe mode to diagnose dashboard issues")
    
    # Simple sidebar
    st.sidebar.header("Safe Mode Dashboard")
    st.sidebar.info("This version disables live sync and complex features to isolate issues")
    
    # Load data safely
    data = load_safe_data()
    
    if data is None:
        st.warning("No game save data found. Please ensure save files are in the save_data directory.")
        st.stop()
    
    # Basic company info
    st.header("📊 Company Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Company Name", 
            data.get('CompanyName', 'Unknown')
        )
    
    with col2:
        st.metric(
            "Cash", 
            f"${data.get('Money', 0):,.0f}"
        )
    
    with col3:
        st.metric(
            "Users", 
            f"{data.get('Users', 0):,.0f}"
        )
    
    # Basic features list
    st.header("🎯 Features")
    features = data.get('Features', [])
    st.write(f"Total Features: {len(features)}")
    
    if features:
        # Show first 10 features as example
        st.subheader("Sample Features")
        for i, feature in enumerate(features[:10]):
            if isinstance(feature, dict):
                name = feature.get('Name', f'Feature {i+1}')
                dev_progress = feature.get('DevProgress', 0)
                st.write(f"• {name} - Progress: {dev_progress:.1%}")
    
    # Basic employee info  
    employees = data.get('Employees', [])
    st.header("👥 Team")
    st.write(f"Total Employees: {len(employees)}")
    
    # Debug info
    st.header("🔍 Debug Information")
    st.write("Data keys available:", list(data.keys()))
    st.write("Dashboard running without errors - safe mode working")
    
    # Simple refresh button (manual only)
    if st.button("🔄 Manual Refresh"):
        st.rerun()

if __name__ == "__main__":
    main()