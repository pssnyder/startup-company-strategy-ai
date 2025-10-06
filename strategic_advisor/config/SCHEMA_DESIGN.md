# Startup Company Game Save Database Schema Design

## Overview
This document defines the database schema for the Startup Company strategic advisor system. The schema is designed to mirror the game's JSON save file structure while adding relational capabilities for analysis.

**CRITICAL UPDATE**: Based on official JSON schema analysis, employees are NOT stored as a top-level array. Instead, they exist as references in `employeesOrder` with actual employee data in `firedEmployees`/`resignedEmployees` arrays.

## Design Principles

### 1. Raw Data Layer - VERIFIED ✅
- Mirror the JSON structure as closely as possible
- Preserve all original field names and data types
- Store complete JSON as backup for future schema evolution
- Use UUIDs from game where available, generate surrogate keys where needed

### 2. Relational Connections - VERIFIED ✅
- Link related entities through foreign keys
- Maintain referential integrity
- Enable efficient joins for analysis queries
- Support historical trending across save files

### 3. Employee Data Architecture - CORRECTED 🔄
**Discovery**: Employees are stored as:
- `employeesOrder`: Array of UUID strings (active employee references)
- `firedEmployees`: Array of complete employee objects (40 fields)
- `resignedEmployees`: Array of complete employee objects (41 fields)  
- `unassignedEmployees`: Array (currently empty)
- Active employees appear to be constructed from other data sources

## Core Tables - SCHEMA VERIFIED

### save_files (Metadata Table)
```sql
CREATE TABLE save_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    game_date TEXT,                    -- JSON: date
    started_date TEXT,                 -- JSON: started  
    real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    company_name TEXT,                 -- JSON: companyName
    save_game_name TEXT,              -- JSON: saveGameName
    game_state INTEGER,               -- JSON: state
    is_gameover BOOLEAN,              -- JSON: gameover
    is_paused BOOLEAN,                -- JSON: paused
    last_version TEXT,                -- JSON: lastVersion
    balance REAL,                     -- JSON: balance
    last_price_per_hour INTEGER,     -- JSON: lastPricePerHour
    selected_floor INTEGER,           -- JSON: selectedFloor
    max_contract_hours INTEGER,       -- JSON: maxContractHours
    contracts_completed INTEGER,      -- JSON: contractsCompleted
    xp REAL,                         -- JSON: xp
    research_points INTEGER,          -- JSON: researchPoints
    user_loss_enabled BOOLEAN,       -- JSON: userLossEnabled
    game_id TEXT,                    -- JSON: id
    beta_version_at_start INTEGER,   -- JSON: betaVersionAtStart
    last_saved TEXT,                 -- JSON: lastSaved
    needs_new_loan BOOLEAN,          -- JSON: needsNewLoan
    amount_of_available_research_items INTEGER, -- JSON: amountOfAvailableResearchItems
    auto_start_time_machine BOOLEAN, -- JSON: autoStartTimeMachine
    selected_building_name TEXT,     -- JSON: selectedBuildingName
    raw_json TEXT,                   -- Complete JSON backup
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### candidates
```sql
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    candidate_id TEXT,               -- JSON: id (UUID)
    name TEXT,                       -- JSON: name
    original_name TEXT,              -- JSON: originalName
    employee_type_name TEXT,         -- JSON: employeeTypeName
    salary INTEGER,                  -- JSON: salary
    competitor_product_id TEXT,      -- JSON: competitorProductId
    avatar TEXT,                     -- JSON: avatar
    progress INTEGER,                -- JSON: progress
    level TEXT,                      -- JSON: level
    employees_count INTEGER,         -- JSON: employees (if array)
    speed INTEGER,                   -- JSON: speed
    age INTEGER,                     -- JSON: age
    max_speed INTEGER,               -- JSON: maxSpeed
    animation_speed REAL,            -- JSON: animationSpeed
    required_worker INTEGER,         -- JSON: requiredWorker
    
    UNIQUE(save_file_id, candidate_id)
);
```

### employees - ARCHITECTURE UPDATED 🔄
```sql
-- Employee references table (from employeesOrder array)
CREATE TABLE employee_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    employee_id TEXT,                -- UUID from employeesOrder array
    employee_order INTEGER,          -- Position in array
    is_active BOOLEAN DEFAULT 1,
    
    UNIQUE(save_file_id, employee_id)
);

