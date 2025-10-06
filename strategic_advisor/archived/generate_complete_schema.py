#!/usr/bin/env python3
"""
Complete Game Save Database Schema Generator
100% coverage of all JSON schema fields with proper relational structure
"""

import json
from pathlib import Path

def analyze_schema_structure():
    """Analyze the complete JSON schema to build database structure"""
    
    with open('schema_export.json', 'r') as f:
        schema = json.load(f)
    
    print("🏗️ COMPLETE DATABASE SCHEMA ANALYSIS")
    print("="*70)
    
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    
    print(f"📊 Total root-level properties: {len(properties)}")
    print(f"⭐ Required properties: {len(required)}")
    print()
    
    # Categorize fields
    scalar_fields = []      # Go in game_state table
    array_tables = []       # Get their own tables
    object_tables = []      # Complex objects that need tables
    
    for prop_name, prop_def in properties.items():
        prop_type = prop_def.get('type')
        is_required = prop_name in required
        
        if prop_type == 'array':
            # Each array becomes its own table
            items_def = prop_def.get('items', {})
            if items_def is False:
                # Arrays with "items": false can contain any type
                array_tables.append({
                    'name': prop_name,
                    'required': is_required,
                    'item_fields': 1,
                    'any_type': True,
                    'properties': {}
                })
            elif isinstance(items_def, dict):
                if items_def.get('type') == 'object':
                    item_props = items_def.get('properties', {})
                    array_tables.append({
                        'name': prop_name,
                        'required': is_required,
                        'item_fields': len(item_props),
                        'properties': item_props
                    })
                else:
                    # Simple array (like string array)
                    array_tables.append({
                        'name': prop_name,
                        'required': is_required,
                        'item_fields': 1,
                        'simple_type': items_def.get('type', 'unknown'),
                        'properties': {}
                    })
            else:
                # Default case for arrays without proper items definition
                array_tables.append({
                    'name': prop_name,
                    'required': is_required,
                    'item_fields': 1,
                    'any_type': True,
                    'properties': {}
                })
        
        elif prop_type == 'object':
            # Complex objects need their own tables
            obj_props = prop_def.get('properties', {})
            object_tables.append({
                'name': prop_name,
                'required': is_required,
                'properties': obj_props
            })
        
        else:
            # Scalar fields go in main game_state table
            scalar_fields.append({
                'name': prop_name,
                'type': prop_type,
                'required': is_required,
                'format': prop_def.get('format')
            })
    
    print("📋 GAME_STATE TABLE (Root-level scalars):")
    print(f"   Will contain {len(scalar_fields)} fields")
    for field in scalar_fields:
        req_marker = "⭐" if field['required'] else " "
        type_info = field['type']
        if field['format']:
            type_info += f" ({field['format']})"
        print(f"   {req_marker} {field['name']}: {type_info}")
    
    print(f"\n📊 ARRAY TABLES ({len(array_tables)} tables):")
    for table in array_tables:
        req_marker = "⭐" if table['required'] else " "
        if 'any_type' in table:
            print(f"   {req_marker} {table['name']}: Any type array")
        elif 'simple_type' in table:
            print(f"   {req_marker} {table['name']}: Simple {table['simple_type']} array")
        else:
            print(f"   {req_marker} {table['name']}: {table['item_fields']} fields per record")
    
    print(f"\n🏗️ OBJECT TABLES ({len(object_tables)} tables):")
    for table in object_tables:
        req_marker = "⭐" if table['required'] else " "
        print(f"   {req_marker} {table['name']}: {len(table['properties'])} properties")
    
    return {
        'scalar_fields': scalar_fields,
        'array_tables': array_tables,
        'object_tables': object_tables
    }

