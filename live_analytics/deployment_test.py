"""
Deployment Verification Script for Streamlit.app
This script helps verify that the fallback system works in production
"""

import streamlit as st
import json
from pathlib import Path
from utilities.live_file_sync import load_game_data, LOCAL_SAVE_PATH, GAME_SAVE_PATH

st.title("🔧 Deployment Verification Test")
st.markdown("**Testing fallback system for Streamlit.app deployment**")

# Environment info
st.header("🌍 Environment Information")
col1, col2 = st.columns(2)

with col1:
    st.metric("Current Working Dir", str(Path.cwd().name))
    st.metric("Script Directory", str(Path(__file__).parent.name))
    
with col2:
    st.metric("Game Save Exists", "✅" if GAME_SAVE_PATH.exists() else "❌")
    st.metric("Backup Exists", "✅" if LOCAL_SAVE_PATH.exists() else "❌")

# Path verification
st.header("📁 Path Verification")
st.code(f"""
Game Save Path: {GAME_SAVE_PATH}
Backup Path: {LOCAL_SAVE_PATH.absolute()}
""")

# Data loading test
st.header("📊 Data Loading Test")

if st.button("🧪 Test Data Loading", type="primary"):
    with st.spinner("Testing data loading..."):
        data = load_game_data()
        
        if data:
            st.success("✅ Data loaded successfully!")
            
            # Show key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Balance", f"${data.get('balance', 0):,.2f}")
            with col2:
                st.metric("Research Points", f"{data.get('researchPoints', 0)}")
            with col3:
                st.metric("Features", len(data.get('featureInstances', [])))
            
            # Show data source
            data_source = getattr(st.session_state, 'data_source', 'unknown')
            st.info(f"📡 Data Source: {data_source}")
            
            # Show sample data structure
            st.header("📋 Sample Data Structure")
            sample_data = {
                "date": data.get("date", "N/A"),
                "balance": data.get("balance", 0),
                "researchPoints": data.get("researchPoints", 0),
                "feature_count": len(data.get("featureInstances", [])),
                "employee_count": len(data.get("employees", [])),
                "has_inventory": bool(data.get("inventory", {})),
                "has_transactions": bool(data.get("transactions", []))
            }
            st.json(sample_data)
            
        else:
            st.error("❌ Failed to load data")

# Backup file verification
st.header("🗃️ Backup File Verification")

if LOCAL_SAVE_PATH.exists():
    try:
        with open(LOCAL_SAVE_PATH, 'r') as f:
            backup_data = json.load(f)
        
        st.success(f"✅ Backup file is valid JSON ({LOCAL_SAVE_PATH.stat().st_size:,} bytes)")
        
        # Show backup file stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{LOCAL_SAVE_PATH.stat().st_size:,} bytes")
        with col2:
            st.metric("Features in Backup", len(backup_data.get('featureInstances', [])))
        with col3:
            st.metric("Transactions in Backup", len(backup_data.get('transactions', [])))
            
    except Exception as e:
        st.error(f"❌ Backup file error: {e}")
else:
    st.warning("⚠️ Backup file not found")
    
    # Show file search results
    search_paths = [
        Path("save_data/sg_momentum ai.json"),
        Path("live_analytics/save_data/sg_momentum ai.json"),
        Path("../save_data/sg_momentum ai.json"),
        LOCAL_SAVE_PATH
    ]
    
    st.write("**File search results:**")
    for path in search_paths:
        exists = path.exists()
        st.write(f"• `{path.absolute()}` - {'✅ FOUND' if exists else '❌ NOT FOUND'}")

# Instructions for deployment
st.header("🚀 Deployment Instructions")
st.info("""
**For successful Streamlit.app deployment:**

1. Ensure the `live_analytics/save_data/` directory is included in your repo
2. The backup file `sg_momentum ai.json` should be committed to git
3. The fallback system will automatically use the backup when the live game file isn't available
4. The dashboard will show "📁 Local Backup" as the data source on Streamlit.app

**This allows the portfolio demo to work even without access to the live game files.**
""")