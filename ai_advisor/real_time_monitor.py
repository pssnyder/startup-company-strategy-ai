"""
Integrated real-time monitor combining file watching, data analysis, and AI strategy.
This is the main entry point for the real-time game companion dashboard.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import queue

from .file_watcher import GameStateMonitor
from .dashboard import RealTimeDashboard
from .main import StartupCompanyAdvisor


class RealTimeGameAdvisor:
    """Real-time game companion that monitors save files and provides AI insights."""
    
    def __init__(self, 
                 save_directory: str | None = None, 
                 output_directory: str = "game_saves",
                 gemini_api_key: str | None = None):
        
        # Initialize components
        self.file_monitor = GameStateMonitor(save_directory, output_directory)
        self.dashboard = RealTimeDashboard(output_directory)
        self.ai_advisor = StartupCompanyAdvisor(gemini_api_key=gemini_api_key)
        
        # Communication queue for file updates
        self.update_queue = queue.Queue()
        self.is_running = False
        
        # Cache for latest analysis
        self.latest_analysis = {}
        self.last_ai_analysis_time = None
        
    def start_monitoring(self, ai_analysis_interval: int = 300):  # 5 minutes
        """Start the complete monitoring system."""
        print("🚀 Starting Real-Time Startup Company Advisor")
        print(f"   📁 Monitoring: {self.file_monitor.save_directory}")
        print(f"   📊 Dashboard data: {self.file_monitor.output_directory}")
        print(f"   🤖 AI analysis every {ai_analysis_interval} seconds")
        print("   Press Ctrl+C to stop\n")
        
        # Create initial snapshots
        self.file_monitor.create_initial_snapshot()
        
        self.is_running = True
        
        # Start file monitoring in a separate thread
        monitor_thread = threading.Thread(target=self._run_file_monitor, daemon=True)
        monitor_thread.start()
        
        # Start dashboard processing loop
        dashboard_thread = threading.Thread(target=self._run_dashboard_processor, daemon=True)
        dashboard_thread.start()
        
        # Main loop for AI analysis
        try:
            self._run_ai_analysis_loop(ai_analysis_interval)
        except KeyboardInterrupt:
            print("\n🛑 Stopping Real-Time Advisor...")
            self.is_running = False
            
    def _run_file_monitor(self):
        """Run the file monitor in a separate thread."""
        # Monkey patch the event handler to notify us of updates
        original_process = self.file_monitor.event_handler._process_save_file
        
        def notify_update(file_path, filename):
            original_process(file_path, filename)
            self.update_queue.put({'type': 'file_update', 'file': filename, 'time': datetime.now()})
            
        self.file_monitor.event_handler._process_save_file = notify_update
        
        # Start monitoring
        self.file_monitor.observer.schedule(
            self.file_monitor.event_handler,
            self.file_monitor.save_directory,
            recursive=False
        )
        
        self.file_monitor.observer.start()
        
        try:
            while self.is_running:
                time.sleep(1)
        finally:
            self.file_monitor.observer.stop()
            self.file_monitor.observer.join()
            
    def _run_dashboard_processor(self):
        """Process dashboard updates in a separate thread."""
        while self.is_running:
            try:
                # Check for file updates
                update = self.update_queue.get(timeout=5)
                
                if update['type'] == 'file_update':
                    print(f"📥 Save file updated: {update['file']} at {update['time'].strftime('%H:%M:%S')}")
                    
                    # Generate dashboard update
                    dashboard_data = self.dashboard.generate_dashboard_data()
                    self.latest_analysis['dashboard'] = dashboard_data
                    
                    # Export dashboard data
                    self.dashboard.export_dashboard_json()
                    
                    # Print key alerts
                    self._print_dashboard_summary(dashboard_data)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Dashboard processing error: {e}")
                
    def _run_ai_analysis_loop(self, interval: int):
        """Run periodic AI analysis."""
        while self.is_running:
            try:
                # Check if we should run AI analysis
                current_time = datetime.now()
                
                should_analyze = (
                    self.last_ai_analysis_time is None or
                    (current_time - self.last_ai_analysis_time).seconds >= interval
                )
                
                if should_analyze:
                    self._run_ai_analysis()
                    self.last_ai_analysis_time = current_time
                    
                # Sleep for a short period
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ AI analysis error: {e}")
                time.sleep(30)  # Wait longer after error
                
    def _run_ai_analysis(self):
        """Run AI analysis on current game state."""
        try:
            # Get latest save file
            latest_snapshots = list(self.file_monitor.output_directory.glob("*_snapshot.json"))
            
            if not latest_snapshots:
                print("⚠️ No save files found for AI analysis")
                return
                
            # Get the most recent snapshot
            latest_file = max(latest_snapshots, key=lambda x: x.stat().st_mtime)
            
            print(f"🤖 Running AI analysis on {latest_file.name}...")
            
            # Load save file and run comprehensive analysis
            if self.ai_advisor.load_save_file(Path(latest_file)):
                # Run async analysis in event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    analysis = loop.run_until_complete(self.ai_advisor.analyze_game_state())
                finally:
                    loop.close()
            else:
                print("❌ Failed to load save file for AI analysis")
                return
            
            self.latest_analysis['ai'] = analysis
            
            # Print AI insights
            self._print_ai_insights(analysis)
            
            # Save analysis
            analysis_file = self.file_monitor.output_directory / f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)
                
        except Exception as e:
            print(f"❌ AI Analysis failed: {e}")
            
    def _print_dashboard_summary(self, dashboard_data: Dict[str, Any]):
        """Print a summary of key dashboard metrics."""
        if not dashboard_data.get('current_state'):
            return
            
        state = dashboard_data['current_state']
        alerts = dashboard_data.get('alerts', [])
        
        print(f"📊 Current State: ${state['balance']:,.0f} | {state['total_users']:,} users | {state['satisfaction']:.1f}% satisfaction")
        
        # Print critical alerts
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        if critical_alerts:
            for alert in critical_alerts:
                print(f"🚨 {alert['title']}: {alert['message']}")
        
        print()  # Empty line for readability
        
    def _print_ai_insights(self, analysis: Dict[str, Any]):
        """Print AI insights in a readable format."""
        print("🧠 AI Strategic Insights:")
        
        # Print strategy if available
        if 'ai_strategy' in analysis and analysis['ai_strategy']:
            strategy = analysis['ai_strategy']
            if isinstance(strategy, str):
                # Split into lines and print with formatting
                lines = strategy.split('\n')
                for line in lines:
                    if line.strip():
                        if line.startswith('**') or line.startswith('#'):
                            print(f"   💡 {line.strip()}")
                        else:
                            print(f"      {line.strip()}")
            
        # Print key recommendations
        if 'alerts' in analysis:
            critical_alerts = [a for a in analysis['alerts'] if a.get('level') == 'critical']
            if critical_alerts:
                print("   🔥 Critical Issues:")
                for alert in critical_alerts:
                    print(f"      • {alert.get('message', 'Unknown alert')}")
                    
        print("=" * 60)
        print()
        
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a complete status summary for external access."""
        return {
            'is_running': self.is_running,
            'last_update': datetime.now().isoformat(),
            'latest_analysis': self.latest_analysis,
            'monitoring_directory': str(self.file_monitor.save_directory),
            'output_directory': str(self.file_monitor.output_directory)
        }
        
    def stop(self):
        """Stop the monitoring system."""
        self.is_running = False


def main():
    """Main entry point for the real-time advisor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-Time Startup Company Game Advisor")
    parser.add_argument("--save-dir", help="Path to game save directory")
    parser.add_argument("--output-dir", default="game_saves", help="Output directory for data")
    parser.add_argument("--gemini-key", help="Gemini API key for AI analysis")
    parser.add_argument("--ai-interval", type=int, default=300, help="AI analysis interval in seconds")
    
    args = parser.parse_args()
    
    advisor = RealTimeGameAdvisor(
        save_directory=args.save_dir,
        output_directory=args.output_dir,
        gemini_api_key=args.gemini_key
    )
    
    advisor.start_monitoring(ai_analysis_interval=args.ai_interval)


if __name__ == "__main__":
    main()