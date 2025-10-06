#!/usr/bin/env python3
"""
Updated Database Schema Implementation
Based on official JSON schema validation
"""

UPDATED_SCHEMA_SQL = """
-- Main save file metadata (verified against JSON schema)
CREATE TABLE IF NOT EXISTS save_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    
    -- Game metadata (from JSON schema)
    date TEXT,                       -- JSON: date
    started TEXT,                    -- JSON: started
    game_id TEXT,                    -- JSON: id
    company_name TEXT,               -- JSON: companyName
    save_game_name TEXT,             -- JSON: saveGameName
    file_name TEXT,                  -- JSON: fileName
    last_version TEXT,               -- JSON: lastVersion
    last_saved TEXT,                 -- JSON: lastSaved
    
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
    
    -- File metadata
    real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    raw_json TEXT,                   -- Complete JSON backup
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Employee references (from employeesOrder array)
CREATE TABLE IF NOT EXISTS employee_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    employee_id TEXT,                -- UUID from employeesOrder
    employee_order INTEGER,          -- Position in array
    
    UNIQUE(save_file_id, employee_id)
);

-- All employee data (from firedEmployees, resignedEmployees arrays)
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
    required_worker INTEGER,         -- Note: JSON has typo "requiredWer"
    mood REAL,
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
    negotiation TEXT,                -- JSON object as text
    hired DATETIME,
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
    
    UNIQUE(save_file_id, employee_id)
);

-- Candidates (verified 33 fields)
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
    
    UNIQUE(save_file_id, candidate_id)
);

-- Transactions (verified 7 fields)
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    transaction_id TEXT,             -- UUID
    day INTEGER,
    hour INTEGER,
    minute INTEGER,
    amount REAL,
    label TEXT,
    balance REAL,
    
    UNIQUE(save_file_id, transaction_id)
);

-- Loans (verified 4 fields)
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    provider TEXT,
    days_left INTEGER,
    amount_left INTEGER,
    active BOOLEAN,
    loan_index INTEGER               -- Position in loans array
);

-- Products (verified 24 fields)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    product_id TEXT,                 -- UUID
    product_name TEXT,               -- JSON: name
    age_in_days INTEGER,
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
    
    UNIQUE(save_file_id, product_id)
);

-- Feature Instances (verified 11 fields)
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
    
    UNIQUE(save_file_id, feature_id)
);

-- Office (verified 4 fields)
CREATE TABLE IF NOT EXISTS office (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    building_name TEXT,
    workstations TEXT,               -- JSON array as text (complex objects)
    grid TEXT,                       -- JSON array as text (spatial data)
    last_selected_floor INTEGER     -- Can be null
);

-- Inventory (verified 19 fields + stats object)
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    item_name TEXT,                  -- Key from inventory object
    item_quantity INTEGER,           -- Value from inventory object
    
    UNIQUE(save_file_id, item_name)
);

-- Inventory stats (194 numbered stats stored separately)
CREATE TABLE IF NOT EXISTS inventory_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    stat_number INTEGER,             -- Key from inventory.stats object
    stat_value TEXT,                 -- Value (can be various types)
    
    UNIQUE(save_file_id, stat_number)
);

-- Production Plans (verified 5 fields)
CREATE TABLE IF NOT EXISTS production_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    plan_id TEXT,                    -- UUID
    plan_name TEXT,
    production TEXT,                 -- JSON object as text (complex structure)
    skip_modules_with_missing_requirements BOOLEAN,
    exceed_targets BOOLEAN,
    
    UNIQUE(save_file_id, plan_id)
);

-- Jeets (verified 8 fields)
CREATE TABLE IF NOT EXISTS jeets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    jeet_id TEXT,                    -- UUID
    gender TEXT,
    jeet_name TEXT,                  -- JSON: name
    handle TEXT,
    avatar TEXT,
    text TEXT,
    day INTEGER,
    read BOOLEAN                     -- Optional field
);

-- Competitor Products (verified 16 fields)
CREATE TABLE IF NOT EXISTS competitor_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    product_id TEXT,
    product_name TEXT,               -- JSON: name
    logo_color_degree INTEGER,
    logo_path TEXT,
    users REAL,
    product_type_name TEXT,
    controlled BOOLEAN,
    history TEXT,                    -- JSON object as text
    stock_volume INTEGER,
    owned_stocks INTEGER,
    deal_results TEXT,               -- JSON array as text
    stock_transactions TEXT,         -- JSON array as text
    price_expectations REAL,
    growth INTEGER,
    viral_days_left INTEGER,
    version REAL                     -- Optional field
);

-- Market Values (60 components with basePrice and change)
CREATE TABLE IF NOT EXISTS market_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    component_name TEXT,
    base_price INTEGER,
    price_change REAL,
    
    UNIQUE(save_file_id, component_name)
);

-- Building History (verified 2 fields)
CREATE TABLE IF NOT EXISTS building_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    day INTEGER,
    building_name TEXT,
    history_order INTEGER           -- Position in array
);

-- Completed Events (7 named events)
CREATE TABLE IF NOT EXISTS completed_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    event_name TEXT,
    event_count INTEGER,
    
    UNIQUE(save_file_id, event_name)
);

-- Activated Benefits (array of UUID strings)
CREATE TABLE IF NOT EXISTS activated_benefits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    benefit_id TEXT,                 -- UUID
    benefit_order INTEGER           -- Position in array
);

-- Researched Items (array of strings)
CREATE TABLE IF NOT EXISTS researched_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    research_item TEXT,
    research_order INTEGER          -- Position in array
);

-- CEO Information (verified 5 fields)
CREATE TABLE IF NOT EXISTS ceo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    retirement_fund TEXT,            -- JSON object as text
    backstory TEXT,
    ceo_name TEXT,                   -- JSON: name
    avatar TEXT,
    employee_id TEXT                 -- UUID reference
);

-- Game Variables (verified 9 fields)
CREATE TABLE IF NOT EXISTS game_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    ceo_starting_age INTEGER,
    disable_ceo_aging BOOLEAN,
    disable_employee_aging BOOLEAN,
    starting_money INTEGER,
    everything_unlocked BOOLEAN,
    disable_workstation_limit BOOLEAN,
    disable_investor BOOLEAN,
    retirement_age INTEGER,
    days_per_year INTEGER
);

-- Hosting Information (verified 7 fields)
CREATE TABLE IF NOT EXISTS hosting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    building_name TEXT,
    grid TEXT,                       -- JSON array as text
    racks TEXT,                      -- JSON array as text
    controllers TEXT,                -- JSON array as text
    inventory TEXT,                  -- JSON object as text
    room_temperature INTEGER,
    performance TEXT                 -- JSON object as text
);

-- Purchase Inventory (3 items)
CREATE TABLE IF NOT EXISTS purchase_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    item_name TEXT,
    quantity INTEGER,
    
    UNIQUE(save_file_id, item_name)
);

-- Investment Projects (1 verified: SolarPower)
CREATE TABLE IF NOT EXISTS investment_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    project_name TEXT,
    invested REAL,                   -- Can be null
    goal INTEGER,
    daily_budget REAL,
    
    UNIQUE(save_file_id, project_name)
);

-- Employee Sort Order (2 fields)
CREATE TABLE IF NOT EXISTS employees_sort_order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    sort_name TEXT,
    sort_order BOOLEAN
);

-- Progress tracking (1 verified: products)
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    progress_data TEXT               -- JSON object as text
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_save_files_game_date ON save_files(date);
CREATE INDEX IF NOT EXISTS idx_save_files_company ON save_files(company_name);
CREATE INDEX IF NOT EXISTS idx_save_files_timestamp ON save_files(real_timestamp);

-- Foreign key indexes
CREATE INDEX IF NOT EXISTS idx_employees_save_file ON employees(save_file_id);
CREATE INDEX IF NOT EXISTS idx_employee_refs_save_file ON employee_references(save_file_id);
CREATE INDEX IF NOT EXISTS idx_candidates_save_file ON candidates(save_file_id);
CREATE INDEX IF NOT EXISTS idx_transactions_save_file ON transactions(save_file_id);
CREATE INDEX IF NOT EXISTS idx_products_save_file ON products(save_file_id);
CREATE INDEX IF NOT EXISTS idx_feature_instances_save_file ON feature_instances(save_file_id);

-- Relationship indexes
CREATE INDEX IF NOT EXISTS idx_feature_instances_product_id ON feature_instances(product_id);
CREATE INDEX IF NOT EXISTS idx_employees_competitor_product ON employees(competitor_product_id);

-- Analysis indexes
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);
CREATE INDEX IF NOT EXISTS idx_employees_salary ON employees(salary);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(employee_status);
CREATE INDEX IF NOT EXISTS idx_employees_type ON employees(employee_type_name);
"""

