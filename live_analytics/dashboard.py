import streamlit as st
import json
import pandas as pd
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(
    page_title="Momentum AI - Phoenix Dashboard",
    page_icon="🚀",
    layout="wide"
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

# --- Main Dashboard ---
st.title("🚀 Momentum AI - Phoenix Dashboard")

if data:
    # --- Key Metrics (KPIs) ---
    st.header("Company Vitals")
    
    balance = data.get('balance', 0)
    research_points = data.get('researchPoints', 0)
    total_users = data.get('progress', {}).get('products', {}).get('e89da7f4-539f-5edf-a287-284ffd04821b', {}).get('users', {}).get('total', 0)
    valuation = data.get('progress', {}).get('products', {}).get('e89da7f4-539f-5edf-a287-284ffd04821b', {}).get('stats', {}).get('valuation', 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Balance", f"${balance:,.2f}")
    col2.metric("💡 Research Points", f"{research_points}")
    col3.metric("👥 Total Users", f"{int(total_users):,}")
    col4.metric("🏦 Valuation", f"${valuation:,.2f}")

    st.divider()

    # --- Candidate Analysis ---
    st.header("Recruitment Intelligence")
    st.info("This section will provide detailed analysis of available candidates, including their hidden salary expectations.")
    
    # Placeholder for candidate data
    if 'candidates' in data and data['candidates']:
        st.write(f"Found {len(data['candidates'])} candidates to analyze.")
    else:
        st.write("No candidates available for recruitment.")

else:
    st.warning("Could not load game data. The dashboard cannot be displayed.")

st.sidebar.success("Select a dashboard view above.")
