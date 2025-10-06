#!/usr/bin/env python3
"""
Temporal Raw Storage Schema
Simple timestamp-based tracking for all data entries
"""

TEMPORAL_SCHEMA_SQL = """
-- Main save file metadata with temporal tracking
CREATE TABLE IF NOT EXISTS save_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    
    -- Game temporal data
    game_date TEXT,                  -- JSON: date (game's current time)
    game_started TEXT,               -- JSON: started (when game began)
    game_day INTEGER,                -- Extracted day number from game_date
    last_saved TEXT,                 -- JSON: lastSaved (game's last save time)
    
    -- Real-world temporal tracking
    real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- When we captured this data
    file_modified_time DATETIME,     -- File system modification time
    ingestion_order INTEGER,         -- Sequential order of processing
    
    -- Game metadata (from JSON schema)
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
    amount_of_available_research_items INTEGER, -- JSON: amountOfAvailableResearchItems
    
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
    raw_json TEXT,                   -- Complete JSON backup
    
    -- Temporal tracking
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Employee references with temporal tracking
CREATE TABLE IF NOT EXISTS employee_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    employee_id TEXT,                -- UUID from employeesOrder
    employee_order INTEGER,          -- Position in array
    
    -- Temporal tracking
    captured_at DATETIME,            -- From save_files.real_timestamp
    game_date TEXT,                  -- From save_files.game_date
    game_day INTEGER,                -- From save_files.game_day
    
    UNIQUE(save_file_id, employee_id)
);

-- All employee data with temporal tracking
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    employee_id TEXT,                -- UUID
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
    components TEXT,                 -- JSON array as text
    gender TEXT,
    hours_left INTEGER,
    call_in_sick_days_left INTEGER,
    sick_hours_left INTEGER,
    idle_minutes INTEGER,
    minutes_till_next_emotion INTEGER,
    creation_time INTEGER,           -- Game's internal creation time
    schedule TEXT,                   -- JSON object as text
    superstar BOOLEAN,
    leads TEXT,                      -- JSON array as text
    lead_filters TEXT,               -- JSON object as text
    task TEXT,                       -- JSON object as text
    demands TEXT,                    -- JSON array as text
    research_demands BOOLEAN,
    research_salary BOOLEAN,
    negotiation TEXT,                -- JSON object as text
    hired DATETIME,                  -- Game's hire date
    active_queue_index INTEGER,
    last_tab TEXT,
    last_emotion_name TEXT,
    last_bonus_day INTEGER,
    is_training BOOLEAN,
    last_day INTEGER,
    
    -- Additional fields for resigned employees
    last_send_home_length INTEGER,
    send_home_days_left INTEGER,
    last_competitor_job_offer INTEGER,
    
    -- Employee status tracking
    employee_status TEXT,            -- 'active', 'fired', 'resigned'
    source_array TEXT,               -- 'employeesOrder', 'firedEmployees', 'resignedEmployees'
    
    -- Temporal tracking
    captured_at DATETIME,            -- When we captured this record
    game_date TEXT,                  -- Game date when captured
    game_day INTEGER,                -- Game day when captured
    
    UNIQUE(save_file_id, employee_id, employee_status)  -- Allow same employee in different states
);

-- Candidates with temporal tracking
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    candidate_id TEXT,               -- UUID
    name TEXT,
    original_name TEXT,
    employee_type_name TEXT,
    salary INTEGER,
    competitor_product_id TEXT,
    avatar TEXT,
    progress INTEGER,
    level TEXT,
    employees TEXT,                  -- Empty array as JSON text
    speed INTEGER,
    age INTEGER,
    max_speed INTEGER,
    animation_speed REAL,
    required_worker INTEGER,
    mood INTEGER,
    overtime_minutes INTEGER,
    components TEXT,                 -- JSON array as text
    gender TEXT,
    hours_left INTEGER,
    call_in_sick_days_left INTEGER,
    sick_hours_left INTEGER,
    idle_minutes INTEGER,
    minutes_till_next_emotion INTEGER,
    creation_time INTEGER,
    schedule TEXT,                   -- JSON object as text
    superstar BOOLEAN,
    leads TEXT,                      -- JSON array as text
    lead_filters TEXT,               -- JSON object as text
    task TEXT,                       -- JSON object as text
    demands TEXT,                    -- JSON array as text
    research_demands BOOLEAN,
    research_salary BOOLEAN,
    
    -- Temporal tracking
    captured_at DATETIME,            -- When we captured this record
    game_date TEXT,                  -- Game date when captured
    game_day INTEGER,                -- Game day when captured
    
    UNIQUE(save_file_id, candidate_id)
);

-- Transactions with game time and capture time
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    transaction_id TEXT,             -- UUID
    day INTEGER,                     -- Game day of transaction
    hour INTEGER,                    -- Game hour of transaction
    minute INTEGER,                  -- Game minute of transaction
    amount REAL,
    label TEXT,
    balance REAL,
    
    -- Temporal tracking
    captured_at DATETIME,            -- When we captured this record
    game_date TEXT,                  -- Game date when captured
    transaction_game_time TEXT,      -- Constructed from day/hour/minute
    
    UNIQUE(save_file_id, transaction_id)  -- Natural deduplication by UUID
);

-- Loans with temporal tracking
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    provider TEXT,
    days_left INTEGER,
    amount_left INTEGER,
    active BOOLEAN,
    loan_index INTEGER,              -- Position in loans array
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,
);

-- Products with temporal tracking
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    product_id TEXT,                 -- UUID
    product_name TEXT,               -- JSON: name
    age_in_days INTEGER,             -- Product's age in game days
    stats TEXT,                      -- JSON object as text
    servers TEXT,                    -- JSON object as text
    campaigns TEXT,                  -- JSON array as text
    hosting_allocation INTEGER,
    framework_name TEXT,
    investments TEXT,                -- JSON array as text
    mergers TEXT,                    -- JSON array as text
    support_teams TEXT,              -- JSON array as text
    tickets TEXT,                    -- JSON array as text
    ticket_resolve_times TEXT,       -- JSON array as text
    resolved_tickets INTEGER,
    total_tickets INTEGER,
    ads TEXT,                        -- JSON array as text
    next_ddos_attack INTEGER,
    logo_path TEXT,
    product_type_name TEXT,
    investor TEXT,                   -- JSON object as text
    position INTEGER,
    owned_percentage INTEGER,
    disable_user_loss BOOLEAN,
    last_ddos_attack INTEGER,
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,
    
    UNIQUE(save_file_id, product_id)
);

-- Feature Instances with temporal tracking
CREATE TABLE IF NOT EXISTS feature_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    feature_id TEXT,                 -- UUID
    feature_name TEXT,
    activated BOOLEAN,
    efficiency TEXT,                 -- JSON object as text
    quality TEXT,                    -- JSON object as text
    price_per_month INTEGER,
    premium_features TEXT,           -- JSON array as text
    product_id TEXT,                 -- UUID - FOREIGN KEY to products
    requirements TEXT,               -- JSON object as text
    dissatisfaction INTEGER,
    time_slots TEXT,                 -- JSON array as text
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,
    
    UNIQUE(save_file_id, feature_id)
);

-- Jeets with game time and deduplication
CREATE TABLE IF NOT EXISTS jeets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    jeet_id TEXT,                    -- UUID
    gender TEXT,
    jeet_name TEXT,                  -- JSON: name
    handle TEXT,
    avatar TEXT,
    text TEXT,
    day INTEGER,                     -- Game day when jeet was posted
    read BOOLEAN,                    -- Optional field
    
    -- Temporal tracking
    captured_at DATETIME,            -- When we captured this record
    game_date TEXT,                  -- Game date when captured
    first_seen_game_day INTEGER,    -- Game day when jeet was first captured
    
    UNIQUE(jeet_id, day)             -- Natural deduplication: same jeet on same game day
);

-- Building History with game time
CREATE TABLE IF NOT EXISTS building_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    day INTEGER,                     -- Game day of building change
    building_name TEXT,
    history_order INTEGER,          -- Position in array
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    
    UNIQUE(save_file_id, day, building_name)  -- Natural deduplication by game day
);

-- All other tables get standard temporal tracking...

-- Office with temporal tracking
CREATE TABLE IF NOT EXISTS office (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    building_name TEXT,
    workstations TEXT,               -- JSON array as text
    grid TEXT,                       -- JSON array as text
    last_selected_floor INTEGER,
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER
);

-- Inventory Items with temporal tracking
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    item_name TEXT,
    item_quantity INTEGER,
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,
    
    UNIQUE(save_file_id, item_name)
);

-- Market Values with temporal tracking (great for price tracking!)
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

-- Researched Items (append-only with deduplication)
CREATE TABLE IF NOT EXISTS researched_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    research_item TEXT,
    research_order INTEGER,
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,
    first_researched_at DATETIME,    -- When this item was first seen as researched
    
    UNIQUE(research_item)            -- Each research item only stored once globally
);

-- Activated Benefits (append-only with deduplication)
CREATE TABLE IF NOT EXISTS activated_benefits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    benefit_id TEXT,                 -- UUID
    benefit_order INTEGER,
    
    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,
    first_activated_at DATETIME,     -- When this benefit was first seen
    
    UNIQUE(benefit_id)               -- Each benefit only stored once globally
);

-- Performance indexes with temporal considerations
CREATE INDEX IF NOT EXISTS idx_save_files_game_date ON save_files(game_date);
CREATE INDEX IF NOT EXISTS idx_save_files_game_day ON save_files(game_day);
CREATE INDEX IF NOT EXISTS idx_save_files_real_timestamp ON save_files(real_timestamp);
CREATE INDEX IF NOT EXISTS idx_save_files_ingestion_order ON save_files(ingestion_order);

-- Temporal indexes for all major tables
CREATE INDEX IF NOT EXISTS idx_employees_captured_at ON employees(captured_at);
CREATE INDEX IF NOT EXISTS idx_employees_game_day ON employees(game_day);
CREATE INDEX IF NOT EXISTS idx_transactions_captured_at ON transactions(captured_at);
CREATE INDEX IF NOT EXISTS idx_transactions_game_day ON transactions(day);
CREATE INDEX IF NOT EXISTS idx_jeets_captured_at ON jeets(captured_at);
CREATE INDEX IF NOT EXISTS idx_jeets_game_day ON jeets(day);
CREATE INDEX IF NOT EXISTS idx_market_values_captured_at ON market_values(captured_at);
CREATE INDEX IF NOT EXISTS idx_market_values_game_day ON market_values(game_day);

-- Foreign key indexes
CREATE INDEX IF NOT EXISTS idx_employees_save_file ON employees(save_file_id);
CREATE INDEX IF NOT EXISTS idx_transactions_save_file ON transactions(save_file_id);
CREATE INDEX IF NOT EXISTS idx_products_save_file ON products(save_file_id);

-- Natural deduplication indexes
CREATE INDEX IF NOT EXISTS idx_jeets_natural_key ON jeets(jeet_id, day);
CREATE INDEX IF NOT EXISTS idx_transactions_natural_key ON transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_employees_natural_key ON employees(employee_id, employee_status);
"""

