import time
import os
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Configuration ---
# The directory where the game saves files
SAVE_GAME_DIR = Path("C:/Users/patss/Saved Games/Startup Company/testing_v1")

# The specific save files we are interested in
MANUAL_SAVE_NAME = "sg_momentum ai.json"
AUTOSAVE_NAME = "sg_momentum ai_autosave.json"

# The local directory where we will store the data for our dashboard
DESTINATION_DIR = Path(__file__).parent.parent / "save_data"
DESTINATION_FILE_NAME = "sg_momentum ai.json"

# --- File Handling Logic ---
def get_latest_save_file():
    """
    Checks which of the two save files (manual or auto) is newer and returns its path.
    """
    manual_save_path = SAVE_GAME_DIR / MANUAL_SAVE_NAME
    autosave_path = SAVE_GAME_DIR / AUTOSAVE_NAME

    try:
        manual_time = manual_save_path.stat().st_mtime
    except FileNotFoundError:
        manual_time = 0

    try:
        autosave_time = autosave_path.stat().st_mtime
    except FileNotFoundError:
        autosave_time = 0

    if manual_time > autosave_time:
        return manual_save_path
    elif autosave_time > 0:
        return autosave_path
    else:
        return None

def copy_latest_save():
    """
    Copies the most recent save file to the local analytics directory.
    """
    latest_file = get_latest_save_file()
    if latest_file:
        destination_path = DESTINATION_DIR / DESTINATION_FILE_NAME
        print(f"[{time.ctime()}] Detected new save. Copying '{latest_file.name}' to '{destination_path}'...")
        shutil.copy(latest_file, destination_path)
        print(f"[{time.ctime()}] Copy complete.")
    else:
        print(f"[{time.ctime()}] No save files found to copy.")


# --- Main Execution ---
if __name__ == "__main__":
    # Ensure the destination directory exists
    DESTINATION_DIR.mkdir(exist_ok=True)

    print("--- Starting Project Phoenix Save Data Utility (Polling Mode) ---")
    print(f"Watching directory: {SAVE_GAME_DIR}")
    print(f"Checking for updates every 30 seconds. Press Ctrl+C to stop.")

    last_known_mod_time = 0

    try:
        while True:
            latest_file = get_latest_save_file()
            
            if latest_file:
                try:
                    current_mod_time = latest_file.stat().st_mtime
                    
                    # Check if the file has been modified since our last check
                    if current_mod_time > last_known_mod_time:
                        print(f"[{time.ctime()}] Detected new save file '{latest_file.name}'.")
                        
                        # Give the game a moment to finish writing to prevent copy errors
                        time.sleep(1) 
                        
                        destination_path = DESTINATION_DIR / DESTINATION_FILE_NAME
                        shutil.copy(latest_file, destination_path)
                        
                        last_known_mod_time = current_mod_time
                        print(f"[{time.ctime()}] Copy complete. New timestamp: {last_known_mod_time}")
                        
                except FileNotFoundError:
                    # This can happen in rare cases if the file is deleted right after being checked
                    print(f"[{time.ctime()}] Warning: Could not stat file {latest_file.name}, it may have been deleted.")
                    pass
                except Exception as e:
                    print(f"[{time.ctime()}] An error occurred: {e}")

            # Wait for 30 seconds before the next check
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n--- Polling stopped. Exiting. ---")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")