def print_schema_summary():
    """Print a summary of the updated schema"""
    print("🗄️ Updated Database Schema Summary")
    print("="*60)
    print("📊 Core Tables:")
    print("   • save_files - Game metadata and financial data")
    print("   • employee_references - Active employee UUIDs from employeesOrder")
    print("   • employees - All employee data (active/fired/resigned)")
    print("   • candidates - Job candidates (33 fields)")
    print("   • transactions - Financial transactions (7 fields)")
    print("   • products - Company products (24 fields)")
    print("   • feature_instances - Product features (11 fields)")
    print("   • loans - Company loans (4 fields)")
    print("   • office - Office layout and workstations")
    print("   • inventory_items - Inventory quantities")
    print("   • inventory_stats - 194 numbered game stats")
    print("   • market_values - 60 market components with pricing")
    print("   • production_plans - Manufacturing plans")
    print("   • jeets - Social media posts")
    print("   • competitor_products - Market competition")
    print("   • hosting - Server hosting infrastructure")
    print("   • ceo - CEO information")
    print("   • game_variables - Game settings")
    print("")
    print("🔗 Key Relationships:")
    print("   • feature_instances.product_id → products.product_id")
    print("   • employees.competitor_product_id → competitor_products.product_id")
    print("   • ceo.employee_id → employees.employee_id")
    print("   • employee_references.employee_id → employees.employee_id")
    print("")
    print("🏗️ Complex JSON Objects (preserved as text):")
    print("   • office.workstations, office.grid (spatial data)")
    print("   • products.stats, products.campaigns (complex metrics)")
    print("   • market_values (60 components with basePrice/change)")
    print("   • hosting.racks, hosting.grid (server infrastructure)")
    print("")
    print("✅ Schema verified against official JSON schema export!")

if __name__ == "__main__":
    print_schema_summary()