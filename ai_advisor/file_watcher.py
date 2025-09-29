"""
Real-time file monitoring for Startup Company save files.
Watches autosave files and creates timestamped snapshots for trend analysis.
"""

import os
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Any, Optional
import logging

class SaveFileWatcher(FileSystemEventHandler):
    """Monitors Startup Company save files for changes and logs snapshots."""
    
    def __init__(self, save_directory: str, output_directory: str):
        self.save_directory = Path(save_directory)
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Files to monitor
        self.autosave_file = "sg_rts technology & solutions llc_autosave.json"
        self.main_save_file = "sg_rts technology & solutions llc.json"
        
        # Track last modification times to avoid duplicate processing
        self.last_processed = {}
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_directory / "file_watcher.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = Path(str(event.src_path))
        filename = file_path.name
        
        # Check if this is one of our target files
        if filename in [self.autosave_file, self.main_save_file]:
            self._process_save_file(file_path, filename)
    
    def _process_save_file(self, file_path: Path, filename: str):
        """Process a save file update and create a timestamped snapshot."""
        try:
            # Get file modification time
            mod_time = os.path.getmtime(file_path)
            
            # Skip if we've already processed this modification
            if filename in self.last_processed and self.last_processed[filename] >= mod_time:
                return
                
            self.last_processed[filename] = mod_time
            
            # Wait a moment to ensure file write is complete
            time.sleep(0.5)
            
            # Load and validate JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_type = "autosave" if "autosave" in filename else "manual"
            snapshot_filename = f"{timestamp}_{file_type}_snapshot.json"
            
            # Save snapshot
            snapshot_path = self.output_directory / snapshot_filename
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
                
            # Log the snapshot
            self.logger.info(f"Created snapshot: {snapshot_filename}")
            
            # Extract key metrics for quick analysis
            metrics = self._extract_key_metrics(save_data)
            self._log_metrics(timestamp, file_type, metrics)
            
        except Exception as e:
            self.logger.error(f"Error processing {filename}: {str(e)}")
    
    def _extract_key_metrics(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from save data for trending."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'game_date': save_data.get('date', 'Unknown'),
            'balance': save_data.get('balance', 0),
            'total_users': 0,
            'satisfaction': 0,
            'total_employees': 0,
            'features_count': 0,
            'monthly_expenses': 0
        }
        
        try:
            # Extract product metrics
            if 'progress' in save_data and 'products' in save_data['progress']:
                products = save_data['progress']['products']
                if products:
                    first_product = products[0]
                    if 'users' in first_product:
                        metrics['total_users'] = first_product['users'].get('total', 0)
                        metrics['satisfaction'] = first_product['users'].get('satisfaction', 0)
            
            # Count employees from workstations
            if 'office' in save_data and 'workstations' in save_data['office']:
                workstations = save_data['office']['workstations']
                metrics['total_employees'] = len([ws for ws in workstations if 'employee' in ws])
                
                # Calculate monthly expenses from salaries
                total_salaries = sum(
                    ws.get('employee', {}).get('salary', 0) 
                    for ws in workstations 
                    if 'employee' in ws
                )
                metrics['monthly_expenses'] = total_salaries
            
            # Count features
            if 'featureInstances' in save_data:
                metrics['features_count'] = len(save_data['featureInstances'])
                
        except Exception as e:
            self.logger.warning(f"Error extracting metrics: {str(e)}")
            
        return metrics
    
    def _log_metrics(self, timestamp: str, file_type: str, metrics: Dict[str, Any]):
        """Log metrics to a CSV-like format for trending analysis."""
        metrics_log_path = self.output_directory / "metrics_timeline.jsonl"
        
        log_entry = {
            'timestamp': timestamp,
            'file_type': file_type,
            **metrics
        }
        
        with open(metrics_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


class GameStateMonitor:
    """Main class for monitoring Startup Company game state in real-time."""
    
    def __init__(self, save_directory: str | None = None, output_directory: str | None = None):
        if save_directory is None:
            save_directory = r"C:\Users\patss\Saved Games\Startup Company\testing_v1"
        
        if output_directory is None:
            output_directory = "game_saves"
            
        self.save_directory = save_directory
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        self.observer = Observer()
        self.event_handler = SaveFileWatcher(save_directory, output_directory)
        
    def start_monitoring(self):
        """Start monitoring the save directory."""
        print(f"Starting to monitor: {self.save_directory}")
        print(f"Snapshots will be saved to: {self.output_directory}")
        
        self.observer.schedule(
            self.event_handler, 
            self.save_directory, 
            recursive=False
        )
        
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping file monitor...")
            self.observer.stop()
            
        self.observer.join()
        print("File monitoring stopped.")
    
    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """Get the most recent metrics from the timeline."""
        metrics_log_path = self.output_directory / "metrics_timeline.jsonl"
        
        if not metrics_log_path.exists():
            return None
            
        try:
            with open(metrics_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    return json.loads(lines[-1].strip())
        except Exception as e:
            print(f"Error reading latest metrics: {e}")
            
        return None
    
    def create_initial_snapshot(self):
        """Create initial snapshots of existing save files."""
        save_path = Path(self.save_directory)
        
        for filename in ["sg_rts technology & solutions llc.json", "sg_rts technology & solutions llc_autosave.json"]:
            file_path = save_path / filename
            if file_path.exists():
                self.event_handler._process_save_file(file_path, filename)
                print(f"Created initial snapshot for {filename}")


if __name__ == "__main__":
    monitor = GameStateMonitor()
    
    # Create initial snapshots
    monitor.create_initial_snapshot()
    
    # Start real-time monitoring
    monitor.start_monitoring()