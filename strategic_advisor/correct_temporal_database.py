#!/usr/bin/env python3
"""
Corrected Temporal Database - Based on Actual Game Save Schema
Completely rebuild database to match the real game structure
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class CorrectTemporalGameDatabase:
    """Temporal database that actually follows the game save file schema"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = self._setup_logging()
        
        # Delete existing database and start fresh
        db_file = Path(db_path)
        if db_file.exists():
            db_file.unlink()
            self.logger.info(f"Deleted existing database: {db_path}")
        
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        
        self._create_schema()
        self.logger.info(f"Created new database with correct schema: {db_path}")
    
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(self.__class__.__name__)
    
    def _create_schema(self):
        """Create database schema that matches the actual game save file structure"""
        
        cursor = self.connection.cursor()
        
        # Core save files table
        cursor.execute("""
            CREATE TABLE save_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                
                -- Core game state (matches schema exactly)
                date TEXT,
                started TEXT,
                gameover BOOLEAN,
                state INTEGER,
                paused BOOLEAN,
                last_version TEXT,
                balance REAL,
                last_price_per_hour INTEGER,
                xp REAL,
                research_points INTEGER,
                amount_of_available_research_items INTEGER,
                user_loss_enabled BOOLEAN,
                beta_version_at_start INTEGER,
                company_name TEXT,
                save_game_name TEXT,
                file_name TEXT,
                selected_floor INTEGER,
                selected_building_name TEXT,
                max_contract_hours INTEGER,
                contracts_completed INTEGER,
                needs_new_loan BOOLEAN,
                auto_start_time_machine BOOLEAN,
                last_saved TEXT,
                
                -- Our temporal tracking
                real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_modified_time DATETIME,
                ingestion_order INTEGER,
                file_size INTEGER,
                raw_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions table (exactly matching schema)
        cursor.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                transaction_id TEXT NOT NULL,
                day INTEGER,
                hour INTEGER,
                minute INTEGER,
                amount REAL,
                label TEXT,
                balance REAL,
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(save_file_id, transaction_id)
            )
        """)
        
        # Candidates table (the missing piece!)
        cursor.execute("""
            CREATE TABLE candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                candidate_id TEXT NOT NULL,
                name TEXT,
                original_name TEXT,
                employee_type_name TEXT,
                salary INTEGER,
                competitor_product_id TEXT,
                avatar TEXT,
                progress INTEGER,
                level TEXT,
                speed INTEGER,
                age INTEGER,
                max_speed INTEGER,
                animation_speed REAL,
                required_worker INTEGER,
                mood INTEGER,
                overtime_minutes INTEGER,
                gender TEXT,
                hours_left INTEGER,
                call_in_sick_days_left INTEGER,
                sick_hours_left INTEGER,
                idle_minutes INTEGER,
                minutes_till_next_emotion INTEGER,
                creation_time INTEGER,
                superstar BOOLEAN,
                research_demands BOOLEAN,
                research_salary BOOLEAN,
                components TEXT, -- JSON array
                employees TEXT, -- JSON array  
                leads TEXT, -- JSON array
                lead_filters TEXT, -- JSON object
                task TEXT, -- JSON object
                demands TEXT, -- JSON array
                schedule TEXT, -- JSON object
                negotiation TEXT, -- JSON object
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(save_file_id, candidate_id)
            )
        """)
        
        # Products table (major missing section)
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                product_id TEXT NOT NULL,
                name TEXT,
                age_in_days INTEGER,
                hosting_allocation INTEGER,
                framework_name TEXT,
                resolved_tickets INTEGER,
                total_tickets INTEGER,
                next_ddos_attack INTEGER,
                logo_path TEXT,
                product_type_name TEXT,
                position INTEGER,
                owned_percentage INTEGER,
                disable_user_loss BOOLEAN,
                last_ddos_attack INTEGER,
                stats TEXT, -- JSON object
                servers TEXT, -- JSON object
                campaigns TEXT, -- JSON array
                investments TEXT, -- JSON array
                mergers TEXT, -- JSON array
                support_teams TEXT, -- JSON array
                tickets TEXT, -- JSON array
                ticket_resolve_times TEXT, -- JSON array
                ads TEXT, -- JSON array
                investor TEXT, -- JSON object
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(save_file_id, product_id)
            )
        """)
        
        # Feature instances table
        cursor.execute("""
            CREATE TABLE feature_instances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                feature_id TEXT NOT NULL,
                feature_name TEXT,
                activated BOOLEAN,
                price_per_month INTEGER,
                dissatisfaction INTEGER,
                product_id TEXT,
                efficiency TEXT, -- JSON object
                quality TEXT, -- JSON object
                premium_features TEXT, -- JSON array
                requirements TEXT, -- JSON object
                time_slots TEXT, -- JSON array
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(save_file_id, feature_id)
            )
        """)
        
        # Market values table (corrected)
        cursor.execute("""
            CREATE TABLE market_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                component_name TEXT NOT NULL,
                base_price INTEGER,
                price_change REAL,
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(save_file_id, component_name)
            )
        """)
        
        # Jeets table (social media)
        cursor.execute("""
            CREATE TABLE jeets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                jeet_id TEXT NOT NULL,
                gender TEXT,
                jeet_name TEXT,
                handle TEXT,
                avatar TEXT,
                text TEXT,
                day INTEGER,
                read BOOLEAN,
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(jeet_id, day)
            )
        """)
        
        # Competitor products table
        cursor.execute("""
            CREATE TABLE competitor_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                competitor_id TEXT NOT NULL,
                name TEXT,
                logo_color_degree INTEGER,
                logo_path TEXT,
                users REAL,
                product_type_name TEXT,
                controlled BOOLEAN,
                stock_volume INTEGER,
                owned_stocks INTEGER,
                price_expectations REAL,
                growth INTEGER,
                viral_days_left INTEGER,
                version REAL,
                history TEXT, -- JSON object
                deal_results TEXT, -- JSON array
                stock_transactions TEXT, -- JSON array
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(save_file_id, competitor_id)
            )
        """)
        
        # Inventory table  
        cursor.execute("""
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                component_name TEXT NOT NULL,
                quantity INTEGER,
                stats TEXT, -- JSON object for daily stats
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id),
                UNIQUE(save_file_id, component_name)
            )
        """)
        
        # Loans table
        cursor.execute("""
            CREATE TABLE loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_file_id INTEGER NOT NULL,
                provider TEXT,
                days_left INTEGER,
                amount_left INTEGER,
                active BOOLEAN,
                captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (save_file_id) REFERENCES save_files(id)
            )
        """)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX idx_save_files_real_timestamp ON save_files(real_timestamp)",
            "CREATE INDEX idx_save_files_company_name ON save_files(company_name)",
            "CREATE INDEX idx_transactions_day ON transactions(day)",
            "CREATE INDEX idx_candidates_employee_type ON candidates(employee_type_name)",
            "CREATE INDEX idx_products_name ON products(name)",
            "CREATE INDEX idx_jeets_day ON jeets(day)",
            "CREATE INDEX idx_market_values_component ON market_values(component_name)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.connection.commit()
        self.logger.info("Database schema created successfully")
    
    def ingest_save_file(self, file_path: Path, save_data: Dict[str, Any]) -> int:
        """Ingest a complete save file following the actual schema structure"""
        
        cursor = self.connection.cursor()
        
        try:
            # Insert main save file record
            cursor.execute("""
                INSERT INTO save_files (
                    filename, date, started, gameover, state, paused, last_version,
                    balance, last_price_per_hour, xp, research_points, 
                    amount_of_available_research_items, user_loss_enabled,
                    beta_version_at_start, company_name, save_game_name, file_name,
                    selected_floor, selected_building_name, max_contract_hours,
                    contracts_completed, needs_new_loan, auto_start_time_machine,
                    last_saved, file_size, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_path.name,
                save_data.get('date'),
                save_data.get('started'),
                save_data.get('gameover'),
                save_data.get('state'),
                save_data.get('paused'),
                save_data.get('lastVersion'),
                save_data.get('balance'),
                save_data.get('lastPricePerHour'),
                save_data.get('xp'),
                save_data.get('researchPoints'),
                save_data.get('amountOfAvailableResearchItems'),
                save_data.get('userLossEnabled'),
                save_data.get('betaVersionAtStart'),
                save_data.get('companyName'),
                save_data.get('saveGameName'),
                save_data.get('fileName'),
                save_data.get('selectedFloor'),
                save_data.get('selectedBuildingName'),
                save_data.get('maxContractHours'),
                save_data.get('contractsCompleted'),
                save_data.get('needsNewLoan'),
                save_data.get('autoStartTimeMachine'),
                save_data.get('lastSaved'),
                file_path.stat().st_size,
                json.dumps(save_data, default=str)
            ))
            
            save_file_id = cursor.lastrowid
            
            # Insert transactions
            for transaction in save_data.get('transactions', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO transactions (
                        save_file_id, transaction_id, day, hour, minute, amount, label, balance
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    transaction['id'],
                    transaction.get('day'),
                    transaction.get('hour'),
                    transaction.get('minute'),
                    transaction.get('amount'),
                    transaction.get('label'),
                    transaction.get('balance')
                ))
            
            # Insert candidates (the missing piece!)
            for candidate in save_data.get('candidates', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO candidates (
                        save_file_id, candidate_id, name, original_name, employee_type_name,
                        salary, competitor_product_id, avatar, progress, level, speed, age,
                        max_speed, animation_speed, required_worker, mood, overtime_minutes,
                        gender, hours_left, call_in_sick_days_left, sick_hours_left,
                        idle_minutes, minutes_till_next_emotion, creation_time, superstar,
                        research_demands, research_salary, components, employees, leads,
                        lead_filters, task, demands, schedule, negotiation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    candidate['id'],
                    candidate.get('name'),
                    candidate.get('originalName'),
                    candidate.get('employeeTypeName'),
                    candidate.get('salary'),
                    candidate.get('competitorProductId'),
                    candidate.get('avatar'),
                    candidate.get('progress'),
                    candidate.get('level'),
                    candidate.get('speed'),
                    candidate.get('age'),
                    candidate.get('maxSpeed'),
                    candidate.get('animationSpeed'),
                    candidate.get('requiredWer'),
                    candidate.get('mood'),
                    candidate.get('overtimeMinutes'),
                    candidate.get('gender'),
                    candidate.get('hoursLeft'),
                    candidate.get('callInSickDaysLeft'),
                    candidate.get('sickHoursLeft'),
                    candidate.get('idleMinutes'),
                    candidate.get('minutesTillNextEmotion'),
                    candidate.get('creationTime'),
                    candidate.get('superstar'),
                    candidate.get('researchDemands'),
                    candidate.get('researchSalary'),
                    json.dumps(candidate.get('components', [])),
                    json.dumps(candidate.get('employees', [])),
                    json.dumps(candidate.get('leads', [])),
                    json.dumps(candidate.get('leadFilters', {})),
                    json.dumps(candidate.get('task', {})),
                    json.dumps(candidate.get('demands', [])),
                    json.dumps(candidate.get('schedule', {})),
                    json.dumps(candidate.get('negotiation', {}))
                ))
            
            # Insert products
            for product in save_data.get('products', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO products (
                        save_file_id, product_id, name, age_in_days, hosting_allocation,
                        framework_name, resolved_tickets, total_tickets, next_ddos_attack,
                        logo_path, product_type_name, position, owned_percentage,
                        disable_user_loss, last_ddos_attack, stats, servers, campaigns,
                        investments, mergers, support_teams, tickets, ticket_resolve_times,
                        ads, investor
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    product['id'],
                    product.get('name'),
                    product.get('ageInDays'),
                    product.get('hostingAllocation'),
                    product.get('frameworkName'),
                    product.get('resolvedTickets'),
                    product.get('totalTickets'),
                    product.get('nextDdosAttack'),
                    product.get('logoPath'),
                    product.get('productTypeName'),
                    product.get('position'),
                    product.get('ownedPercentage'),
                    product.get('disableUserLoss'),
                    product.get('lastDdosAttack'),
                    json.dumps(product.get('stats', {})),
                    json.dumps(product.get('servers', {})),
                    json.dumps(product.get('campaigns', [])),
                    json.dumps(product.get('investments', [])),
                    json.dumps(product.get('mergers', [])),
                    json.dumps(product.get('supportTeams', [])),
                    json.dumps(product.get('tickets', [])),
                    json.dumps(product.get('ticketResolveTimes', [])),
                    json.dumps(product.get('ads', [])),
                    json.dumps(product.get('investor', {}))
                ))
            
            # Insert market values
            market_values = save_data.get('marketValues', {})
            for component_name, market_data in market_values.items():
                cursor.execute("""
                    INSERT OR IGNORE INTO market_values (
                        save_file_id, component_name, base_price, price_change
                    ) VALUES (?, ?, ?, ?)
                """, (
                    save_file_id,
                    component_name,
                    market_data.get('basePrice'),
                    market_data.get('change')
                ))
            
            # Insert jeets
            for jeet in save_data.get('jeets', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO jeets (
                        save_file_id, jeet_id, gender, jeet_name, handle, avatar, text, day, read
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    jeet['id'],
                    jeet.get('gender'),
                    jeet.get('name'),
                    jeet.get('handle'),
                    jeet.get('avatar'),
                    jeet.get('text'),
                    jeet.get('day'),
                    jeet.get('read')
                ))
            
            # Insert feature instances
            for feature in save_data.get('featureInstances', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO feature_instances (
                        save_file_id, feature_id, feature_name, activated, price_per_month,
                        dissatisfaction, product_id, efficiency, quality, premium_features,
                        requirements, time_slots
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    feature['id'],
                    feature.get('featureName'),
                    feature.get('activated'),
                    feature.get('pricePerMonth'),
                    feature.get('dissatisfaction'),
                    feature.get('productId'),
                    json.dumps(feature.get('efficiency', {})),
                    json.dumps(feature.get('quality', {})),
                    json.dumps(feature.get('premiumFeatures', [])),
                    json.dumps(feature.get('requirements', {})),
                    json.dumps(feature.get('timeSlots', []))
                ))
            
            # Insert inventory
            inventory = save_data.get('inventory', {})
            stats_data = inventory.get('stats', {})
            for component_name, value in inventory.items():
                if component_name != 'stats' and isinstance(value, int):
                    cursor.execute("""
                        INSERT OR IGNORE INTO inventory (
                            save_file_id, component_name, quantity, stats
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        save_file_id,
                        component_name,
                        value,
                        json.dumps(stats_data.get(str(component_name), {}))
                    ))
            
            # Insert loans
            for loan in save_data.get('loans', []):
                cursor.execute("""
                    INSERT INTO loans (
                        save_file_id, provider, days_left, amount_left, active
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    loan.get('provider'),
                    loan.get('daysLeft'),
                    loan.get('amountLeft'),
                    loan.get('active')
                ))
            
            # Insert competitor products
            for competitor in save_data.get('competitorProducts', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO competitor_products (
                        save_file_id, competitor_id, name, logo_color_degree, logo_path,
                        users, product_type_name, controlled, stock_volume, owned_stocks,
                        price_expectations, growth, viral_days_left, version, history,
                        deal_results, stock_transactions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_file_id,
                    competitor['id'],
                    competitor.get('name'),
                    competitor.get('logoColorDegree'),
                    competitor.get('logoPath'),
                    competitor.get('users'),
                    competitor.get('productTypeName'),
                    competitor.get('controlled'),
                    competitor.get('stockVolume'),
                    competitor.get('ownedStocks'),
                    competitor.get('priceExpectations'),
                    competitor.get('growth'),
                    competitor.get('viralDaysLeft'),
                    competitor.get('version'),
                    json.dumps(competitor.get('history', {})),
                    json.dumps(competitor.get('dealResults', [])),
                    json.dumps(competitor.get('stockTransactions', []))
                ))
            
            self.connection.commit()
            self.logger.info(f"Successfully ingested save file: {file_path.name} (ID: {save_file_id})")
            return save_file_id
            
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Failed to ingest save file {file_path.name}: {str(e)}")
            raise
    
    def get_table_counts(self) -> Dict[str, int]:
        """Get record counts for all tables"""
        cursor = self.connection.cursor()
        
        tables = [
            'save_files', 'transactions', 'candidates', 'products', 
            'feature_instances', 'market_values', 'jeets', 
            'competitor_products', 'inventory', 'loans'
        ]
        
        counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        return counts
    
    def close(self):
        """Close database connection"""
        self.connection.close()

if __name__ == "__main__":
    print("🚀 Creating CORRECT Temporal Database")
    print("="*60)
    
    # Create new database with correct schema
    db = CorrectTemporalGameDatabase("momentum_ai_correct.db")
    
    print("✅ Database created with correct schema!")
    print("📊 Ready to ingest game save files properly")
    
    db.close()