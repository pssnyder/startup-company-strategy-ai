#!/usr/bin/env python3
"""
Complete Schema Validation and Gap Analysis
"""

import json
from pathlib import Path

def validate_complete_coverage():
    """Validate 100% coverage and identify any gaps"""
    
    print("🔍 COMPREHENSIVE SCHEMA VALIDATION")
    print("="*60)
    
    # Load official JSON schema
    with open('schema_export.json', 'r') as f:
        schema = json.load(f)
    
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    
    print(f"📊 Official Schema: {len(properties)} properties, {len(required)} required")
    
    # Load our generated SQL schema
    with open('complete_schema.sql', 'r', encoding='utf-8') as f:
        sql_schema = f.read()
    
    # Check coverage
    covered_fields = set()
    missing_fields = []
    
    # Check scalars in game_state table
    scalar_count = 0
    for field_name in properties:
        field_def = properties[field_name]
        field_type = field_def.get('type')
        
        if field_type not in ['array', 'object']:
            scalar_count += 1
            # Check if field appears in SQL (keep original camelCase)
            field_name_to_check = field_name
            if field_name == 'id':
                field_name_to_check = 'game_id'  # Our conflict resolution
                
            if field_name_to_check in sql_schema:
                covered_fields.add(field_name)
            else:
                missing_fields.append(f"SCALAR: {field_name} -> {field_name_to_check}")
    
    # Check arrays
    array_count = 0
    for field_name in properties:
        field_def = properties[field_name]
        if field_def.get('type') == 'array':
            array_count += 1
            table_name = field_name  # Keep original camelCase
            if field_name == 'employeesOrder':
                table_name = 'employeesOrderList'  # Our conflict resolution
            
            if f"CREATE TABLE IF NOT EXISTS {table_name}" in sql_schema:
                covered_fields.add(field_name)
            else:
                missing_fields.append(f"ARRAY: {field_name} -> {table_name}")
    
    # Check objects  
    object_count = 0
    for field_name in properties:
        field_def = properties[field_name]
        if field_def.get('type') == 'object':
            object_count += 1
            table_name = field_name  # Keep original camelCase
            if field_name == 'employeesSortOrder':
                table_name = 'employeesSortOrderList'  # Our conflict resolution
            
            if f"CREATE TABLE IF NOT EXISTS {table_name}" in sql_schema:
                covered_fields.add(field_name)
            else:
                missing_fields.append(f"OBJECT: {field_name} -> {table_name}")
    
    print(f"🎯 Coverage Analysis:")
    print(f"   📋 Scalars: {scalar_count} fields")
    print(f"   📊 Arrays: {array_count} tables") 
    print(f"   🏗️ Objects: {object_count} tables")
    print(f"   📈 Total: {len(properties)} fields")
    print()
    print(f"✅ Covered: {len(covered_fields)}/{len(properties)} ({len(covered_fields)/len(properties)*100:.1f}%)")
    
    if missing_fields:
        print(f"❌ Missing: {len(missing_fields)} fields")
        for missing in missing_fields:
            print(f"   {missing}")
    else:
        print("🎉 100% COMPLETE COVERAGE!")
    
    # Check for any fields in the required list that we missed
    missing_required = []
    for req_field in required:
        if req_field not in covered_fields:
            missing_required.append(req_field)
    
    if missing_required:
        print(f"\n⚠️ Missing REQUIRED fields: {len(missing_required)}")
        for field in missing_required:
            print(f"   {field}")
    else:
        print(f"\n✅ All {len(required)} required fields covered!")
    
    return missing_fields, missing_required

def camel_to_snake(name):
    """Convert camelCase to snake_case - not used anymore"""
    return name  # Keep original name

if __name__ == "__main__":
    missing_fields, missing_required = validate_complete_coverage()
    
    if not missing_fields and not missing_required:
        print("\\n🎉 SCHEMA VALIDATION PASSED!")
        print("✅ Ready for visualization!")
    else:
        print("\\n⚠️ Schema needs updates before visualization")