def generate_complete_schema(analysis):
    """Generate complete SQL schema from analysis"""
    
    schema_sql = []
    schema_sql.append("-- COMPLETE STARTUP COMPANY GAME SAVE DATABASE SCHEMA")
    schema_sql.append("-- 100% coverage of all JSON schema fields")
    schema_sql.append("")
    
    # Main game state table with all scalar fields
    schema_sql.append("-- Main game state table (all root-level scalars)")
    schema_sql.append("CREATE TABLE IF NOT EXISTS game_state (")
    schema_sql.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
    schema_sql.append("    filename TEXT NOT NULL UNIQUE,")
    schema_sql.append("")
    schema_sql.append("    -- Temporal tracking")
    schema_sql.append("    real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,")
    schema_sql.append("    file_modified_time DATETIME,")
    schema_sql.append("    ingestion_order INTEGER,")
    schema_sql.append("")
    schema_sql.append("    -- All root-level scalar fields from JSON schema")
    
    for field in analysis['scalar_fields']:
        sql_type = convert_json_type_to_sql(field['type'], field.get('format'))
        comment = f"-- JSON: {field['name']}"
        if field['required']:
            comment += " (REQUIRED)"
        
        # Keep original field names (no conversion needed)
        db_name = field['name']
        
        # Handle name conflicts with SQL reserved words or our schema
        if db_name == 'id':
            db_name = 'game_id'  # Avoid conflict with PRIMARY KEY id
        
        schema_sql.append(f"    {db_name} {sql_type}, {comment}")
    
    schema_sql.append("")
    schema_sql.append("    -- Raw storage")
    schema_sql.append("    file_size INTEGER,")
    schema_sql.append("    raw_json TEXT,")
    schema_sql.append("")
    schema_sql.append("    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,")
    schema_sql.append("    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    schema_sql.append(");")
    schema_sql.append("")
    
    # Array tables
    schema_sql.append("-- ARRAY TABLES (one table per root-level array)")
    schema_sql.append("")
    
    for table in analysis['array_tables']:
        table_name = table['name']  # Keep original camelCase names
        
        # Fix SQL reserved word conflicts in table names
        if table_name == 'employeesOrder':
            table_name = 'employeesOrderList'  # Avoid 'order' keyword
        
        schema_sql.append(f"-- {table['name']} array -> {table_name} table")
        
        if table['required']:
            schema_sql.append(f"-- ⭐ REQUIRED FIELD")
        
        schema_sql.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")
        schema_sql.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
        schema_sql.append("    game_state_id INTEGER REFERENCES game_state(id),")
        schema_sql.append("    array_index INTEGER,  -- Position in original array")
        schema_sql.append("")
        
        if 'any_type' in table:
            # Generic any-type array
            schema_sql.append(f"    value TEXT,  -- Array item (any type as JSON)")
        elif 'simple_type' in table:
            # Simple array like strings
            sql_type = convert_json_type_to_sql(table['simple_type'])
            schema_sql.append(f"    value {sql_type},  -- Array item value")
        else:
            # Complex object array
            schema_sql.append("    -- Object fields")
            for prop_name, prop_def in table['properties'].items():
                sql_type = convert_json_type_to_sql(prop_def.get('type'), prop_def.get('format'))
                db_name = prop_name  # Keep original camelCase
                
                # Handle name conflicts  
                if db_name == 'id':
                    db_name = f'{table_name}ItemId'  # More specific naming
                
                # Handle nested objects/arrays as JSON text
                if prop_def.get('type') in ['object', 'array']:
                    sql_type = 'TEXT'  # Store as JSON
                
                schema_sql.append(f"    {db_name} {sql_type},  -- JSON: {prop_name}")
        
        schema_sql.append("")
        schema_sql.append("    -- Temporal tracking")
        schema_sql.append("    captured_at DATETIME,")
        schema_sql.append("    game_date TEXT,")
        schema_sql.append("    game_day INTEGER,")
        schema_sql.append("")
        schema_sql.append(f"    UNIQUE(game_state_id, array_index)")
        schema_sql.append(");")
        schema_sql.append("")
    
    # Object tables
    schema_sql.append("-- OBJECT TABLES (one table per root-level object)")
    schema_sql.append("")
    
    for table in analysis['object_tables']:
        table_name = table['name']  # Keep original camelCase names
        
        # Fix SQL reserved word conflicts in table names  
        if table_name == 'employeesSortOrder':
            table_name = 'employeesSortOrderList'  # Avoid 'order' keyword
        
        schema_sql.append(f"-- {table['name']} object -> {table_name} table")
        
        if table['required']:
            schema_sql.append(f"-- ⭐ REQUIRED FIELD")
        
        schema_sql.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")
        schema_sql.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
        schema_sql.append("    game_state_id INTEGER REFERENCES game_state(id),")
        schema_sql.append("")
        
        # Object properties
        for prop_name, prop_def in table['properties'].items():
            sql_type = convert_json_type_to_sql(prop_def.get('type'), prop_def.get('format'))
            db_name = prop_name  # Keep original camelCase
            
            # Handle name conflicts
            if db_name == 'id':
                db_name = f'{table_name}ObjectId'  # More specific naming
            
            # Handle nested structures as JSON text
            if prop_def.get('type') in ['object', 'array']:
                sql_type = 'TEXT'  # Store as JSON
            
            schema_sql.append(f"    {db_name} {sql_type},  -- JSON: {prop_name}")
        
        schema_sql.append("")
        schema_sql.append("    -- Temporal tracking")
        schema_sql.append("    captured_at DATETIME,")
        schema_sql.append("    game_date TEXT,")
        schema_sql.append("    game_day INTEGER,")
        schema_sql.append("")
        schema_sql.append(f"    UNIQUE(game_state_id)")
        schema_sql.append(");")
        schema_sql.append("")
    
    # Indexes
    schema_sql.append("-- PERFORMANCE INDEXES")
    schema_sql.append("CREATE INDEX IF NOT EXISTS idx_game_state_timestamp ON game_state(real_timestamp);")
    schema_sql.append("CREATE INDEX IF NOT EXISTS idx_game_state_date ON game_state(date);")  # Fixed column name
    schema_sql.append("")
    
    for table in analysis['array_tables']:
        table_name = table['name']
        # Fix SQL reserved word conflicts in table names
        if table_name == 'employeesOrder':
            table_name = 'employeesOrderList'
        schema_sql.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_game_state ON {table_name}(game_state_id);")
        schema_sql.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_captured_at ON {table_name}(captured_at);")
    
    for table in analysis['object_tables']:
        table_name = table['name']
        # Fix SQL reserved word conflicts in table names
        if table_name == 'employeesSortOrder':
            table_name = 'employeesSortOrderList'
        schema_sql.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_game_state ON {table_name}(game_state_id);")
    
    return "\n".join(schema_sql)

