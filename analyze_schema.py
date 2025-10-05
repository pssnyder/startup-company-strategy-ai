#!/usr/bin/env python3
"""
Analyze JSON structure to understand the game save schema
"""

import json
from pathlib import Path

def analyze_json_structure():
    """Analyze the JSON save file structure"""
    
    # Load the current save file
    save_file = Path('strategic_advisor/save_files/20251005_1139_sg_momentum_ai.json')
    
    if not save_file.exists():
        print("❌ Save file not found")
        return
    
    with open(save_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print('🔍 JSON Structure Analysis')
    print('='*60)
    
    # Top level fields
    print(f"📊 Top-level fields: {len(data)}")
    
    for key, value in list(data.items()):
        if isinstance(value, dict):
            print(f"   📂 {key}: dict({len(value)} fields)")
            # Show sample of nested keys
            if len(value) > 0:
                sample_keys = list(value.keys())[:5]
                print(f"      Sample keys: {sample_keys}")
                
        elif isinstance(value, list):
            print(f"   📋 {key}: list({len(value)} items)")
            if len(value) > 0:
                item_type = type(value[0]).__name__
                print(f"      Item type: {item_type}")
                if isinstance(value[0], dict):
                    sample_keys = list(value[0].keys())[:5]
                    print(f"      Item keys: {sample_keys}")
        else:
            print(f"   📝 {key}: {type(value).__name__} = {str(value)[:50]}")
    
    print("\n🎯 Key Collections for Database Tables:")
    print("-" * 40)
    
    # Analyze key collections that should become tables
    collections = {
        'candidates': data.get('candidates', {}),
        'employees': data.get('employees', {}), 
        'unassignedEmployees': data.get('unassignedEmployees', {}),
        'employeesOrder': data.get('employeesOrder', []),
        'loans': data.get('loans', {}),
        'inventory': data.get('inventory', {}),
        'transactions': data.get('transactions', []),
        'products': data.get('products', {}),
        'features': data.get('features', {}),
        'office': data.get('office', {}),
        'activatedBenefits': data.get('activatedBenefits', {}),
        'buildingHistory': data.get('buildingHistory', []),
        'completedEvents': data.get('completedEvents', {}),
        'progress': data.get('progress', {})
    }
    
    for name, collection in collections.items():
        if isinstance(collection, dict) and len(collection) > 0:
            sample_key = list(collection.keys())[0]
            sample_item = collection[sample_key]
            if isinstance(sample_item, dict):
                fields = list(sample_item.keys())
                print(f"🗂️ {name}: {len(collection)} items, fields: {fields[:8]}")
            else:
                print(f"🗂️ {name}: {len(collection)} items, type: {type(sample_item).__name__}")
        elif isinstance(collection, list) and len(collection) > 0:
            if isinstance(collection[0], dict):
                fields = list(collection[0].keys())
                print(f"📜 {name}: {len(collection)} items, fields: {fields[:8]}")
            else:
                print(f"📜 {name}: {len(collection)} items, type: {type(collection[0]).__name__}")
        else:
            print(f"📄 {name}: {len(collection) if hasattr(collection, '__len__') else 'N/A'} items")

if __name__ == "__main__":
    analyze_json_structure()