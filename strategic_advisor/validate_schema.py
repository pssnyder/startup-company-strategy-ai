#!/usr/bin/env python3
"""
Schema Validation Tool
Compare our database schema against the official JSON schema export
"""

import json
from pathlib import Path

def analyze_json_schema():
    """Analyze the official JSON schema and compare with our database design"""
    
    schema_file = Path('schema_export.json')
    if not schema_file.exists():
        print("❌ Schema export file not found")
        return
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    print("🔍 JSON Schema Analysis vs Database Design")
    print("="*70)
    
    # Get the required top-level fields
    required_fields = schema.get('required', [])
    properties = schema.get('properties', {})
    
    print(f"📊 Total required fields: {len(required_fields)}")
    print(f"📊 Total properties: {len(properties)}")
    
    print("\n🗂️ Key Collections Analysis:")
    print("-" * 50)
    
    # Analyze each major collection for database table design
    collections_analysis = {}
    
    for field_name in required_fields:
        if field_name in properties:
            field_schema = properties[field_name]
            field_type = field_schema.get('type', 'unknown')
            
            if field_type == 'array':
                items_schema = field_schema.get('items', {})
                if isinstance(items_schema, dict):
                    item_type = items_schema.get('type', 'unknown')
                    if item_type == 'object':
                        item_properties = items_schema.get('properties', {})
                        item_required = items_schema.get('required', [])
                        
                        collections_analysis[field_name] = {
                            'type': 'array_of_objects',
                            'properties': list(item_properties.keys()),
                            'required_properties': item_required,
                            'property_count': len(item_properties)
                        }
                        
                        print(f"📋 {field_name}:")
                        print(f"   Type: Array of objects")
                        print(f"   Properties: {len(item_properties)} fields")
                        print(f"   Required: {len(item_required)} fields")
                        if len(item_properties) <= 10:
                            print(f"   Fields: {list(item_properties.keys())}")
                        else:
                            print(f"   Sample fields: {list(item_properties.keys())[:10]}...")
                    else:
                        collections_analysis[field_name] = {
                            'type': f'array_of_{item_type}',
                            'properties': [],
                            'required_properties': [],
                            'property_count': 0
                        }
                        print(f"📜 {field_name}: Array of {item_type}")
                else:
                    print(f"📜 {field_name}: Array (items schema not defined)")
                    
            elif field_type == 'object':
                obj_properties = field_schema.get('properties', {})
                obj_required = field_schema.get('required', [])
                
                collections_analysis[field_name] = {
                    'type': 'object',
                    'properties': list(obj_properties.keys()),
                    'required_properties': obj_required,
                    'property_count': len(obj_properties)
                }
                
                print(f"🗂️ {field_name}:")
                print(f"   Type: Object")
                print(f"   Properties: {len(obj_properties)} fields")
                print(f"   Required: {len(obj_required)} fields")
                if len(obj_properties) <= 10:
                    print(f"   Fields: {list(obj_properties.keys())}")
                else:
                    print(f"   Sample fields: {list(obj_properties.keys())[:10]}...")
            else:
                print(f"📝 {field_name}: {field_type}")
    
    print("\n🔗 Relational Field Analysis:")
    print("-" * 50)
    
    # Look for UUID fields that indicate relationships
    uuid_fields = {}
    for field_name, analysis in collections_analysis.items():
        if analysis['type'] in ['array_of_objects', 'object']:
            field_schema = properties[field_name]
            if field_schema.get('type') == 'array':
                items_schema = field_schema.get('items', {})
                if isinstance(items_schema, dict):
                    item_properties = items_schema.get('properties', {})
                    for prop_name, prop_schema in item_properties.items():
                        if prop_schema.get('format') == 'uuid':
                            if field_name not in uuid_fields:
                                uuid_fields[field_name] = []
                            uuid_fields[field_name].append(prop_name)
            elif field_schema.get('type') == 'object':
                obj_properties = field_schema.get('properties', {})
                for prop_name, prop_schema in obj_properties.items():
                    if prop_schema.get('format') == 'uuid':
                        if field_name not in uuid_fields:
                            uuid_fields[field_name] = []
                        uuid_fields[field_name].append(prop_name)
    
    for table_name, uuids in uuid_fields.items():
        print(f"🔗 {table_name}: UUID fields = {uuids}")
    
    print("\n🎯 Database Table Recommendations:")
    print("-" * 50)
    
    priority_tables = [
        'candidates', 'employees', 'transactions', 'products', 
        'featureInstances', 'office', 'loans', 'inventory',
        'competitorProducts', 'productionPlans', 'jeets'
    ]
    
    for table in priority_tables:
        if table in collections_analysis:
            analysis = collections_analysis[table]
            print(f"✅ {table}: {analysis['property_count']} fields ({analysis['type']})")
        else:
            print(f"❌ {table}: Not found in schema")
    
    print("\n📋 Complex Nested Objects (Store as JSON initially):")
    print("-" * 50)
    
    # Look for complex nested structures
    complex_fields = []
    for field_name, field_schema in properties.items():
        if field_schema.get('type') == 'object':
            obj_properties = field_schema.get('properties', {})
            # Check for deeply nested structures
            for prop_name, prop_schema in obj_properties.items():
                if prop_schema.get('type') == 'object' and prop_schema.get('properties'):
                    complex_fields.append(f"{field_name}.{prop_name}")
                elif prop_schema.get('type') == 'array':
                    items = prop_schema.get('items', {})
                    if isinstance(items, dict) and items.get('type') == 'object':
                        complex_fields.append(f"{field_name}.{prop_name}")
    
    for field in complex_fields[:10]:  # Show first 10
        print(f"🏗️ {field}")
    
    print(f"\n📊 Summary:")
    print(f"   • {len([a for a in collections_analysis.values() if a['type'] == 'array_of_objects'])} array collections")
    print(f"   • {len([a for a in collections_analysis.values() if a['type'] == 'object'])} object collections") 
    print(f"   • {len(uuid_fields)} collections with UUID relationships")
    print(f"   • {len(complex_fields)} complex nested structures")
    
    return collections_analysis, uuid_fields

if __name__ == "__main__":
    analyze_json_schema()