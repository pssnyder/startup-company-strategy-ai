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


# --- Watchdog Event Handler ---
class SaveFileEventHandler(FileSystemEventHandler):
    """
    An event handler that triggers when a file is modified in the save directory.
    """
    def on_modified(self, event):
        if not event.is_directory:
            # Check if the modified file is one of the ones we're watching
            if event.src_path.endswith(MANUAL_SAVE_NAME) or event.src_path.endswith(AUTOSAVE_NAME):
                # Give the game a moment to finish writing the file
                time.sleep(1) 
                copy_latest_save()

# --- Main Execution ---
if __name__ == "__main__":
    # Ensure the destination directory exists
    DESTINATION_DIR.mkdir(exist_ok=True)

    print("--- Starting Project Phoenix Save Data Utility ---")
    print(f"Watching directory: {SAVE_GAME_DIR}")
    print("Press Ctrl+C to stop.")

    # Perform an initial copy when the script starts
    copy_latest_save()

    # Set up and start the file system observer
    event_handler = SaveFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(SAVE_GAME_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
        print("\n--- Observer stopped. Exiting. ---")
    observer.join()