#!/usr/bin/env python3
"""
Schema Gap Analysis - Compare Database vs Game Save Schema
"""

import sys
import sqlite3
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def analyze_schema_gaps():
    """Compare our database schema with the actual game save file schema"""
    
    print("🔍 SCHEMA GAP ANALYSIS")
    print("="*70)
    
    # Load the official game schema
    with open('schema_export.json', 'r') as f:
        game_schema = json.load(f)
    
    print("📊 OFFICIAL GAME SAVE FILE SCHEMA")
    print("-" * 50)
    
    required_fields = game_schema.get('required', [])
    all_properties = game_schema.get('properties', {})
    
    print(f"Total top-level properties: {len(all_properties)}")
    print(f"Required properties: {len(required_fields)}")
    print()
    
    # Categorize the properties
    major_sections = {}
    for prop_name, prop_def in all_properties.items():
        if prop_def.get('type') == 'array':
            items_def = prop_def.get('items', {})
            if isinstance(items_def, dict) and items_def.get('type') == 'object':
                major_sections[prop_name] = f"Array of objects ({len(items_def.get('properties', {}))} fields each)"
            else:
                major_sections[prop_name] = "Array of simple values"
        elif prop_def.get('type') == 'object':
            props = prop_def.get('properties', {})
            major_sections[prop_name] = f"Object ({len(props)} properties)"
        else:
            major_sections[prop_name] = f"Simple field ({prop_def.get('type', 'unknown')})"
    
    print("🎯 MAJOR DATA SECTIONS IN GAME SAVES:")
    for section, description in major_sections.items():
        required_marker = "⭐ REQUIRED" if section in required_fields else "   Optional"
        print(f"   {required_marker} | {section}: {description}")
    
    print()
    
    # Check our current database
    print("🗄️ CURRENT DATABASE SCHEMA")
    print("-" * 50)
    
    db = sqlite3.connect("momentum_ai_historical.db")
    cursor = db.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    our_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Our current tables: {', '.join(our_tables)}")
    print()
    
    # Identify missing sections
    print("❌ MISSING FROM OUR DATABASE:")
    print("-" * 50)
    
    key_missing = []
    for section in ['candidates', 'products', 'featureInstances', 'office', 'inventory', 'competitorProducts']:
        if section not in [table.lower().replace('_', '') for table in our_tables]:
            if section in required_fields:
                key_missing.append(f"⭐ {section} (REQUIRED)")
            else:
                key_missing.append(f"   {section}")
    
    for missing in key_missing:
        print(f"   {missing}")
    
    print()
    
    # Show what candidates array contains
    print("👥 CANDIDATES SECTION DETAILS:")
    print("-" * 50)
    candidates_schema = all_properties.get('candidates', {})
    if candidates_schema.get('type') == 'array':
        candidate_props = candidates_schema.get('items', {}).get('properties', {})
        print(f"Each candidate has {len(candidate_props)} fields:")
        for field_name, field_def in candidate_props.items():
            field_type = field_def.get('type', 'unknown')
            print(f"   • {field_name}: {field_type}")
    
    print()
    
    # Show what we are capturing vs what we should be
    print("📊 COVERAGE ANALYSIS:")
    print("-" * 50)
    
    captured = ['transactions', 'jeets', 'marketValues', 'date', 'balance', 'xp', 'researchPoints']
    total_sections = len(required_fields)
    captured_sections = len([s for s in captured if s in required_fields])
    
    print(f"Required sections in game: {total_sections}")
    print(f"Required sections we capture: {captured_sections}")
    print(f"Coverage: {captured_sections/total_sections*100:.1f}%")
    
    db.close()

if __name__ == "__main__":
    analyze_schema_gaps()