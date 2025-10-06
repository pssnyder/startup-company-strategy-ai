"""
Strategic Advisor - Main Coordinator
Orchestrates file monitoring, database ingestion, and decision modules
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .file_monitor import GameSaveMonitor
from .database_sqlite import GameDatabase
from .decision_modules.capacity_analyzer import CapacityAnalyzer
from .logger_config import setup_logging, SUCCESS_MESSAGES, WARNING_MESSAGES, ERROR_MESSAGES

# Setup safe logging
setup_logging()
logger = logging.getLogger(__name__)

class StrategicAdvisor:
    """
    Main coordinator for the strategic advisor system
    Orchestrates file monitoring, database ingestion, and strategic analysis
    """
    
    def __init__(self, 
                 save_directory: str = "c:/Users/patss/Saved Games/Startup Company/testing_v1",
                 database_path: str = "strategic_advisor/game_data.db"):
        """Initialize the strategic advisor system"""
        
        self.save_directory = Path(save_directory)
        self.database_path = database_path
        
        # Initialize components
        self.database = GameDatabase(database_path)
        self.file_monitor = GameSaveMonitor(
            source_dir=str(self.save_directory),
            target_dir="strategic_advisor/save_files",
            company_name="momentum ai"
        )
        
        # Initialize decision modules
        self.capacity_analyzer = CapacityAnalyzer(self.database)
        
        # File monitoring state
        self.observer = None
        self.monitoring_active = False
        
        # Analysis state
        self.last_analysis_time = None
        self.analysis_interval = 300  # 5 minutes between full analyses
        
        logger.info(SUCCESS_MESSAGES['advisor_init'])
    
    def process_save_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single save file and return analysis results
        Used for manual file processing without monitoring
        """
        try:
            file_path_obj = Path(file_path)
            
            # Load the save file
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            logger.info(f"Processing save file: {file_path_obj.name}")
            
            # Ingest into database
            save_file_id = self.database.ingest_save_file(file_path_obj, save_data)
            
            # Run analysis
            analysis_results = self._run_all_decision_modules()
            
            # Generate dashboard data
            dashboard_data = self.get_dashboard_data()
            
            logger.info(SUCCESS_MESSAGES['file_processed'].format(file_path_obj.name))
            
            return {
                'success': True,
                'save_file_id': save_file_id,
                'analysis_results': analysis_results,
                'dashboard_data': dashboard_data
            }
            
        except Exception as e:
            error_msg = ERROR_MESSAGES['file_error'].format(str(e))
            logger.error(error_msg)
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_monitoring(self):
        """Start the complete monitoring and analysis pipeline"""
        logger.info("Starting strategic monitoring pipeline...")
        
        # Set up file monitor with watchdog observer
        from watchdog.observers import Observer
        
        self.observer = Observer()
        self.observer.schedule(self.file_monitor, str(self.save_directory), recursive=False)
        self.observer.start()
        self.monitoring_active = True
        
        # Perform initial sync
        self.file_monitor.manual_sync()
        
        logger.info("Strategic Advisor is now monitoring and analyzing game saves")
        
        try:
            # Keep the main thread alive
            while self.monitoring_active:
                # Perform periodic full analysis
                if self._should_run_full_analysis():
                    self._run_full_strategic_analysis()
                
                # Check for new files and process them
                self._check_for_new_save_files()
                
                # Sleep briefly to prevent busy waiting
                import time
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Stopping Strategic Advisor...")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.monitoring_active = False
        logger.info("Strategic Advisor monitoring stopped")
    
    def _check_for_new_save_files(self):
        """Check for new save files in the target directory and process them"""
        try:
            save_files_dir = Path("strategic_advisor/save_files")
            if not save_files_dir.exists():
                return
            
            # Get all JSON files in the save files directory
            json_files = list(save_files_dir.glob("*.json"))
            
            # Check each file to see if it needs processing
            for file_path in json_files:
                # Check if this file has been processed
                if not self._is_file_processed(file_path):
                    self._on_new_save_file(file_path)
                    self._mark_file_processed(file_path)
                    
        except Exception as e:
            logger.error(ERROR_MESSAGES['file_error'].format(str(e)))
    
    def _is_file_processed(self, file_path: Path) -> bool:
        """Check if a file has already been processed"""
        try:
            # Check if this filename exists in our database
            query = "SELECT COUNT(*) as count FROM save_files WHERE filename = ?"
            results = self.database.execute_read_query(query, (file_path.name,))
            return results[0]['count'] > 0 if results else False
        except:
            return False
    
    def _mark_file_processed(self, file_path: Path):
        """Mark a file as processed (this happens automatically in _on_new_save_file)"""
        pass
    
    def _on_new_save_file(self, file_path: Path):
        """Callback when a new save file is detected"""
        logger.info(f"Processing new save file: {file_path.name}")
        
        try:
            # Load and parse the save file
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Ingest into database
            save_file_id = self.database.ingest_save_file(file_path, save_data)
            
            # Run quick analysis for immediate alerts
            self._run_immediate_analysis(save_file_id)
            
        except Exception as e:
            logger.error(f"Error processing save file {file_path}: {str(e)}")
    
    def _should_run_full_analysis(self) -> bool:
        """Check if it's time for a full strategic analysis"""
        if self.last_analysis_time is None:
            return True
        
        time_since_last = (datetime.now() - self.last_analysis_time).total_seconds()
        return time_since_last >= self.analysis_interval
    
    def _run_immediate_analysis(self, save_file_id: int):
        """Run quick analysis for immediate alerts"""
        logger.info("Running immediate analysis...")
        
        try:
            # Quick capacity check
            capacity_metrics = self.capacity_analyzer.analyze_current_capacity()
            alerts = capacity_metrics.get_quantitative_alerts()
            
            # Log immediate alerts
            for alert in alerts:
                logger.warning(f"IMMEDIATE ALERT: {alert}")
            
            # Store alerts in database for dashboard
            self._store_alerts(save_file_id, alerts)
            
        except Exception as e:
            logger.error(f"Immediate analysis failed: {str(e)}")
    
    def _run_full_strategic_analysis(self):
        """Run complete strategic analysis across all modules"""
        logger.info("Running full strategic analysis...")
        self.last_analysis_time = datetime.now()
        
        try:
            # Get latest save file
            latest_save = self.database.get_latest_save_file()
            if not latest_save:
                logger.warning("No save files available for analysis")
                return
            
            # Run all decision modules
            analysis_results = self._run_all_decision_modules()
            
            # Generate comprehensive report
            report = self._generate_strategic_report(analysis_results)
            
            # Save report
            self._save_strategic_report(report)
            
            logger.info("Full strategic analysis complete")
            
        except Exception as e:
            logger.error(f"Full strategic analysis failed: {str(e)}")
    
    def _run_all_decision_modules(self) -> Dict[str, Any]:
        """Execute all decision modules and collect results"""
        results = {}
        
        try:
            # Capacity Analysis
            logger.info("Running capacity analysis...")
            capacity_metrics = self.capacity_analyzer.analyze_current_capacity()
            capacity_recommendations = self.capacity_analyzer.get_capacity_recommendations(capacity_metrics)
            capacity_trends = self.capacity_analyzer.calculate_trend_analysis()
            
            results['capacity'] = {
                'metrics': capacity_metrics,
                'recommendations': capacity_recommendations,
                'trends': capacity_trends
            }
            
            # TODO: Add more decision modules here
            # - Production Optimizer
            # - Research Prioritizer  
            # - Financial Planner
            # - Market Analyzer
            
            logger.info(f"Completed {len(results)} decision module analyses")
            
        except Exception as e:
            logger.error(f"Decision module execution failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _generate_strategic_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive strategic report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_modules': list(analysis_results.keys()),
            'executive_summary': [],
            'quantitative_metrics': {},
            'immediate_actions': [],
            'strategic_recommendations': [],
            'trend_analysis': {},
            'risk_alerts': []
        }
        
        # Process capacity analysis
        if 'capacity' in analysis_results:
            capacity_data = analysis_results['capacity']
            capacity_metrics = capacity_data['metrics']
            
            # Add to executive summary
            report['executive_summary'].append(
                f"Team Capacity: {capacity_metrics.workstation_utilization:.1f}% utilization, "
                f"{capacity_metrics.growth_capacity} hiring slots available"
            )
            
            # Add quantitative metrics
            report['quantitative_metrics']['capacity_utilization'] = capacity_metrics.workstation_utilization
            report['quantitative_metrics']['growth_capacity'] = capacity_metrics.growth_capacity
            report['quantitative_metrics']['team_efficiency'] = capacity_metrics.employee_efficiency
            
            # Add immediate actions
            if capacity_metrics.capacity_shortage > 0:
                report['immediate_actions'].append(
                    f"Purchase {capacity_metrics.capacity_shortage} workstations"
                )
            
            # Add strategic recommendations
            report['strategic_recommendations'].extend(capacity_data['recommendations'])
            
            # Add risk alerts
            report['risk_alerts'].extend(capacity_metrics.get_quantitative_alerts())
            
            # Add trend data
            report['trend_analysis']['capacity'] = capacity_data['trends']
        
        return report
    
    def _save_strategic_report(self, report: Dict[str, Any]):
        """Save strategic report to file and log key insights"""
        try:
            # Save to file
            output_path = Path("strategic_advisor/reports")
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = output_path / f"strategic_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            # Log executive summary
            logger.info("STRATEGIC REPORT SUMMARY:")
            for item in report['executive_summary']:
                logger.info(f"   • {item}")
            
            # Log immediate actions
            if report['immediate_actions']:
                logger.info("IMMEDIATE ACTIONS REQUIRED:")
                for action in report['immediate_actions']:
                    logger.info(f"   TARGET: {action}")
            
            # Log risk alerts
            if report['risk_alerts']:
                logger.info("RISK ALERTS:")
                for alert in report['risk_alerts']:
                    logger.info(f"   WARNING: {alert}")
            
            logger.info(f"Strategic report saved: {report_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to save strategic report: {str(e)}")
    
    def _store_alerts(self, save_file_id: int, alerts: List[str]):
        """Store alerts in database for dashboard access"""
        try:
            with self.database.get_write_connection() as conn:
                for alert in alerts:
                    conn.execute("""
                        INSERT INTO calculated_metrics (save_file_id, metric_name, metric_value, calculation_method)
                        VALUES (?, ?, ?, ?)
                    """, (save_file_id, 'alert', 1.0, alert))
            
        except Exception as e:
            logger.error(f"Failed to store alerts: {str(e)}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for dashboard display"""
        try:
            # Get latest save file info
            latest_save = self.database.get_latest_save_file()
            
            # Get capacity metrics
            capacity_metrics = self.capacity_analyzer.analyze_current_capacity()
            capacity_trends = self.capacity_analyzer.calculate_trend_analysis()
            
            # Get recent alerts
            recent_alerts = self._get_recent_alerts()
            
            dashboard_data = {
                'company_info': {
                    'name': latest_save.get('company_name', 'Unknown') if latest_save else 'No Data',
                    'balance': latest_save.get('balance', 0) if latest_save else 0,
                    'employees': latest_save.get('total_employees', 0) if latest_save else 0,
                    'last_update': latest_save.get('real_timestamp', 'Never') if latest_save else 'Never'
                },
                'capacity_metrics': {
                    'workstation_utilization': capacity_metrics.workstation_utilization,
                    'growth_capacity': capacity_metrics.growth_capacity,
                    'team_efficiency': capacity_metrics.employee_efficiency,
                    'capacity_shortage': capacity_metrics.capacity_shortage
                },
                'alerts': recent_alerts,
                'trends': {
                    'capacity': capacity_trends
                },
                'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_recent_alerts(self, limit: int = 10) -> List[str]:
        """Get recent alerts from database"""
        try:
            query = """
            SELECT calculation_method as alert_text
            FROM calculated_metrics 
            WHERE metric_name = 'alert'
            ORDER BY calculated_at DESC
            LIMIT ?
            """
            
            results = self.database.execute_read_query(query, (limit,))
            return [row['alert_text'] for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {str(e)}")
            return []

def main():
    """Main entry point for strategic advisor"""
    try:
        # Initialize and start strategic advisor
        advisor = StrategicAdvisor()
        advisor.start_monitoring()
        
    except Exception as e:
        logger.error(f"Strategic Advisor startup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()