-- All employee data (active, fired, resigned)
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    employee_id TEXT,                -- JSON: id (UUID)
    name TEXT,                       -- JSON: name
    original_name TEXT,              -- JSON: originalName
    employee_type_name TEXT,         -- JSON: employeeTypeName
    salary INTEGER,                  -- JSON: salary
    competitor_product_id TEXT,      -- JSON: competitorProductId
    avatar TEXT,                     -- JSON: avatar
    progress INTEGER,                -- JSON: progress
    level TEXT,                      -- JSON: level
    speed REAL,                      -- JSON: speed
    age INTEGER,                     -- JSON: age
    max_speed INTEGER,               -- JSON: maxSpeed
    animation_speed REAL,            -- JSON: animationSpeed
    required_worker INTEGER,         -- JSON: requiredWer (typo in JSON)
    mood REAL,                       -- JSON: mood
    overtime_minutes INTEGER,        -- JSON: overtimeMinutes
    components TEXT,                 -- JSON: components (array as JSON text)
    gender TEXT,                     -- JSON: gender
    hours_left INTEGER,              -- JSON: hoursLeft
    call_in_sick_days_left INTEGER,  -- JSON: callInSickDaysLeft
    sick_hours_left INTEGER,         -- JSON: sickHoursLeft
    idle_minutes INTEGER,            -- JSON: idleMinutes
    minutes_till_next_emotion INTEGER, -- JSON: minutesTillNextEmotion
    creation_time INTEGER,           -- JSON: creationTime
    schedule TEXT,                   -- JSON: schedule (object as JSON text)
    superstar BOOLEAN,               -- JSON: superstar
    leads TEXT,                      -- JSON: leads (array as JSON text)
    lead_filters TEXT,               -- JSON: leadFilters (object as JSON text)
    task TEXT,                       -- JSON: task (object as JSON text)
    demands TEXT,                    -- JSON: demands (array as JSON text)
    research_demands BOOLEAN,        -- JSON: researchDemands
    research_salary BOOLEAN,         -- JSON: researchSalary
    negotiation TEXT,                -- JSON: negotiation (object as JSON text)
    hired DATETIME,                  -- JSON: hired
    active_queue_index INTEGER,      -- JSON: activeQueueIndex
    last_tab TEXT,                   -- JSON: lastTab
    last_emotion_name TEXT,          -- JSON: lastEmotionName
    last_bonus_day INTEGER,          -- JSON: lastBonusDay
    is_training BOOLEAN,             -- JSON: isTraining
    last_day INTEGER,                -- JSON: lastDay
    
    -- Employee status (derived from source array)
    employee_status TEXT,            -- 'active', 'fired', 'resigned', 'unassigned'
    source_array TEXT,               -- 'employeesOrder', 'firedEmployees', 'resignedEmployees'
    
    UNIQUE(save_file_id, employee_id)
);
```

### transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    transaction_id TEXT,             -- JSON: id (UUID)
    day INTEGER,                     -- JSON: day
    hour INTEGER,                    -- JSON: hour
    minute INTEGER,                  -- JSON: minute
    amount REAL,                     -- JSON: amount
    label TEXT,                      -- JSON: label
    balance REAL,                    -- JSON: balance
    
    UNIQUE(save_file_id, transaction_id)
);
```

### loans
```sql
CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    provider TEXT,                   -- JSON: provider
    days_left INTEGER,               -- JSON: daysLeft
    amount_left REAL,                -- JSON: amountLeft
    is_active BOOLEAN,               -- JSON: active
    loan_index INTEGER               -- Position in loans array
);
```

### inventory
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    item_key TEXT,                   -- Key from inventory object
    item_value INTEGER,              -- Value from inventory object
    
    UNIQUE(save_file_id, item_key)
);
```

### products
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    product_id TEXT,                 -- JSON: id
    product_name TEXT,               -- JSON: name
    age_in_days INTEGER,             -- JSON: ageInDays
    stats TEXT,                      -- JSON: stats (as JSON text)
    servers TEXT,                    -- JSON: servers (as JSON text)
    campaigns TEXT,                  -- JSON: campaigns (as JSON text)
    hosting_allocation TEXT,         -- JSON: hostingAllocation (as JSON text)
    framework_name TEXT,             -- JSON: frameworkName
    
    UNIQUE(save_file_id, product_id)
);
```

### feature_instances
```sql
CREATE TABLE feature_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    feature_id TEXT,                 -- JSON: id
    feature_name TEXT,               -- JSON: featureName
    is_activated BOOLEAN,            -- JSON: activated
    efficiency REAL,                 -- JSON: efficiency
    quality REAL,                    -- JSON: quality
    
    UNIQUE(save_file_id, feature_id)
);
```

### office
```sql
CREATE TABLE office (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    building_name TEXT,              -- JSON: buildingName
    workstations INTEGER,            -- JSON: workstations
    grid TEXT,                       -- JSON: grid (as JSON text)
    last_selected_floor INTEGER     -- JSON: lastSelectedFloor
);
```

