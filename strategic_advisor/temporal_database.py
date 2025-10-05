"""
Strategic Advisor - Temporal Database Implementation
Raw storage with comprehensive temporal tracking
"""

import sqlite3
import json
import logging
import threading
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime

from .logger_config import setup_logging, SUCCESS_MESSAGES, ERROR_MESSAGES

# Setup safe logging
setup_logging()
logger = logging.getLogger(__name__)

class TemporalGameDatabase:
    """
    Temporal database for raw game save storage with comprehensive time tracking
    Designed for historical analysis and trend tracking
    """
    
    def __init__(self, db_path: str = "strategic_advisor/temporal_game_data.db"):
        self.db_path = db_path
        self._local = threading.local()
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema
        self._initialize_temporal_schema()
        
        logger.info(SUCCESS_MESSAGES['database_init'].format(self.db_path))
    
    def get_connection(self, read_only: bool = False):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection'):
            if read_only:
                self._local.connection = sqlite3.connect(
                    f"file:{self.db_path}?mode=ro", 
                    uri=True,
                    check_same_thread=False
                )
            else:
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
    
    def _initialize_temporal_schema(self):
        """Create temporal database tables"""
        
        schema_sql = """
        -- Main save file metadata with temporal tracking
        CREATE TABLE IF NOT EXISTS save_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            
            -- Game temporal data
            game_date TEXT,                  -- JSON: date
            game_started TEXT,               -- JSON: started
            game_day INTEGER,                -- Extracted day number
            last_saved TEXT,                 -- JSON: lastSaved
            
            -- Real-world temporal tracking
            real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_modified_time DATETIME,
            ingestion_order INTEGER,
            
            -- Game metadata
            game_id TEXT,                    -- JSON: id
            company_name TEXT,               -- JSON: companyName
            save_game_name TEXT,             -- JSON: saveGameName
            file_name TEXT,                  -- JSON: fileName
            last_version TEXT,               -- JSON: lastVersion
            
            -- Game state
            gameover BOOLEAN,                -- JSON: gameover
            state INTEGER,                   -- JSON: state
            paused BOOLEAN,                  -- JSON: paused
            user_loss_enabled BOOLEAN,       -- JSON: userLossEnabled
            beta_version_at_start INTEGER,   -- JSON: betaVersionAtStart
            
            -- Financial data
            balance REAL,                    -- JSON: balance
            last_price_per_hour INTEGER,     -- JSON: lastPricePerHour
            
            -- Game progress
            xp REAL,                         -- JSON: xp
            research_points INTEGER,         -- JSON: researchPoints
            amount_of_available_research_items INTEGER,
            
            -- Office/Building
            selected_floor INTEGER,          -- JSON: selectedFloor
            selected_building_name TEXT,     -- JSON: selectedBuildingName
            
            -- Contracts
            max_contract_hours INTEGER,      -- JSON: maxContractHours
            contracts_completed INTEGER,     -- JSON: contractsCompleted
            
            -- Loans
            needs_new_loan BOOLEAN,          -- JSON: needsNewLoan
            
            -- Settings
            auto_start_time_machine BOOLEAN, -- JSON: autoStartTimeMachine
            
            -- Raw storage
            file_size INTEGER,
            raw_json TEXT,
            
            -- Temporal tracking
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Employee references with temporal tracking
        CREATE TABLE IF NOT EXISTS employee_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            employee_id TEXT,
            employee_order INTEGER,
            
            -- Temporal tracking
            captured_at DATETIME,
            game_date TEXT,
            game_day INTEGER,
            
            UNIQUE(save_file_id, employee_id)
        );
        
        -- All employee data with temporal tracking
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            employee_id TEXT,
            name TEXT,
            original_name TEXT,
            employee_type_name TEXT,
            salary INTEGER,
            competitor_product_id TEXT,
            avatar TEXT,
            progress INTEGER,
            level TEXT,
            speed REAL,
            age INTEGER,
            max_speed INTEGER,
            animation_speed REAL,
            required_worker INTEGER,
            mood REAL,
            overtime_minutes INTEGER,
            components TEXT,
            gender TEXT,
            hours_left INTEGER,
            call_in_sick_days_left INTEGER,
            sick_hours_left INTEGER,
            idle_minutes INTEGER,
            minutes_till_next_emotion INTEGER,
            creation_time INTEGER,
            schedule TEXT,
            superstar BOOLEAN,
            leads TEXT,
            lead_filters TEXT,
            task TEXT,
            demands TEXT,
            research_demands BOOLEAN,
            research_salary BOOLEAN,
            negotiation TEXT,
            hired DATETIME,
            active_queue_index INTEGER,
            last_tab TEXT,
            last_emotion_name TEXT,
            last_bonus_day INTEGER,
            is_training BOOLEAN,
            last_day INTEGER,
            last_send_home_length INTEGER,
            send_home_days_left INTEGER,
            last_competitor_job_offer INTEGER,
            
            -- Employee status tracking
            employee_status TEXT,
            source_array TEXT,
            
            -- Temporal tracking
            captured_at DATETIME,
            game_date TEXT,
            game_day INTEGER,
            
            UNIQUE(save_file_id, employee_id, employee_status)
        );
        
        -- Transactions with game time and capture time
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            transaction_id TEXT,
            day INTEGER,
            hour INTEGER,
            minute INTEGER,
            amount REAL,
            label TEXT,
            balance REAL,
            
            -- Temporal tracking
            captured_at DATETIME,
            game_date TEXT,
            transaction_game_time TEXT,
            
            UNIQUE(save_file_id, transaction_id)
        );
        
        -- Jeets with game time and deduplication
        CREATE TABLE IF NOT EXISTS jeets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            jeet_id TEXT,
            gender TEXT,
            jeet_name TEXT,
            handle TEXT,
            avatar TEXT,
            text TEXT,
            day INTEGER,
            read BOOLEAN,
            
            -- Temporal tracking
            captured_at DATETIME,
            game_date TEXT,
            first_seen_game_day INTEGER,
            
            UNIQUE(jeet_id, day)
        );
        
        -- Market Values with temporal tracking (perfect for price trends!)
        CREATE TABLE IF NOT EXISTS market_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            save_file_id INTEGER REFERENCES save_files(id),
            component_name TEXT,
            base_price INTEGER,
            price_change REAL,
            
            -- Temporal tracking
            captured_at DATETIME,
            game_date TEXT,
            game_day INTEGER,
            
            UNIQUE(save_file_id, component_name)
        );
        
        -- Performance indexes with temporal considerations
        CREATE INDEX IF NOT EXISTS idx_save_files_game_date ON save_files(game_date);
        CREATE INDEX IF NOT EXISTS idx_save_files_game_day ON save_files(game_day);
        CREATE INDEX IF NOT EXISTS idx_save_files_real_timestamp ON save_files(real_timestamp);
        CREATE INDEX IF NOT EXISTS idx_save_files_ingestion_order ON save_files(ingestion_order);
        
        -- Temporal indexes for major tables
        CREATE INDEX IF NOT EXISTS idx_employees_captured_at ON employees(captured_at);
        CREATE INDEX IF NOT EXISTS idx_employees_game_day ON employees(game_day);
        CREATE INDEX IF NOT EXISTS idx_transactions_captured_at ON transactions(captured_at);
        CREATE INDEX IF NOT EXISTS idx_transactions_game_day ON transactions(day);
        CREATE INDEX IF NOT EXISTS idx_jeets_captured_at ON jeets(captured_at);
        CREATE INDEX IF NOT EXISTS idx_jeets_game_day ON jeets(day);
        CREATE INDEX IF NOT EXISTS idx_market_values_captured_at ON market_values(captured_at);
        
        -- Foreign key indexes
        CREATE INDEX IF NOT EXISTS idx_employees_save_file ON employees(save_file_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_save_file ON transactions(save_file_id);
        
        -- Natural deduplication indexes
        CREATE INDEX IF NOT EXISTS idx_jeets_natural_key ON jeets(jeet_id, day);
        CREATE INDEX IF NOT EXISTS idx_transactions_natural_key ON transactions(transaction_id);
        CREATE INDEX IF NOT EXISTS idx_employees_natural_key ON employees(employee_id, employee_status);
        """
        
        try:
            with self.get_write_connection() as conn:
                conn.executescript(schema_sql)
            logger.info("Temporal database schema initialized")
        except Exception as e:
            logger.error(f"Temporal schema initialization failed: {str(e)}")
            raise
    
    def ingest_save_file(self, file_path: Path, save_data: Dict[str, Any]) -> int:
        """
        Ingest a complete save file with temporal tracking
        Returns the save_file_id for reference
        """
        try:
            with self.get_write_connection() as conn:
                # Extract game day from date
                game_day = self._extract_game_day(save_data.get('date', ''))
                
                # Extract metadata with temporal info
                metadata = {
                    'filename': file_path.name,
                    'game_date': save_data.get('date', ''),
                    'game_started': save_data.get('started', ''),
                    'game_day': game_day,
                    'last_saved': save_data.get('lastSaved', ''),
                    'file_modified_time': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'game_id': save_data.get('id', ''),
                    'company_name': save_data.get('companyName', ''),
                    'save_game_name': save_data.get('saveGameName', ''),
                    'file_name': save_data.get('fileName', ''),
                    'last_version': save_data.get('lastVersion', ''),
                    'gameover': save_data.get('gameover', False),
                    'state': save_data.get('state', 0),
                    'paused': save_data.get('paused', False),
                    'user_loss_enabled': save_data.get('userLossEnabled', True),
                    'beta_version_at_start': save_data.get('betaVersionAtStart', 0),
                    'balance': save_data.get('balance', 0),
                    'last_price_per_hour': save_data.get('lastPricePerHour', 0),
                    'xp': save_data.get('xp', 0),
                    'research_points': save_data.get('researchPoints', 0),
                    'amount_of_available_research_items': save_data.get('amountOfAvailableResearchItems', 0),
                    'selected_floor': save_data.get('selectedFloor', 0),
                    'selected_building_name': save_data.get('selectedBuildingName', ''),
                    'max_contract_hours': save_data.get('maxContractHours', 0),
                    'contracts_completed': save_data.get('contractsCompleted', 0),
                    'needs_new_loan': save_data.get('needsNewLoan', False),
                    'auto_start_time_machine': save_data.get('autoStartTimeMachine', False),
                    'file_size': file_path.stat().st_size,
                    'raw_json': json.dumps(save_data)
                }
                
                # Insert save file record
                cursor = conn.execute("""
                    INSERT INTO save_files (
                        filename, game_date, game_started, game_day, last_saved,
                        file_modified_time, game_id, company_name, save_game_name, file_name,
                        last_version, gameover, state, paused, user_loss_enabled,
                        beta_version_at_start, balance, last_price_per_hour, xp,
                        research_points, amount_of_available_research_items,
                        selected_floor, selected_building_name, max_contract_hours,
                        contracts_completed, needs_new_loan, auto_start_time_machine,
                        file_size, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata['filename'], metadata['game_date'], metadata['game_started'],
                    metadata['game_day'], metadata['last_saved'], metadata['file_modified_time'],
                    metadata['game_id'], metadata['company_name'], metadata['save_game_name'],
                    metadata['file_name'], metadata['last_version'], metadata['gameover'],
                    metadata['state'], metadata['paused'], metadata['user_loss_enabled'],
                    metadata['beta_version_at_start'], metadata['balance'], metadata['last_price_per_hour'],
                    metadata['xp'], metadata['research_points'], metadata['amount_of_available_research_items'],
                    metadata['selected_floor'], metadata['selected_building_name'], metadata['max_contract_hours'],
                    metadata['contracts_completed'], metadata['needs_new_loan'], metadata['auto_start_time_machine'],
                    metadata['file_size'], metadata['raw_json']
                ))
                
                save_file_id = cursor.lastrowid
                
                if save_file_id is None:
                    raise ValueError("Failed to get save file ID after insertion")
                
                # Ingest temporal data
                self._ingest_transactions(conn, save_file_id, save_data, metadata)
                self._ingest_jeets(conn, save_file_id, save_data, metadata)
                self._ingest_market_values(conn, save_file_id, save_data, metadata)
                
                logger.info(f"Save file ingested with temporal tracking: {file_path.name} (ID: {save_file_id})")
                
                return save_file_id
                
        except Exception as e:
            logger.error(f"Save file ingestion failed: {str(e)}")
            raise
    
    def _extract_game_day(self, game_date: str) -> int:
        """Extract game day number from date string"""
        try:
            if game_date:
                # Parse ISO date and calculate days from start
                from datetime import datetime as dt
                date_obj = dt.fromisoformat(game_date.replace('Z', '+00:00'))
                # Simple day extraction (could be improved with game's start date)
                return int(date_obj.timestamp() // 86400)  # Days since epoch
        except:
            pass
        return 0
    
    def _ingest_transactions(self, conn, save_file_id: int, save_data: Dict, metadata: Dict):
        """Ingest transactions with temporal tracking and deduplication"""
        transactions = save_data.get('transactions', [])
        
        for transaction in transactions:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO transactions (
                        save_file_id, transaction_id, day, hour, minute, amount, label, balance,
                        captured_at, game_date, transaction_game_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    transaction.get('id', ''),
                    transaction.get('day', 0),
                    transaction.get('hour', 0),
                    transaction.get('minute', 0),
                    transaction.get('amount', 0),
                    transaction.get('label', ''),
                    transaction.get('balance', 0),
                    datetime.now(),
                    metadata['game_date'],
                    f"Day {transaction.get('day', 0)} {transaction.get('hour', 0):02d}:{transaction.get('minute', 0):02d}"
                ))
            except Exception as e:
                logger.warning(f"Transaction ingestion failed: {str(e)}")
    
    def _ingest_jeets(self, conn, save_file_id: int, save_data: Dict, metadata: Dict):
        """Ingest jeets with temporal tracking and deduplication"""
        jeets = save_data.get('jeets', [])
        
        for jeet in jeets:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO jeets (
                        save_file_id, jeet_id, gender, jeet_name, handle, avatar, text, day, read,
                        captured_at, game_date, first_seen_game_day
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    jeet.get('id', ''),
                    jeet.get('gender', ''),
                    jeet.get('name', ''),
                    jeet.get('handle', ''),
                    jeet.get('avatar', ''),
                    jeet.get('text', ''),
                    jeet.get('day', 0),
                    jeet.get('read', False),
                    datetime.now(),
                    metadata['game_date'],
                    metadata['game_day']
                ))
            except Exception as e:
                logger.warning(f"Jeet ingestion failed: {str(e)}")
    
    def _ingest_market_values(self, conn, save_file_id: int, save_data: Dict, metadata: Dict):
        """Ingest market values with temporal tracking"""
        market_values = save_data.get('marketValues', {})
        
        for component_name, component_data in market_values.items():
            try:
                if isinstance(component_data, dict):
                    conn.execute("""
                        INSERT OR REPLACE INTO market_values (
                            save_file_id, component_name, base_price, price_change,
                            captured_at, game_date, game_day
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        save_file_id,
                        component_name,
                        component_data.get('basePrice', 0),
                        component_data.get('change', 0),
                        datetime.now(),
                        metadata['game_date'],
                        metadata['game_day']
                    ))
            except Exception as e:
                logger.warning(f"Market value ingestion failed for {component_name}: {str(e)}")
    
    def get_latest_save_file(self) -> Optional[Dict]:
        """Get the most recent save file metadata"""
        try:
            with self.get_read_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM save_files 
                    ORDER BY real_timestamp DESC 
                    LIMIT 1
                """)
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get latest save file: {str(e)}")
            return None
    
    def execute_read_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a read query and return results"""
        try:
            with self.get_read_connection() as conn:
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Read query failed: {str(e)}")
            return []