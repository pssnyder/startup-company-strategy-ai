"""
Dashboard Auto-Refresh Utility

This module provides utilities for the Streamlit dashboard to detect
when new save data is available and trigger automatic refreshes.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Path to the trigger file created by update_save_data.py
TRIGGER_FILE = Path(__file__).parent.parent / "save_data" / ".update_trigger"


def get_last_update_info() -> Optional[Dict[str, Any]]:
    """
    Get information about the last save file update.
    
    Returns:
        Dict with update info or None if no trigger file exists
    """
    try:
        if TRIGGER_FILE.exists():
            with open(TRIGGER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def get_update_count() -> int:
    """Get the current update count."""
    info = get_last_update_info()
    return info.get("update_count", 0) if info else 0


def get_last_update_time() -> Optional[datetime]:
    """Get the timestamp of the last update."""
    info = get_last_update_info()
    if info and "last_update" in info:
        try:
            return datetime.fromisoformat(info["last_update"])
        except ValueError:
            pass
    return None


def should_refresh_dashboard(last_known_count: int = 0) -> bool:
    """
    Check if the dashboard should refresh based on update count.
    
    Args:
        last_known_count: The last update count the dashboard knew about
        
    Returns:
        True if dashboard should refresh
    """
    current_count = get_update_count()
    return current_count > last_known_count


def format_last_update_display() -> str:
    """
    Format last update time for display in the dashboard.
    
    Returns:
        Formatted string showing last update time
    """
    last_update = get_last_update_time()
    if last_update:
        time_diff = datetime.now() - last_update
        if time_diff.total_seconds() < 60:
            return f"Updated {int(time_diff.total_seconds())} seconds ago"
        elif time_diff.total_seconds() < 3600:
            return f"Updated {int(time_diff.total_seconds() / 60)} minutes ago"
        else:
            return f"Updated {last_update.strftime('%H:%M:%S')}"
    return "No updates detected"


def get_dashboard_status() -> Dict[str, Any]:
    """
    Get comprehensive dashboard status information.
    
    Returns:
        Dict with status info for dashboard display
    """
    info = get_last_update_info()
    last_update = get_last_update_time()
    
    if not info:
        return {
            "status": "waiting",
            "message": "Waiting for first save file update...",
            "update_count": 0,
            "last_update": None,
            "time_display": "No updates yet"
        }
    
    # Calculate time since last update
    time_since_update = None
    if last_update:
        time_since_update = (datetime.now() - last_update).total_seconds()
    
    # Determine status
    if time_since_update and time_since_update < 30:
        status = "active"
        message = "🟢 Live data stream active"
    elif time_since_update and time_since_update < 300:  # 5 minutes
        status = "recent"
        message = "🟡 Recent update available"
    else:
        status = "stale"
        message = "🔴 Data may be stale"
    
    return {
        "status": status,
        "message": message,
        "update_count": info.get("update_count", 0),
        "last_update": last_update,
        "time_display": format_last_update_display(),
        "source_file": info.get("source_file", "Unknown")
    }


# Example usage for Streamlit
def add_live_status_to_sidebar():
    """
    Add live update status to Streamlit sidebar.
    Call this function in your Streamlit dashboard.
    """
    import streamlit as st
    
    status = get_dashboard_status()
    
    st.sidebar.markdown("### 📡 Live Data Status")
    st.sidebar.write(status["message"])
    st.sidebar.write(f"**Updates:** {status['update_count']}")
    st.sidebar.write(f"**Last Update:** {status['time_display']}")
    
    # Auto-refresh button
    if st.sidebar.button("🔄 Force Refresh", help="Manually refresh the dashboard data"):
        st.cache_data.clear()
        st.rerun()
    
    # Auto-refresh logic (check every 30 seconds)
    if status["status"] == "active":
        st.sidebar.success("✅ Real-time monitoring active")
        # You can add auto-refresh logic here if needed
    elif status["status"] == "recent":
        st.sidebar.warning("⏰ New data available")
    else:
        st.sidebar.error("❌ No recent updates")


if __name__ == "__main__":
    # Test the utility functions
    print("🔥 Project Phoenix - Dashboard Refresh Utility Test")
    print("=" * 50)
    
    status = get_dashboard_status()
    print(f"Status: {status['status']}")
    print(f"Message: {status['message']}")
    print(f"Update Count: {status['update_count']}")
    print(f"Time Display: {status['time_display']}")
    
    if status['last_update']:
        print(f"Last Update: {status['last_update'].isoformat()}")
    
    print("\nMonitoring for updates... (Press Ctrl+C to stop)")
    last_count = status['update_count']
    
    try:
        while True:
            time.sleep(5)  # Check every 5 seconds
            if should_refresh_dashboard(last_count):
                new_status = get_dashboard_status()
                print(f"🔄 New update detected! Count: {new_status['update_count']}")
                last_count = new_status['update_count']
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped.")