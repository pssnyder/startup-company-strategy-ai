import time
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Configuration ---
# The directory where the game saves files
SAVE_GAME_DIR = Path("C:/Users/patss/Saved Games/Startup Company/testing_v1")

# The specific save file we are monitoring
TARGET_SAVE_FILE = "sg_momentum ai.json"

# The local directory where we will store the data for our dashboard
DESTINATION_DIR = Path(__file__).parent.parent / "save_data"
DESTINATION_FILE_NAME = "sg_momentum ai.json"

# Trigger file to signal streamlit dashboard updates
TRIGGER_FILE = DESTINATION_DIR / ".update_trigger"


class SaveFileHandler(FileSystemEventHandler):
    """Handles file system events for the target save file."""
    
    def __init__(self):
        self.target_file_path = SAVE_GAME_DIR / TARGET_SAVE_FILE
        self.last_processed_time = 0
        self.debounce_seconds = 2  # Prevent multiple rapid triggers
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        # Check if this is our target file
        event_path = str(event.src_path)
        if Path(event_path).name == TARGET_SAVE_FILE:
            self._handle_save_file_update(event_path)
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
            
        event_path = str(event.src_path)
        if Path(event_path).name == TARGET_SAVE_FILE:
            self._handle_save_file_update(event_path)
    
    def _handle_save_file_update(self, file_path):
        """Process the save file update with debouncing and validation."""
        current_time = time.time()
        
        # Debounce rapid file updates
        if current_time - self.last_processed_time < self.debounce_seconds:
            return
            
        try:
            file_path = Path(file_path)
            
            # Verify the file exists and is readable
            if not file_path.exists():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] File not found: {file_path}")
                return
                
            # Wait a moment for the game to finish writing
            time.sleep(0.5)
            
            # Validate the JSON file is complete and readable
            if not self._validate_json_file(file_path):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Invalid JSON file, skipping: {file_path.name}")
                return
            
            # Copy the file to our analytics directory
            self._copy_save_file(file_path)
            
            # Create trigger file for dashboard updates
            self._create_update_trigger()
            
            self.last_processed_time = current_time
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error processing file update: {e}")
    
    def _validate_json_file(self, file_path):
        """Validate that the file is a complete, readable JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            return False
    
    def _copy_save_file(self, source_path):
        """Copy the save file to the analytics directory."""
        try:
            destination_path = DESTINATION_DIR / DESTINATION_FILE_NAME
            
            # Ensure destination directory exists
            DESTINATION_DIR.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, destination_path)
            
            # Get file size for logging
            file_size = destination_path.stat().st_size
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Save file updated: {source_path.name}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📁 Copied to: {destination_path}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 File size: {file_size:,} bytes")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to copy file: {e}")
    
    def _create_update_trigger(self):
        """Create a trigger file to signal dashboard updates."""
        try:
            # Write timestamp to trigger file
            trigger_data = {
                "last_update": datetime.now().isoformat(),
                "source_file": TARGET_SAVE_FILE,
                "update_count": self._get_update_count() + 1
            }
            
            with open(TRIGGER_FILE, 'w', encoding='utf-8') as f:
                json.dump(trigger_data, f, indent=2)
                
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Dashboard update triggered")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Failed to create update trigger: {e}")
    
    def _get_update_count(self):
        """Get the current update count from trigger file."""
        try:
            if TRIGGER_FILE.exists():
                with open(TRIGGER_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("update_count", 0)
        except:
            pass
        return 0


def perform_initial_copy():
    """Perform initial copy of the save file if it exists."""
    source_file = SAVE_GAME_DIR / TARGET_SAVE_FILE
    
    if source_file.exists():
        handler = SaveFileHandler()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Found existing save file, performing initial copy...")
        handler._handle_save_file_update(source_file)
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Target save file not found: {source_file}")


def main():
    """Main execution function."""
    print("🔥 Project Phoenix - Real-Time Save Data Monitor")
    print("=" * 50)
    print(f"📂 Monitoring: {SAVE_GAME_DIR}")
    print(f"🎯 Target file: {TARGET_SAVE_FILE}")
    print(f"📊 Output directory: {DESTINATION_DIR}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Ensure directories exist
    SAVE_GAME_DIR.mkdir(parents=True, exist_ok=True)
    DESTINATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Perform initial copy if file exists
    perform_initial_copy()
    
    # Set up file system monitoring
    event_handler = SaveFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(SAVE_GAME_DIR), recursive=False)
    
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 👀 Starting file system monitoring...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 Press Ctrl+C to stop")
        print()
        
        observer.start()
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Stopping monitor...")
        observer.stop()
        
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ Unexpected error: {e}")
        observer.stop()
        
    finally:
        observer.join()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 👋 Monitor stopped. Goodbye!")


if __name__ == "__main__":
    main()