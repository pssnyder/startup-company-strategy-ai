"""
Live File Sync System for Real-Time Game Data
Handles local game save monitoring and auto-refresh functionality
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import streamlit as st
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Game save file path - Use environment variable for flexibility in deployment
import os
GAME_SAVE_PATH = Path(os.environ.get(
    'STARTUP_COMPANY_SAVE_PATH', 
    r"C:\Users\patss\Saved Games\Startup Company\testing_v1\sg_momentum ai.json"
))

# Local save path - resolve relative to this file's directory
_SCRIPT_DIR = Path(__file__).parent
LOCAL_SAVE_PATH = _SCRIPT_DIR.parent / "save_data" / "sg_momentum ai.json"

class GameSaveHandler(FileSystemEventHandler):
    """Handler for game save file changes"""
    
    def __init__(self):
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if str(event.src_path).endswith("sg_momentum ai.json"):
            current_time = time.time()
            # Debounce rapid file changes (game may write multiple times)
            # Increased debounce time to prevent excessive syncing
            if current_time - self.last_modified > 3:
                self.last_modified = current_time
                self.sync_file()
                
    def sync_file(self):
        """Copy game save to local directory and trigger refresh"""
        try:
            if GAME_SAVE_PATH.exists():
                # Ensure local directory exists
                LOCAL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file with validation
                with open(GAME_SAVE_PATH, 'r') as src:
                    data = json.load(src)  # Validate JSON
                
                with open(LOCAL_SAVE_PATH, 'w') as dst:
                    json.dump(data, dst, indent=2)
                
                # Store sync timestamp
                sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open("save_data/last_sync.txt", "w") as f:
                    f.write(sync_time)
                
                # Note: Removed automatic st.rerun() to prevent infinite loops
                # The dashboard will pick up changes on next manual interaction
                    
        except Exception as e:
            print(f"Error syncing game save: {e}")

def is_running_locally():
    """Detect if running locally vs Streamlit Cloud"""
    # Check for local environment indicators
    local_indicators = [
        os.path.exists(GAME_SAVE_PATH),  # Game save file exists
        'STREAMLIT_SHARING' not in os.environ,  # Not on Streamlit Cloud
        'localhost' in os.environ.get('STREAMLIT_SERVER_ADDRESS', ''),
        os.path.exists(r"C:\Users\patss"),  # Local user directory
    ]
    
    return any(local_indicators)

def verify_data_sources():
    """Debug function to check all data source availability"""
    verification = {
        'live_game_file': {
            'path': str(GAME_SAVE_PATH),
            'exists': GAME_SAVE_PATH.exists() if GAME_SAVE_PATH else False,
            'readable': False,
            'size': 0,
            'modified': None
        },
        'local_backup': {
            'path': str(LOCAL_SAVE_PATH),
            'exists': LOCAL_SAVE_PATH.exists(),
            'readable': False,
            'size': 0,
            'modified': None
        },
        'environment': {
            'is_local': is_running_locally(),
            'streamlit_sharing': 'STREAMLIT_SHARING' in os.environ,
            'current_dir': str(Path.cwd())
        }
    }
    
    # Test live game file
    if verification['live_game_file']['exists']:
        try:
            stat = GAME_SAVE_PATH.stat()
            verification['live_game_file']['size'] = stat.st_size
            verification['live_game_file']['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            with open(GAME_SAVE_PATH, 'r') as f:
                json.load(f)  # Test if valid JSON
            verification['live_game_file']['readable'] = True
        except Exception as e:
            verification['live_game_file']['error'] = str(e)
    
    # Test local backup
    if verification['local_backup']['exists']:
        try:
            stat = LOCAL_SAVE_PATH.stat()
            verification['local_backup']['size'] = stat.st_size
            verification['local_backup']['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            with open(LOCAL_SAVE_PATH, 'r') as f:
                json.load(f)  # Test if valid JSON
            verification['local_backup']['readable'] = True
        except Exception as e:
            verification['local_backup']['error'] = str(e)
    
    return verification

def get_data_freshness():
    """Get timestamp of when data was last updated with source indication"""
    freshness_info = {"timestamp": "No data available", "source": "none"}
    
    # Check live game file first (if local)
    if is_running_locally() and GAME_SAVE_PATH.exists():
        try:
            mtime = GAME_SAVE_PATH.stat().st_mtime
            freshness_info = {
                "timestamp": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "live_game_file"
            }
        except Exception:
            pass
    
    # Fallback to local backup
    if freshness_info["source"] == "none" and LOCAL_SAVE_PATH.exists():
        try:
            mtime = LOCAL_SAVE_PATH.stat().st_mtime
            freshness_info = {
                "timestamp": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "source": "local_backup"
            }
        except Exception:
            pass
    
    return freshness_info["timestamp"]

def setup_live_monitoring():
    """Setup live file monitoring for local development"""
    if not is_running_locally():
        return None
        
    if not GAME_SAVE_PATH.exists():
        st.warning(f"Game save file not found: {GAME_SAVE_PATH}")
        return None
    
    # Initial sync
    handler = GameSaveHandler()
    handler.sync_file()
    
    # Setup file watcher
    observer = Observer()
    observer.schedule(handler, str(GAME_SAVE_PATH.parent), recursive=False)
    
    try:
        observer.start()
        return observer
    except Exception as e:
        st.error(f"Could not start file monitoring: {e}")
        return None

def ensure_backup_file_exists():
    """Ensure there's always a backup file available for cloud deployment"""
    if not LOCAL_SAVE_PATH.exists():
        # Create directory if it doesn't exist
        LOCAL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to copy from live game file if available
        if is_running_locally() and GAME_SAVE_PATH.exists():
            try:
                handler = GameSaveHandler()
                handler.sync_file()
                return True
            except Exception as e:
                print(f"Could not sync from live game file: {e}")
        
        # Create a realistic demo data file for cloud deployment
        demo_data = {
            "date": "2025-12-18T16:17:00.681Z",
            "started": "2025-09-29T12:00:00.681Z",
            "gameover": False,
            "state": 1,
            "paused": False,
            "lastVersion": "1.24",
            "balance": 227591.39,
            "researchPoints": 15432,
            "transactions": [
                {
                    "id": "demo-transaction-1",
                    "day": 69,
                    "hour": 0,
                    "minute": 0,
                    "amount": -434,
                    "label": "Loan: Eazy Money",
                    "balance": 79198.39
                },
                {
                    "id": "demo-transaction-2", 
                    "day": 69,
                    "hour": 0,
                    "minute": 0,
                    "amount": 5000,
                    "label": "Software Sales Revenue",
                    "balance": 84198.39
                }
            ],
            "inventory": {
                "UiComponent": 15,
                "BackendComponent": 8,
                "DatabaseComponent": 12,
                "GraphicsComponent": 5,
                "NetworkComponent": 10
            },
            "featureInstances": [
                {
                    "id": "demo-feature-1",
                    "featureName": "User Interface System",
                    "activated": True,
                    "requirements": {
                        "UiComponent": 5,
                        "GraphicsComponent": 3
                    },
                    "quality": {
                        "current": 1200,
                        "max": 2000
                    },
                    "efficiency": {
                        "current": 800,
                        "max": 1500
                    },
                    "pricePerMonth": 50
                }
            ],
            "progress": {
                "products": {
                    "main_product": {
                        "users": {
                            "total": 15420,
                            "satisfaction": 75,
                            "conversionRate": 12.5,
                            "potentialUsers": 50000
                        },
                        "stats": {
                            "quality": 1200,
                            "efficiency": 800,
                            "valuation": 450000,
                            "performance": {
                                "state": "Good"
                            }
                        }
                    }
                }
            },
            "office": {
                "workstations": [
                    {
                        "employee": {
                            "name": "Alice Johnson",
                            "employeeTypeName": "Developer",
                            "level": "Intermediate",
                            "speed": 120,
                            "mood": 85,
                            "queue": [
                                {
                                    "component": {
                                        "name": "PaymentModule",
                                        "type": "Module"
                                    },
                                    "state": "Running",
                                    "totalMinutes": 480,
                                    "completedMinutes": 240
                                }
                            ]
                        }
                    },
                    {
                        "employee": {
                            "name": "Bob Smith", 
                            "employeeTypeName": "Designer",
                            "level": "Expert",
                            "speed": 150,
                            "mood": 90,
                            "queue": []
                        }
                    }
                ]
            },
            "employees": [
                {
                    "name": "Alice Johnson",
                    "employeeTypeName": "Developer", 
                    "level": "Intermediate",
                    "speed": 120,
                    "mood": 85
                },
                {
                    "name": "Bob Smith",
                    "employeeTypeName": "Designer",
                    "level": "Expert", 
                    "speed": 150,
                    "mood": 90
                }
            ],
            "meta": {
                "created_by": "Project Phoenix Dashboard",
                "note": "Demo data for portfolio showcase - live game integration available",
                "data_type": "demo"
            }
        }
        
        try:
            with open(LOCAL_SAVE_PATH, 'w') as f:
                json.dump(demo_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Could not create demo backup file: {e}")
            return False
    
    return True

def load_game_data():
    """Load current game data with robust fallback system for cloud deployment"""
    
    # Ensure backup file exists for cloud deployment
    ensure_backup_file_exists()
    
    data = None
    data_source = "unknown"
    error_details = []
    
    # Priority 1: Read directly from game save file (if exists)
    if GAME_SAVE_PATH.exists():
        try:
            with open(GAME_SAVE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data_source = "live_game_file"
            
        except Exception as e:
            error_details.append(f"Game save file error: {e}")
            data = None
    else:
        error_details.append(f"Game save file not found: {GAME_SAVE_PATH}")
    
    # Priority 2: Fallback to local backup copy
    if data is None:
        # Check if backup file exists and log path for debugging
        backup_exists = LOCAL_SAVE_PATH.exists()
        error_details.append(f"Checking backup at: {LOCAL_SAVE_PATH.absolute()}")
        error_details.append(f"Backup exists: {backup_exists}")
        
        if backup_exists:
            try:
                with open(LOCAL_SAVE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data_source = "local_backup"
                
            except Exception as e:
                error_details.append(f"Backup file error: {e}")
        else:
            error_details.append(f"Backup file not found: {LOCAL_SAVE_PATH}")
    
    # Priority 3: Try alternative backup locations for cloud deployment
    if data is None:
        alternative_paths = [
            Path("save_data/sg_momentum ai.json"),  # Original relative path
            Path("live_analytics/save_data/sg_momentum ai.json"),  # From project root
            Path("../save_data/sg_momentum ai.json"),  # Up one level
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                try:
                    with open(alt_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    data_source = f"alternative_backup_{alt_path}"
                    error_details.append(f"Found backup at: {alt_path.absolute()}")
                    break
                except Exception as e:
                    error_details.append(f"Alternative backup error ({alt_path}): {e}")
            else:
                error_details.append(f"Alternative path not found: {alt_path.absolute()}")
    
    # Set data source info for status display
    if data and hasattr(st, 'session_state'):
        st.session_state.data_source = data_source
        if error_details:
            st.session_state.data_source_debug = error_details
    
    # Handle no data available - show debugging info
    if data is None:
        # Show debugging information in the UI
        st.error("❌ No game data available from any source")
        
        with st.expander("🔧 Debug Information", expanded=True):
            st.write("**Data Source Attempts:**")
            for detail in error_details:
                st.write(f"• {detail}")
            
            st.write("**Current Working Directory:**")
            st.write(f"• {Path.cwd().absolute()}")
            
            st.write("**File Search Locations:**")
            all_paths = [GAME_SAVE_PATH, LOCAL_SAVE_PATH] + [
                Path("save_data/sg_momentum ai.json"),
                Path("live_analytics/save_data/sg_momentum ai.json"),
                Path("../save_data/sg_momentum ai.json"),
            ]
            for path in all_paths:
                exists = path.exists()
                st.write(f"• {path.absolute()} - {'✅ EXISTS' if exists else '❌ NOT FOUND'}")
        
        return None
    
    return data

def get_environment_status():
    """Get current environment and data source status"""
    
    # Get actual data source from session state if available
    if hasattr(st, 'session_state') and hasattr(st.session_state, 'data_source'):
        source_type = st.session_state.data_source
        source_labels = {
            'live_game_file': '🎮 Direct Game File',
            'local_backup': '📁 Local Backup',
            'unknown': '❓ Unknown Source'
        }
        data_source_display = source_labels.get(source_type, f'📊 {source_type}')
    else:
        data_source_display = "Not loaded"
    
    # Get file freshness
    freshness = "Unknown"
    if GAME_SAVE_PATH.exists():
        try:
            mtime = GAME_SAVE_PATH.stat().st_mtime
            freshness = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    elif LOCAL_SAVE_PATH.exists():
        try:
            mtime = LOCAL_SAVE_PATH.stat().st_mtime
            freshness = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    
    status = {
        'environment': 'Direct Game File Access',
        'data_source': data_source_display,
        'data_source_detail': f"Reading from: {GAME_SAVE_PATH}" if GAME_SAVE_PATH.exists() else f"Fallback: {LOCAL_SAVE_PATH}",
        'last_updated': freshness,
        'auto_sync': False,  # No auto-refresh
        'live_file_available': GAME_SAVE_PATH.exists(),
        'backup_available': LOCAL_SAVE_PATH.exists()
    }
    
    return status