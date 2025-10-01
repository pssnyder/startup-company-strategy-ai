# Real-Time Dashboard Integration Guide

## Quick Integration Steps

To add real-time auto-refresh to your existing Streamlit dashboard, follow these steps:

### 1. Import the refresh utility

Add this import to the top of your `live_analytics/dashboard.py`:

```python
from utilities.dashboard_refresh import add_live_status_to_sidebar, get_dashboard_status, should_refresh_dashboard
```

### 2. Add auto-refresh logic

Add this code near the top of your dashboard, after the page config:

```python
# --- Auto-Refresh Logic ---
def check_for_updates():
    """Check for new save data and auto-refresh if needed."""
    # Get stored update count from session state
    if 'last_update_count' not in st.session_state:
        st.session_state.last_update_count = 0
    
    # Check if we should refresh
    if should_refresh_dashboard(st.session_state.last_update_count):
        status = get_dashboard_status()
        st.session_state.last_update_count = status['update_count']
        st.cache_data.clear()  # Clear cached data
        st.rerun()  # Trigger dashboard refresh

# Run the check
check_for_updates()
```

### 3. Add live status to sidebar

Add this after your sidebar configuration:

```python
# Add live update status to sidebar
add_live_status_to_sidebar()
```

### 4. Update your data loading function

Modify your `load_data()` function to include update tracking:

```python
@st.cache_data
def load_data():
    """Loads the save game data from the local JSON file."""
    save_file_path = Path(__file__).parent / "save_data" / "sg_momentum ai.json"
    try:
        with open(save_file_path, 'r') as f:
            data = json.load(f)
        
        # Add update info to the data
        from utilities.dashboard_refresh import get_dashboard_status
        status = get_dashboard_status()
        data['_dashboard_meta'] = status
        
        return data
    except FileNotFoundError:
        st.error(f"Error: The save file was not found at {save_file_path}. Please ensure the file exists.")
        return None
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode the JSON from {save_file_path}. The file might be corrupted.")
        return None
```

## Usage Instructions

### Starting the Real-Time Monitor

1. Open a terminal in the project directory
2. Run: `python live_analytics/utilities/update_save_data.py`
3. The monitor will:
   - Detect existing save files and copy them initially
   - Watch for file changes in real-time
   - Create trigger files for dashboard updates
   - Show detailed logging of all operations

### Starting the Dashboard

1. Open another terminal
2. Run: `streamlit run live_analytics/dashboard.py`
3. The dashboard will now:
   - Show live update status in the sidebar
   - Auto-refresh when new data is available
   - Display update timestamps and counts

### Testing the Integration

1. Start both the monitor and dashboard
2. Play the game and save (manual save or wait for autosave)
3. Watch the monitor console for copy notifications
4. Check the dashboard sidebar for live status updates
5. The dashboard should automatically refresh with new data

## Troubleshooting

### Monitor Not Detecting Updates
- Ensure the save file path is correct in `update_save_data.py`
- Check that the game is actually writing to the expected file
- Verify file permissions allow reading the save directory

### Dashboard Not Auto-Refreshing
- Check that the trigger file exists in `save_data/.update_trigger`
- Verify the dashboard refresh utility can read the trigger file
- Make sure you've added the auto-refresh code to your dashboard

### File Permission Issues
- Run the monitor as administrator if needed
- Ensure the destination directory is writable
- Check that the game isn't locking save files during writes

## Advanced Configuration

### Changing Update Intervals
Modify the debounce time in `SaveFileHandler.__init__()`:
```python
self.debounce_seconds = 2  # Increase for less frequent updates
```

### Custom Dashboard Refresh Logic
You can implement custom refresh behavior by using the utility functions directly:
```python
from utilities.dashboard_refresh import get_update_count, get_last_update_time

# Your custom logic here
current_count = get_update_count()
last_update = get_last_update_time()
```

### Multiple Save File Monitoring
To monitor multiple save files, modify the `TARGET_SAVE_FILE` configuration or extend the handler to watch multiple files.