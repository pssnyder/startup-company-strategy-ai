"""
Strategic Advisor - SQLite Database Schema
Lightweight database for game save analysis with concurrent read access
"""

import sqlite3
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from contextlib import contextmanager
from .logger_config import setup_logging, SUCCESS_MESSAGES

from .logger_config import setup_logging, SUCCESS_MESSAGES, ERROR_MESSAGES

# Setup safe logging
setup_logging()
logger = logging.getLogger(__name__)

class GameDatabase:
    """SQLite database manager with concurrent read access support"""
    
    def __init__(self, db_path: str = "strategic_advisor/game_data.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use thread-local storage for connections to support concurrent access
        self._local = threading.local()
        
        # Initialize schema
        self._initialize_schema()
        logger.info(SUCCESS_MESSAGES['database_init'].format(self.db_path))
    
    def _get_connection(self, read_only: bool = False) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            if read_only:
                # Read-only connection for concurrent access
                self._local.connection = sqlite3.connect(
                    f"file:{self.db_path}?mode=ro", 
                    uri=True,
                    check_same_thread=False
                )
            else:
                # Read-write connection
                self._local.connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False
                )
            
            self._local.connection.row_factory = sqlite3.Row
            
            # Enable WAL mode for better concurrent access
            if not read_only:
                self._local.connection.execute("PRAGMA journal_mode=WAL")
                self._local.connection.execute("PRAGMA synchronous=NORMAL")
        
        return self._local.connection
    
    @contextmanager
    def get_read_connection(self):
        """Context manager for read-only connections"""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_write_connection(self):
        """Context manager for write connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _initialize_schema(self):
        """Create database tables if they don't exist"""
        
        schema_sql = """
        -- Main save file metadata
        CREATE TABLE IF NOT EXISTS save_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            game_date TEXT,
            real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            company_name TEXT,
            game_state TEXT,
            balance INTEGER,
            total_employees INTEGER,
            game_version TEXT,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            raw_data TEXT  -- JSON data as text
        );
        
        -- Employee data
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            employee_id TEXT,
            name TEXT,
            position TEXT,
            salary INTEGER,
            skill_level REAL,
            productivity REAL,
            assigned_task TEXT,
            hire_date TEXT,
            experience INTEGER,
            is_active INTEGER DEFAULT 1
        );
        
        -- Financial transactions
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            transaction_date TEXT,
            amount INTEGER,
            transaction_type TEXT,
            description TEXT,
            category TEXT
        );
        
        -- Inventory items
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            item_name TEXT,
            quantity INTEGER,
            item_type TEXT,
            value_per_unit INTEGER
        );
        
        -- Research progress
        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            research_item TEXT,
            progress_points INTEGER,
            is_completed INTEGER,
            category TEXT
        );
        
        -- Product features
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            feature_name TEXT,
            feature_type TEXT,
            level INTEGER,
            development_progress REAL,
            assigned_employees TEXT,
            dependencies TEXT
        );
        
        -- Market data
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            metric_name TEXT,
            metric_value REAL,
            category TEXT
        );
        
        -- Office/infrastructure
        CREATE TABLE IF NOT EXISTS office_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            workstations_total INTEGER,
            workstations_occupied INTEGER,
            office_level INTEGER,
            monthly_rent INTEGER
        );
        
        -- Calculated metrics (for caching complex calculations)
        CREATE TABLE IF NOT EXISTS calculated_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            metric_name TEXT,
            metric_value REAL,
            calculation_method TEXT,
            calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_save_files_game_date ON save_files(game_date);
        CREATE INDEX IF NOT EXISTS idx_save_files_timestamp ON save_files(real_timestamp);
        CREATE INDEX IF NOT EXISTS idx_employees_save_file ON employees(save_file_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_save_file ON transactions(save_file_id);
        CREATE INDEX IF NOT EXISTS idx_calculated_metrics_name ON calculated_metrics(metric_name);
        """
        
        try:
            with self.get_write_connection() as conn:
                conn.executescript(schema_sql)
            logger.info(SUCCESS_MESSAGES['database_init'].format(self.db_path))
        except Exception as e:
            logger.error(f"❌ Schema initialization failed: {str(e)}")
            raise
    
    def ingest_save_file(self, file_path: Path, save_data: Dict[str, Any]) -> int:
        """
        Ingest a complete save file into the database
        Returns the save_file_id for reference
        """
        try:
            with self.get_write_connection() as conn:
                # Extract metadata
                metadata = {
                    'filename': file_path.name,
                    'game_date': save_data.get('date', 'unknown'),
                    'file_size': file_path.stat().st_size,
                    'company_name': save_data.get('companyName', 'unknown'),
                    'game_state': save_data.get('state', 'unknown'),
                    'balance': save_data.get('balance', 0),
                    'total_employees': len(save_data.get('employeesOrder', [])),
                    'game_version': save_data.get('lastVersion', 'unknown'),
                    'raw_data': json.dumps(save_data)
                }
                
                # Insert main save file record
                save_file_id = self._insert_save_file(conn, metadata)
                
                # Insert related data
                self._insert_employees(conn, save_file_id, save_data)
                self._insert_transactions(conn, save_file_id, save_data)
                self._insert_inventory(conn, save_file_id, save_data)
                self._insert_research(conn, save_file_id, save_data)
                self._insert_office_data(conn, save_file_id, save_data)
                
                logger.info(f"✅ Save file ingested: {file_path.name} (ID: {save_file_id})")
                return save_file_id
                
        except Exception as e:
            logger.error(f"❌ Error ingesting save file: {str(e)}")
            raise
    
    def _insert_save_file(self, conn: sqlite3.Connection, metadata: Dict[str, Any]) -> int:
        """Insert main save file record"""
        sql = """
        INSERT OR REPLACE INTO save_files 
        (filename, game_date, file_size, company_name, game_state, balance, 
         total_employees, game_version, raw_data, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        cursor = conn.execute(sql, (
            metadata['filename'], metadata['game_date'], metadata['file_size'],
            metadata['company_name'], metadata['game_state'], metadata['balance'],
            metadata['total_employees'], metadata['game_version'], metadata['raw_data']
        ))
        return cursor.lastrowid
    
    def _insert_employees(self, conn: sqlite3.Connection, save_file_id: int, save_data: Dict[str, Any]):
        """Insert employee data"""
        employees = save_data.get('employeesOrder', [])
        if not employees:
            return
        
        # Clear existing employee data for this save file
        conn.execute("DELETE FROM employees WHERE save_file_id = ?", (save_file_id,))
        
        # Insert employee records
        for emp_id in employees:
            conn.execute("""
                INSERT INTO employees (save_file_id, employee_id, name, position, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (save_file_id, emp_id, f"Employee_{emp_id}", 'unknown', 1))
    
    def _insert_transactions(self, conn: sqlite3.Connection, save_file_id: int, save_data: Dict[str, Any]):
        """Insert transaction data"""
        transactions = save_data.get('transactions', [])
        if not transactions:
            return
        
        # Clear existing transaction data for this save file
        conn.execute("DELETE FROM transactions WHERE save_file_id = ?", (save_file_id,))
        
        # Insert transaction records
        for trans in transactions:
            conn.execute("""
                INSERT INTO transactions (save_file_id, transaction_date, amount, 
                                        transaction_type, description, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                save_file_id, trans.get('date', 'unknown'), trans.get('amount', 0),
                trans.get('type', 'unknown'), trans.get('reason', ''), 
                trans.get('category', 'general')
            ))
    
    def _insert_inventory(self, conn: sqlite3.Connection, save_file_id: int, save_data: Dict[str, Any]):
        """Insert inventory data"""
        inventory = save_data.get('inventory', {})
        if not inventory:
            return
        
        # Clear existing inventory data for this save file
        conn.execute("DELETE FROM inventory WHERE save_file_id = ?", (save_file_id,))
        
        # Insert inventory records
        for item_name, quantity in inventory.items():
            if isinstance(quantity, dict):
                actual_quantity = quantity.get('amount', 0)
            else:
                actual_quantity = quantity
                
            conn.execute("""
                INSERT INTO inventory (save_file_id, item_name, quantity, item_type)
                VALUES (?, ?, ?, ?)
            """, (save_file_id, item_name, actual_quantity, 'component'))
    
    def _insert_research(self, conn: sqlite3.Connection, save_file_id: int, save_data: Dict[str, Any]):
        """Insert research data"""
        research_points = save_data.get('researchPoints', 0)
        researched_items = save_data.get('researchedItems', [])
        
        # Clear existing research data for this save file
        conn.execute("DELETE FROM research WHERE save_file_id = ?", (save_file_id,))
        
        # Insert research records
        for item in researched_items:
            conn.execute("""
                INSERT INTO research (save_file_id, research_item, progress_points, 
                                    is_completed, category)
                VALUES (?, ?, ?, ?, ?)
            """, (save_file_id, item, research_points, 1, 'completed'))
    
    def _insert_office_data(self, conn: sqlite3.Connection, save_file_id: int, save_data: Dict[str, Any]):
        """Insert office data"""
        office = save_data.get('office', {})
        if not office:
            return
        
        # Clear existing office data for this save file
        conn.execute("DELETE FROM office_data WHERE save_file_id = ?", (save_file_id,))
        
        workstations = office.get('workstations', [])
        occupied_count = sum(1 for ws in workstations if ws.get('employee'))
        
        conn.execute("""
            INSERT INTO office_data (save_file_id, workstations_total, workstations_occupied, 
                                   office_level, monthly_rent)
            VALUES (?, ?, ?, ?, ?)
        """, (save_file_id, len(workstations), occupied_count, 
              office.get('level', 1), office.get('rent', 0)))
    
    def get_latest_save_file(self) -> Optional[Dict[str, Any]]:
        """Get the most recent save file data"""
        with self.get_read_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM save_files 
                ORDER BY real_timestamp DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_balance_trend(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get balance trend over time"""
        with self.get_read_connection() as conn:
            cursor = conn.execute("""
                SELECT game_date, real_timestamp, balance, total_employees
                FROM save_files 
                ORDER BY real_timestamp DESC
                LIMIT ?
            """, (limit,))
            results = cursor.fetchall()
            return [dict(row) for row in reversed(results)]
    
    def get_capacity_metrics(self) -> Dict[str, Any]:
        """Calculate team capacity metrics from latest save"""
        with self.get_read_connection() as conn:
            # Get latest office data
            cursor = conn.execute("""
                SELECT workstations_total, workstations_occupied 
                FROM office_data o
                JOIN save_files s ON o.save_file_id = s.id
                ORDER BY s.real_timestamp DESC
                LIMIT 1
            """)
            office_data = cursor.fetchone()
            
            if not office_data:
                return {'capacity_utilization': 0, 'available_capacity': 0}
            
            utilization = (office_data['workstations_occupied'] / office_data['workstations_total']) * 100
            available = office_data['workstations_total'] - office_data['workstations_occupied']
            
            return {
                'capacity_utilization': round(utilization, 1),
                'available_capacity': available,
                'total_workstations': office_data['workstations_total'],
                'occupied_workstations': office_data['workstations_occupied']
            }
    
    def get_inventory_status(self) -> List[Dict[str, Any]]:
        """Get current inventory status"""
        with self.get_read_connection() as conn:
            cursor = conn.execute("""
                SELECT item_name, quantity, item_type
                FROM inventory i
                JOIN save_files s ON i.save_file_id = s.id
                WHERE s.id = (SELECT id FROM save_files ORDER BY real_timestamp DESC LIMIT 1)
                ORDER BY item_name
            """)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def execute_read_query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a read-only query for dashboard exploration"""
        with self.get_read_connection() as conn:
            cursor = conn.execute(sql, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]