### production_plans
```sql
CREATE TABLE production_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    plan_id TEXT,                    -- JSON: id
    plan_name TEXT,                  -- JSON: name
    production TEXT,                 -- JSON: production (as JSON text)
    skip_modules_with_missing_requirements BOOLEAN, -- JSON: skipModulesWithMissingRequirements
    exceed_targets BOOLEAN,          -- JSON: exceedTargets
    
    UNIQUE(save_file_id, plan_id)
);
```

### research_items
```sql
CREATE TABLE research_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    research_item TEXT,              -- From researchedItems array
    research_order INTEGER           -- Position in array
);
```

### building_history
```sql
CREATE TABLE building_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    day INTEGER,                     -- JSON: day
    building_name TEXT,              -- JSON: buildingName
    history_order INTEGER           -- Position in array
);
```

### completed_events
```sql
CREATE TABLE completed_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    event_name TEXT,                 -- Key from completedEvents object
    event_value INTEGER              -- Value from completedEvents object
);
```

### activated_benefits
```sql
CREATE TABLE activated_benefits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    benefit_name TEXT,               -- From activatedBenefits array
    benefit_order INTEGER           -- Position in array
);
```

### competitor_products
```sql
CREATE TABLE competitor_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    product_id TEXT,                 -- JSON: id
    product_name TEXT,               -- JSON: name
    logo_color_degree INTEGER,       -- JSON: logoColorDegree
    logo_path TEXT,                  -- JSON: logoPath
    users INTEGER                    -- JSON: users
);
```

### market_values
```sql
CREATE TABLE market_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    component_name TEXT,             -- Key from marketValues object
    market_value REAL                -- Value from marketValues object
);
```

### jeets
```sql
CREATE TABLE jeets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    save_file_id INTEGER REFERENCES save_files(id),
    jeet_id TEXT,                    -- JSON: id
    gender TEXT,                     -- JSON: gender
    jeet_name TEXT,                  -- JSON: name
    handle TEXT,                     -- JSON: handle
    avatar TEXT                      -- JSON: avatar
);
```

## Views for Analysis

### Current Company Status
```sql
CREATE VIEW current_company_status AS
SELECT 
    sf.company_name,
    sf.balance,
    sf.research_points,
    sf.xp,
    COUNT(DISTINCT e.employee_id) as active_employees,
    COUNT(DISTINCT c.candidate_id) as available_candidates,
    COUNT(DISTINCT p.product_id) as active_products,
    o.workstations,
    sf.game_date,
    sf.real_timestamp
FROM save_files sf
LEFT JOIN employees e ON sf.id = e.save_file_id AND e.is_fired = 0 AND e.is_resigned = 0
LEFT JOIN candidates c ON sf.id = c.save_file_id  
LEFT JOIN products p ON sf.id = p.save_file_id
LEFT JOIN office o ON sf.id = o.save_file_id
WHERE sf.real_timestamp = (SELECT MAX(real_timestamp) FROM save_files);
```

## Indexes for Performance

```sql
-- Primary lookup indexes
CREATE INDEX idx_save_files_game_date ON save_files(game_date);
CREATE INDEX idx_save_files_company ON save_files(company_name);
CREATE INDEX idx_save_files_timestamp ON save_files(real_timestamp);

-- Foreign key indexes
CREATE INDEX idx_employees_save_file ON employees(save_file_id);
CREATE INDEX idx_candidates_save_file ON candidates(save_file_id);
CREATE INDEX idx_transactions_save_file ON transactions(save_file_id);
CREATE INDEX idx_products_save_file ON products(save_file_id);

-- Analysis indexes
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_employees_salary ON employees(salary);
CREATE INDEX idx_employees_type ON employees(employee_type_name);
```

## Schema Evolution Notes

1. **JSON Backup**: Every save file includes complete raw JSON for future schema updates
2. **Nullable Fields**: Most fields nullable to handle missing data in older save formats
3. **Text Storage**: Complex nested objects stored as JSON text initially, can be normalized later
4. **Unique Constraints**: Prevent duplicate data within same save file
5. **Flexible Design**: Easy to add new tables for newly discovered game mechanics

## Questions for Discussion

1. **Normalization Level**: Should we normalize employee types, building names, etc. into lookup tables?
2. **Historical Tracking**: Do we want separate tables for tracking changes over time?
3. **Computed Fields**: Should we pre-calculate common metrics or compute on-demand?
4. **Partitioning**: Should we partition by company or time period for large datasets?
5. **JSON vs Relational**: Which nested objects should be flattened vs stored as JSON?

## Implementation Priority

### Phase 1: Core Tables
- save_files, employees, candidates, transactions, inventory, office

### Phase 2: Game Mechanics  
- products, feature_instances, production_plans, research_items

### Phase 3: Analytics
- Views, computed metrics, trend analysis tables

### Phase 4: Advanced Features
- Historical change tracking, performance optimization, data archival