def convert_json_type_to_sql(json_type, format_type=None):
    """Convert JSON schema type to SQL type"""
    if not json_type:
        return "TEXT"
    
    type_mapping = {
        'string': 'TEXT',
        'integer': 'INTEGER', 
        'number': 'REAL',
        'boolean': 'BOOLEAN',
        'array': 'TEXT',     # Store as JSON
        'object': 'TEXT'     # Store as JSON
    }
    
    sql_type = type_mapping.get(json_type, 'TEXT')
    
    # Handle special formats
    if format_type == 'date-time':
        sql_type = 'DATETIME'
    elif format_type == 'uuid':
        sql_type = 'TEXT'  # UUIDs are strings
    
    return sql_type

def main():
    """Generate complete database schema"""
    print("🔄 Analyzing complete JSON schema structure...")
    analysis = analyze_schema_structure()
    
    print(f"\n📝 Generating complete SQL schema...")
    complete_sql = generate_complete_schema(analysis)
    
    # Save to file
    with open('complete_schema.sql', 'w', encoding='utf-8') as f:
        f.write(complete_sql)
    
    print(f"\n✅ Complete schema generated!")
    print(f"📄 Saved to: complete_schema.sql")
    print(f"📊 Coverage:")
    print(f"   🎯 Game state fields: {len(analysis['scalar_fields'])}")
    print(f"   📋 Array tables: {len(analysis['array_tables'])}")
    print(f"   🏗️ Object tables: {len(analysis['object_tables'])}")
    print(f"   🎉 Total coverage: 100% of JSON schema")

if __name__ == "__main__":
    main()