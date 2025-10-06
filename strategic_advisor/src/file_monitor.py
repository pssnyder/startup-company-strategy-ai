"""
Strategic Advisor - File Monitor
Watches for game save updates and copies with timestamps
"""

import os
import shutil
import time
import json
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Configure logging
log_dir = Path("strategic_advisor/logs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'file_monitor.log'),
        logging.StreamHandler()
    ]
)
from .logger_config import setup_logging, SUCCESS_MESSAGES

# Setup safe logging
setup_logging()
logger = logging.getLogger(__name__)

class GameSaveMonitor(FileSystemEventHandler):
    """Monitor game save files and copy latest version with timestamp"""
    
    def __init__(self, source_dir: str, target_dir: str, company_name: str = "momentum ai"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.company_name = company_name
        
        # File patterns to watch
        self.main_file = f"sg_{company_name}.json"
        self.autosave_file = f"sg_{company_name}_autosave.json"
        
        # Ensure target directory exists
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Track last processed timestamps
        self.last_main_timestamp = 0
        self.last_autosave_timestamp = 0
        
        logger.info("Monitoring initialized:")
        logger.info(f"   Source: {self.source_dir}")
        logger.info(f"   Target: {self.target_dir}")
        logger.info(f"   Company: {company_name}")
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(str(event.src_path))
        filename = file_path.name
        
        # Check if it's one of our target files
        if filename in [self.main_file, self.autosave_file]:
            self._process_save_file(file_path)
    
    def _process_save_file(self, file_path: Path):
        """Process a save file change"""
        try:
            # Get current modification time
            current_timestamp = file_path.stat().st_mtime
            filename = file_path.name
            
            # Determine which file type and check if it's newer
            is_newer = False
            if filename == self.main_file:
                if current_timestamp > self.last_main_timestamp:
                    self.last_main_timestamp = current_timestamp
                    is_newer = True
            elif filename == self.autosave_file:
                if current_timestamp > self.last_autosave_timestamp:
                    self.last_autosave_timestamp = current_timestamp
                    is_newer = True
            
            if not is_newer:
                return
            
            # Determine which file is actually newest overall
            main_path = self.source_dir / self.main_file
            autosave_path = self.source_dir / self.autosave_file
            
            latest_file = self._get_latest_file(main_path, autosave_path)
            if latest_file != file_path:
                logger.debug(f"⏭️ Skipping {filename} - not the latest file")
                return
            
            # Copy the latest file with timestamp
            self._copy_with_timestamp(latest_file)
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {str(e)}")
    
    def _get_latest_file(self, main_path: Path, autosave_path: Path) -> Path:
        """Determine which file is most recent"""
        main_time = 0
        autosave_time = 0
        
        if main_path.exists():
            main_time = main_path.stat().st_mtime
        if autosave_path.exists():
            autosave_time = autosave_path.stat().st_mtime
        
        # Return the file with the most recent modification time
        if main_time >= autosave_time:
            return main_path
        else:
            return autosave_path
    
    def _copy_with_timestamp(self, source_file: Path):
        """Copy file to target directory with timestamp"""
        try:
            # Add small delay to ensure file write is complete
            time.sleep(0.5)
            
            # Load and validate JSON
            with open(source_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Get game date/time for filename
            game_date = save_data.get('date', 'unknown')
            current_time = datetime.now()
            
            # Create timestamped filename: YYYYMMDD_HHMM_sg_momentum ai.json
            timestamp_str = current_time.strftime("%Y%m%d_%H%M")
            target_filename = f"{timestamp_str}_sg_{self.company_name}.json"
            target_path = self.target_dir / target_filename
            
            # Copy file
            shutil.copy2(source_file, target_path)
            
            # Log successful copy with key metrics
            file_size = target_path.stat().st_size
            balance = save_data.get('balance', 0)
            employees = len(save_data.get('employeesOrder', []))
            
            logger.info(f"✅ Copied save file: {target_filename}")
            logger.info(f"   📊 Game Date: {game_date}")
            logger.info(f"   💰 Balance: ${balance:,}")
            logger.info(f"   👥 Employees: {employees}")
            logger.info(f"   📦 Size: {file_size:,} bytes")
            
            return target_path
            
        except Exception as e:
            logger.error(f"❌ Error copying file: {str(e)}")
            return None
    
    def manual_sync(self):
        """Manually check and sync latest file"""
        logger.info("🔄 Manual sync triggered")
        
        main_path = self.source_dir / self.main_file
        autosave_path = self.source_dir / self.autosave_file
        
        latest_file = self._get_latest_file(main_path, autosave_path)
        
        if latest_file.exists():
            result = self._copy_with_timestamp(latest_file)
            if result:
                logger.info(f"✅ Manual sync completed: {result.name}")
            else:
                logger.error("❌ Manual sync failed")
        else:
            logger.warning("⚠️ No save files found for manual sync")


def start_monitoring(source_dir: str, target_dir: str, company_name: str = "momentum ai"):
    """Start the file monitoring system"""
    
    # Ensure log directory exists
    Path("strategic_advisor/logs").mkdir(parents=True, exist_ok=True)
    
    monitor = GameSaveMonitor(source_dir, target_dir, company_name)
    
    # Perform initial manual sync
    monitor.manual_sync()
    
    # Start watching for file changes
    observer = Observer()
    observer.schedule(monitor, source_dir, recursive=False)
    observer.start()
    
    logger.info("🎯 File monitoring started - Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 File monitoring stopped")
    
    observer.join()


if __name__ == "__main__":
    # Configuration
    SOURCE_DIR = r"C:\Users\patss\Saved Games\Startup Company\testing_v1"
    TARGET_DIR = r"S:\Maker Stuff\Programming\Gaming Projects\startup-company-strategy-ai\strategic_advisor\save_files"
    COMPANY_NAME = "momentum ai"
    
    start_monitoring(SOURCE_DIR, TARGET_DIR, COMPANY_NAME)