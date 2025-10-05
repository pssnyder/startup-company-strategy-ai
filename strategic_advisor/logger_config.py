"""
Strategic Advisor - Logging Configuration
Clean logging without Unicode characters that cause Windows console issues
"""

import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO):
    """Configure logging to avoid Unicode encoding issues"""
    
    # Create logs directory
    log_dir = Path("strategic_advisor/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(
        log_dir / 'strategic_advisor.log', 
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Console handler with safe encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger('strategic_advisor')

# Message templates without Unicode
SUCCESS_MESSAGES = {
    'database_init': 'Database initialized: {}',
    'monitoring_init': 'File monitoring initialized',
    'capacity_init': 'Capacity analyzer ready',
    'advisor_init': 'Strategic advisor system ready',
    'analysis_complete': 'Capacity analysis complete: {:.1f}% utilization, {} capacity gap',
    'file_processed': 'Save file processed: {}',
    'test_passed': 'Test passed: {}'
}

WARNING_MESSAGES = {
    'high_utilization': 'High capacity utilization detected: {:.1f}%',
    'low_inventory': 'Low inventory warning: {}',
    'file_not_found': 'Save file not found: {}'
}

ERROR_MESSAGES = {
    'database_error': 'Database operation failed: {}',
    'file_error': 'File operation failed: {}',
    'analysis_error': 'Analysis failed: {}'
}