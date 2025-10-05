"""
Strategic Advisor - Database Schema
PostgreSQL database for game save analysis with flexible schema
"""

import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class GameDatabase:
    """Database manager for game save data with flexible schema"""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize database connection
        
        db_config should contain: host, database, user, password, port
        """
        self.db_config = db_config
        self.connection = None
        self._connect()
        self._initialize_schema()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            raise
    
    def _initialize_schema(self):
        """Create database tables if they don't exist"""
        
        schema_sql = """
        -- Main save file metadata
        CREATE TABLE IF NOT EXISTS save_files (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            game_date VARCHAR(50),
            real_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            company_name VARCHAR(255),
            game_state VARCHAR(50),
            balance BIGINT,
            total_employees INTEGER,
            game_version VARCHAR(50),
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_data JSONB,
            UNIQUE(filename)
        );
        
        -- Employee data
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            employee_id VARCHAR(100),
            name VARCHAR(255),
            position VARCHAR(100),
            salary INTEGER,
            skill_level FLOAT,
            productivity FLOAT,
            assigned_task VARCHAR(255),
            hire_date VARCHAR(50),
            experience INTEGER,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        -- Financial transactions
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            transaction_date VARCHAR(50),
            amount BIGINT,
            transaction_type VARCHAR(100),
            description TEXT,
            category VARCHAR(100)
        );
        
        -- Inventory items
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            item_name VARCHAR(255),
            quantity INTEGER,
            item_type VARCHAR(100),
            value_per_unit INTEGER
        );
        
        -- Research progress
        CREATE TABLE IF NOT EXISTS research (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            research_item VARCHAR(255),
            progress_points INTEGER,
            is_completed BOOLEAN,
            category VARCHAR(100)
        );
        
        -- Product features
        CREATE TABLE IF NOT EXISTS features (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            feature_name VARCHAR(255),
            feature_type VARCHAR(100),
            level INTEGER,
            development_progress FLOAT,
            assigned_employees TEXT,
            dependencies TEXT
        );
        
        -- Market data
        CREATE TABLE IF NOT EXISTS market_data (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            metric_name VARCHAR(255),
            metric_value FLOAT,
            category VARCHAR(100)
        );
        
        -- Office/infrastructure
        CREATE TABLE IF NOT EXISTS office_data (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            workstations_total INTEGER,
            workstations_occupied INTEGER,
            office_level INTEGER,
            monthly_rent INTEGER
        );
        
        -- Calculated metrics (for caching complex calculations)
        CREATE TABLE IF NOT EXISTS calculated_metrics (
            id SERIAL PRIMARY KEY,
            save_file_id INTEGER REFERENCES save_files(id),
            metric_name VARCHAR(255),
            metric_value FLOAT,
            calculation_method VARCHAR(255),
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_save_files_game_date ON save_files(game_date);
        CREATE INDEX IF NOT EXISTS idx_save_files_timestamp ON save_files(real_timestamp);
        CREATE INDEX IF NOT EXISTS idx_employees_save_file ON employees(save_file_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_save_file ON transactions(save_file_id);
        CREATE INDEX IF NOT EXISTS idx_calculated_metrics_name ON calculated_metrics(metric_name);
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(schema_sql)
            logger.info("✅ Database schema initialized")
        except Exception as e:
            logger.error(f"❌ Schema initialization failed: {str(e)}")
            raise
    
    def ingest_save_file(self, file_path: Path, save_data: Dict[str, Any]) -> int:
        """
        Ingest a complete save file into the database
        Returns the save_file_id for reference
        """
        try:
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
            save_file_id = self._insert_save_file(metadata)
            
            # Insert related data
            self._insert_employees(save_file_id, save_data)
            self._insert_transactions(save_file_id, save_data)
            self._insert_inventory(save_file_id, save_data)
            self._insert_research(save_file_id, save_data)
            self._insert_features(save_file_id, save_data)
            self._insert_market_data(save_file_id, save_data)
            self._insert_office_data(save_file_id, save_data)
            
            logger.info(f"✅ Save file ingested: {file_path.name} (ID: {save_file_id})")
            return save_file_id
            
        except Exception as e:
            logger.error(f"❌ Error ingesting save file: {str(e)}")
            raise
    
    def _insert_save_file(self, metadata: Dict[str, Any]) -> int:
        """Insert main save file record"""
        sql = """
        INSERT INTO save_files (filename, game_date, file_size, company_name, 
                               game_state, balance, total_employees, game_version, raw_data)
        VALUES (%(filename)s, %(game_date)s, %(file_size)s, %(company_name)s,
                %(game_state)s, %(balance)s, %(total_employees)s, %(game_version)s, %(raw_data)s)
        ON CONFLICT (filename) DO UPDATE SET
            game_date = EXCLUDED.game_date,
            balance = EXCLUDED.balance,
            total_employees = EXCLUDED.total_employees,
            processed_at = CURRENT_TIMESTAMP,
            raw_data = EXCLUDED.raw_data
        RETURNING id;
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(sql, metadata)
            save_file_id = cursor.fetchone()[0]
            return save_file_id
    
    def _insert_employees(self, save_file_id: int, save_data: Dict[str, Any]):
        """Insert employee data"""
        employees = save_data.get('employeesOrder', [])
        if not employees:
            return
        
        # Clear existing employee data for this save file
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE save_file_id = %s", (save_file_id,))
        
        # Insert employee records
        employee_records = []
        for emp_id in employees:
            # Note: Employee details would need to be extracted from the full save data
            # This is a simplified version - we'd need to map employee IDs to their full data
            employee_records.append({
                'save_file_id': save_file_id,
                'employee_id': emp_id,
                'name': f"Employee_{emp_id}",  # Would extract from actual data
                'position': 'unknown',
                'salary': 0,
                'is_active': True
            })
        
        if employee_records:
            sql = """
            INSERT INTO employees (save_file_id, employee_id, name, position, salary, is_active)
            VALUES (%(save_file_id)s, %(employee_id)s, %(name)s, %(position)s, %(salary)s, %(is_active)s)
            """
            with self.connection.cursor() as cursor:
                cursor.executemany(sql, employee_records)
    
    def _insert_transactions(self, save_file_id: int, save_data: Dict[str, Any]):
        """Insert transaction data"""
        transactions = save_data.get('transactions', [])
        if not transactions:
            return
        
        # Clear existing transaction data for this save file
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM transactions WHERE save_file_id = %s", (save_file_id,))
        
        # Insert transaction records
        transaction_records = []
        for trans in transactions:
            transaction_records.append({
                'save_file_id': save_file_id,
                'transaction_date': trans.get('date', 'unknown'),
                'amount': trans.get('amount', 0),
                'transaction_type': trans.get('type', 'unknown'),
                'description': trans.get('reason', ''),
                'category': trans.get('category', 'general')
            })
        
        if transaction_records:
            sql = """
            INSERT INTO transactions (save_file_id, transaction_date, amount, 
                                    transaction_type, description, category)
            VALUES (%(save_file_id)s, %(transaction_date)s, %(amount)s, 
                    %(transaction_type)s, %(description)s, %(category)s)
            """
            with self.connection.cursor() as cursor:
                cursor.executemany(sql, transaction_records)
    
    def _insert_inventory(self, save_file_id: int, save_data: Dict[str, Any]):
        """Insert inventory data"""
        inventory = save_data.get('inventory', {})
        if not inventory:
            return
        
        # Clear existing inventory data for this save file
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM inventory WHERE save_file_id = %s", (save_file_id,))
        
        # Insert inventory records
        inventory_records = []
        for item_name, quantity in inventory.items():
            if isinstance(quantity, dict):
                # Handle complex inventory objects
                actual_quantity = quantity.get('amount', 0)
            else:
                actual_quantity = quantity
                
            inventory_records.append({
                'save_file_id': save_file_id,
                'item_name': item_name,
                'quantity': actual_quantity,
                'item_type': 'component',  # Would categorize based on item name
                'value_per_unit': 0  # Would calculate from market data
            })
        
        if inventory_records:
            sql = """
            INSERT INTO inventory (save_file_id, item_name, quantity, item_type, value_per_unit)
            VALUES (%(save_file_id)s, %(item_name)s, %(quantity)s, %(item_type)s, %(value_per_unit)s)
            """
            with self.connection.cursor() as cursor:
                cursor.executemany(sql, inventory_records)
    
    def _insert_research(self, save_file_id: int, save_data: Dict[str, Any]):
        """Insert research data"""
        research_points = save_data.get('researchPoints', 0)
        researched_items = save_data.get('researchedItems', [])
        
        # Clear existing research data for this save file
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM research WHERE save_file_id = %s", (save_file_id,))
        
        # Insert research records
        research_records = []
        for item in researched_items:
            research_records.append({
                'save_file_id': save_file_id,
                'research_item': item,
                'progress_points': research_points,
                'is_completed': True,
                'category': 'completed'
            })
        
        if research_records:
            sql = """
            INSERT INTO research (save_file_id, research_item, progress_points, is_completed, category)
            VALUES (%(save_file_id)s, %(research_item)s, %(progress_points)s, %(is_completed)s, %(category)s)
            """
            with self.connection.cursor() as cursor:
                cursor.executemany(sql, research_records)
    
    def _insert_features(self, save_file_id: int, save_data: Dict[str, Any]):
        """Insert feature data - placeholder for now"""
        # This would be expanded based on actual feature data structure
        pass
    
    def _insert_market_data(self, save_file_id: int, save_data: Dict[str, Any]):
        """Insert market data - placeholder for now"""
        # This would be expanded based on actual market data structure
        pass
    
    def _insert_office_data(self, save_file_id: int, save_data: Dict[str, Any]):
        """Insert office data"""
        office = save_data.get('office', {})
        if not office:
            return
        
        # Clear existing office data for this save file
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM office_data WHERE save_file_id = %s", (save_file_id,))
        
        workstations = office.get('workstations', [])
        occupied_count = sum(1 for ws in workstations if ws.get('employee'))
        
        office_record = {
            'save_file_id': save_file_id,
            'workstations_total': len(workstations),
            'workstations_occupied': occupied_count,
            'office_level': office.get('level', 1),
            'monthly_rent': office.get('rent', 0)
        }
        
        sql = """
        INSERT INTO office_data (save_file_id, workstations_total, workstations_occupied, 
                               office_level, monthly_rent)
        VALUES (%(save_file_id)s, %(workstations_total)s, %(workstations_occupied)s, 
                %(office_level)s, %(monthly_rent)s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql, office_record)
    
    def get_latest_save_file(self) -> Optional[Dict[str, Any]]:
        """Get the most recent save file data"""
        sql = """
        SELECT * FROM save_files 
        ORDER BY real_timestamp DESC 
        LIMIT 1
        """
        
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_trend_data(self, metric_name: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get trend data for a specific metric"""
        sql = """
        SELECT game_date, real_timestamp, %s as metric_value
        FROM save_files 
        WHERE real_timestamp >= NOW() - INTERVAL '%s days'
        ORDER BY real_timestamp ASC
        """
        
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(sql, (metric_name, days_back))
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("📊 Database connection closed")


# Database configuration
DEFAULT_DB_CONFIG = {
    'host': 'localhost',
    'database': 'startup_strategy',
    'user': 'postgres',
    'password': 'your_password',
    'port': '5432'
}