def print_temporal_schema_summary():
    """Print summary of temporal tracking approach"""
    print("⏰ Temporal Raw Storage Schema")
    print("="*50)
    print("🎯 Design Philosophy:")
    print("   • Raw storage with simple timestamp tracking")
    print("   • Dual time tracking: game time + real capture time")
    print("   • Natural deduplication using game UUIDs")
    print("   • Append-only for incremental data (jeets, transactions)")
    print("   • Full snapshots for state data (employees, office)")
    print("")
    print("⏱️ Temporal Tracking Fields (added to all tables):")
    print("   • captured_at: When we captured this data (real time)")
    print("   • game_date: Game's current date when captured")
    print("   • game_day: Extracted game day number")
    print("   • ingestion_order: Sequential processing order")
    print("")
    print("🔄 Deduplication Strategies:")
    print("   • Transactions: UUID-based (transaction_id)")
    print("   • Jeets: UUID + game day (jeet_id, day)")
    print("   • Building History: Game day + building name")
    print("   • Research Items: Global unique (research_item)")
    print("   • Benefits: Global unique (benefit_id)")
    print("   • Employees: UUID + status (employee_id, employee_status)")
    print("")
    print("📊 Time-based Analysis Ready:")
    print("   • Market price trends over game time")
    print("   • Employee salary progression")
    print("   • Financial transaction patterns")
    print("   • Company growth metrics")
    print("   • Research unlock timeline")
    print("")
    print("🗄️ Raw Storage Benefits:")
    print("   • Complete data preservation")
    print("   • Flexible analysis later")
    print("   • Natural game progression tracking")
    print("   • Easy backfill from historical saves")

if __name__ == "__main__":
    print_temporal_schema_summary()