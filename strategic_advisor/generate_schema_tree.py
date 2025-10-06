#!/usr/bin/env python3
"""
Database Schema Tree Viewer - JSON Hero Style
Interactive nested outline view of the complete database schema
"""

import json
from pathlib import Path

def generate_schema_tree():
    """Generate nested tree structure of database schema"""
    
    print("🌳 Generating Schema Tree Viewer...")
    
    # Load the schema
    with open('schema_export.json', 'r') as f:
        schema = json.load(f)
    
    properties = schema.get('properties', {})
    
    # Create the tree structure
    tree_data = {
        'game_state': {
            'type': 'table',
            'description': 'Central game state table (root-level scalars)',
            'fields': {},
            'relationships': []
        }
    }
    
    # Add scalar fields to game_state
    scalar_count = 0
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') not in ['array', 'object']:
            scalar_count += 1
            field_name = prop_name if prop_name != 'id' else 'game_id'
            tree_data['game_state']['fields'][field_name] = {
                'type': get_display_type(prop_def.get('type'), prop_def.get('format')),
                'required': True,
                'json_source': prop_name,
                'description': f"JSON: {prop_name}"
            }
    
    # Add system fields
    system_fields = {
        'id': {'type': 'INTEGER PRIMARY KEY', 'required': True, 'description': 'Database auto-increment ID'},
        'filename': {'type': 'TEXT', 'required': True, 'description': 'Save file name'},
        'real_timestamp': {'type': 'DATETIME', 'required': True, 'description': 'When record was captured'},
        'file_modified_time': {'type': 'DATETIME', 'required': False, 'description': 'File system timestamp'},
        'ingestion_order': {'type': 'INTEGER', 'required': False, 'description': 'Order of ingestion'},
        'file_size': {'type': 'INTEGER', 'required': False, 'description': 'File size in bytes'},
        'raw_json': {'type': 'TEXT', 'required': False, 'description': 'Complete JSON dump'},
        'created_at': {'type': 'DATETIME', 'required': True, 'description': 'Database record creation'},
        'updated_at': {'type': 'DATETIME', 'required': True, 'description': 'Database record update'}
    }
    
    for field_name, field_info in system_fields.items():
        tree_data['game_state']['fields'][field_name] = field_info
    
    # Add array tables
    array_count = 0
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') == 'array':
            array_count += 1
            table_name = prop_name if prop_name != 'employeesOrder' else 'employeesOrderList'
            
            tree_data[table_name] = {
                'type': 'array_table',
                'description': f'Array table for JSON field: {prop_name}',
                'json_source': prop_name,
                'fields': {
                    'id': {'type': 'INTEGER PRIMARY KEY', 'required': True, 'description': 'Database auto-increment ID'},
                    'game_state_id': {'type': 'INTEGER FOREIGN KEY', 'required': True, 'description': 'References game_state.id', 'link': 'game_state'},
                    'array_index': {'type': 'INTEGER', 'required': True, 'description': 'Position in original JSON array'},
                },
                'relationships': ['game_state']
            }
            
            # Add array-specific fields
            items_def = prop_def.get('items', {})
            if items_def is False or not isinstance(items_def, dict):
                # Any type array
                tree_data[table_name]['fields']['value'] = {
                    'type': 'TEXT (JSON)',
                    'required': False,
                    'description': 'Array item value (any type stored as JSON)'
                }
            elif items_def.get('type') == 'object':
                # Complex object array
                item_props = items_def.get('properties', {})
                for item_prop_name, item_prop_def in item_props.items():
                    field_name = item_prop_name if item_prop_name != 'id' else f'{table_name}ItemId'
                    tree_data[table_name]['fields'][field_name] = {
                        'type': get_display_type(item_prop_def.get('type'), item_prop_def.get('format')),
                        'required': False,
                        'json_source': item_prop_name,
                        'description': f"JSON item property: {item_prop_name}"
                    }
            else:
                # Simple type array
                tree_data[table_name]['fields']['value'] = {
                    'type': get_display_type(items_def.get('type', 'string')),
                    'required': False,
                    'description': f"Array item value ({items_def.get('type', 'string')})"
                }
            
            # Add temporal fields
            temporal_fields = {
                'captured_at': {'type': 'DATETIME', 'required': True, 'description': 'When this array item was captured'},
                'game_date': {'type': 'TEXT', 'required': False, 'description': 'Game date when captured'},
                'game_day': {'type': 'INTEGER', 'required': False, 'description': 'Game day when captured'}
            }
            
            for field_name, field_info in temporal_fields.items():
                tree_data[table_name]['fields'][field_name] = field_info
    
    # Add object tables
    object_count = 0
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') == 'object':
            object_count += 1
            table_name = prop_name if prop_name != 'employeesSortOrder' else 'employeesSortOrderList'
            
            tree_data[table_name] = {
                'type': 'object_table',
                'description': f'Object table for JSON field: {prop_name}',
                'json_source': prop_name,
                'fields': {
                    'id': {'type': 'INTEGER PRIMARY KEY', 'required': True, 'description': 'Database auto-increment ID'},
                    'game_state_id': {'type': 'INTEGER FOREIGN KEY', 'required': True, 'description': 'References game_state.id', 'link': 'game_state'},
                },
                'relationships': ['game_state']
            }
            
            # Add object properties
            obj_props = prop_def.get('properties', {})
            for obj_prop_name, obj_prop_def in obj_props.items():
                field_name = obj_prop_name if obj_prop_name != 'id' else f'{table_name}ObjectId'
                tree_data[table_name]['fields'][field_name] = {
                    'type': get_display_type(obj_prop_def.get('type'), obj_prop_def.get('format')),
                    'required': False,
                    'json_source': obj_prop_name,
                    'description': f"JSON object property: {obj_prop_name}"
                }
            
            # Add temporal fields
            temporal_fields = {
                'captured_at': {'type': 'DATETIME', 'required': True, 'description': 'When this object was captured'},
                'game_date': {'type': 'TEXT', 'required': False, 'description': 'Game date when captured'},
                'game_day': {'type': 'INTEGER', 'required': False, 'description': 'Game day when captured'}
            }
            
            for field_name, field_info in temporal_fields.items():
                tree_data[table_name]['fields'][field_name] = field_info
    
    return tree_data, scalar_count, array_count, object_count

def get_display_type(json_type, format_type=None):
    """Convert JSON type to display type"""
    if not json_type:
        return "TEXT"
    
    type_mapping = {
        'string': 'TEXT',
        'integer': 'INTEGER', 
        'number': 'REAL',
        'boolean': 'BOOLEAN',
        'array': 'TEXT (JSON)',
        'object': 'TEXT (JSON)'
    }
    
    sql_type = type_mapping.get(json_type, 'TEXT')
    
    if format_type == 'date-time':
        sql_type = 'DATETIME'
    elif format_type == 'uuid':
        sql_type = 'UUID'
    
    return sql_type

def create_tree_viewer():
    """Create interactive tree viewer HTML"""
    
    tree_data, scalar_count, array_count, object_count = generate_schema_tree()
    
    # Convert tree data to JSON for JavaScript
    tree_json = json.dumps(tree_data, indent=2)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Schema Tree Viewer - JSON Hero Style</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            color: #1e3c72;
            font-size: 2.2em;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .stat {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            text-align: center;
            min-width: 100px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #ffd700;
        }}
        
        .stat-label {{
            font-size: 0.9em;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255,255,255,0.98);
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .controls {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 250px;
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .control-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        
        .control-btn:hover {{
            background: #5a6fd8;
        }}
        
        .tree-container {{
            padding: 20px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .tree-node {{
            margin-bottom: 10px;
        }}
        
        .table-header {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .table-header:hover {{
            transform: translateY(-2px);
        }}
        
        .table-header.array-table {{
            background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%);
        }}
        
        .table-header.object-table {{
            background: linear-gradient(135deg, #3742FA 0%, #2F3542 100%);
        }}
        
        .table-info {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .table-name {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .table-type {{
            background: rgba(255,255,255,0.2);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            text-transform: uppercase;
        }}
        
        .expand-icon {{
            font-size: 1.2em;
            transition: transform 0.3s;
        }}
        
        .expand-icon.expanded {{
            transform: rotate(90deg);
        }}
        
        .fields-container {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            margin-left: 20px;
            margin-top: 10px;
            border-radius: 0 8px 8px 0;
            overflow: hidden;
            display: none;
        }}
        
        .fields-container.expanded {{
            display: block;
        }}
        
        .field-row {{
            padding: 12px 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: background 0.2s;
        }}
        
        .field-row:hover {{
            background: #e9ecef;
        }}
        
        .field-row:last-child {{
            border-bottom: none;
        }}
        
        .field-name {{
            font-weight: 600;
            color: #495057;
            min-width: 180px;
            font-family: 'Courier New', monospace;
        }}
        
        .field-type {{
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 500;
            min-width: 100px;
            text-align: center;
        }}
        
        .field-type.primary-key {{
            background: #28a745;
        }}
        
        .field-type.foreign-key {{
            background: #ffc107;
            color: #212529;
        }}
        
        .field-description {{
            color: #6c757d;
            font-size: 0.9em;
            flex: 1;
        }}
        
        .field-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
        }}
        
        .field-link:hover {{
            text-decoration: underline;
        }}
        
        .required-badge {{
            background: #dc3545;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.7em;
            font-weight: bold;
        }}
        
        .json-source {{
            background: #e7f3ff;
            color: #0066cc;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.75em;
            font-family: 'Courier New', monospace;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .highlight {{
            background: #fff3cd !important;
            border-color: #ffeaa7 !important;
        }}
        
        .table-description {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .field-count {{
            background: rgba(255,255,255,0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌳 Database Schema Tree Viewer</h1>
        <p>Interactive nested outline view - JSON Hero style comparison</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{scalar_count}</div>
                <div class="stat-label">Scalar Fields</div>
            </div>
            <div class="stat">
                <div class="stat-number">{array_count}</div>
                <div class="stat-label">Array Tables</div>
            </div>
            <div class="stat">
                <div class="stat-number">{object_count}</div>
                <div class="stat-label">Object Tables</div>
            </div>
            <div class="stat">
                <div class="stat-number">{scalar_count + array_count + object_count + 1}</div>
                <div class="stat-label">Total Tables</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="controls">
            <input type="text" class="search-box" id="searchBox" placeholder="🔍 Search tables and fields...">
            <button class="control-btn" onclick="expandAll()">📂 Expand All</button>
            <button class="control-btn" onclick="collapseAll()">📁 Collapse All</button>
            <button class="control-btn" onclick="scrollToTop()">⬆️ Top</button>
        </div>
        
        <div class="tree-container" id="treeContainer">
            <!-- Tree will be generated by JavaScript -->
        </div>
    </div>

    <script>
        const treeData = {tree_json};
        
        function createTreeView() {{
            const container = document.getElementById('treeContainer');
            container.innerHTML = '';
            
            // Sort tables: game_state first, then arrays, then objects
            const sortedTables = Object.keys(treeData).sort((a, b) => {{
                if (a === 'game_state') return -1;
                if (b === 'game_state') return 1;
                
                const aType = treeData[a].type;
                const bType = treeData[b].type;
                
                if (aType === 'array_table' && bType === 'object_table') return -1;
                if (aType === 'object_table' && bType === 'array_table') return 1;
                
                return a.localeCompare(b);
            }});
            
            sortedTables.forEach(tableName => {{
                const tableData = treeData[tableName];
                const tableNode = createTableNode(tableName, tableData);
                container.appendChild(tableNode);
            }});
        }}
        
        function createTableNode(tableName, tableData) {{
            const node = document.createElement('div');
            node.className = 'tree-node';
            node.setAttribute('data-table', tableName);
            
            const fieldCount = Object.keys(tableData.fields).length;
            const typeClass = tableData.type === 'array_table' ? 'array-table' : 
                             tableData.type === 'object_table' ? 'object-table' : 'table';
            
            node.innerHTML = `
                <div class="table-header ${{typeClass}}" onclick="toggleTable('${{tableName}}')">
                    <div class="table-info">
                        <div class="table-name">${{tableName}}</div>
                        <div class="table-type">${{tableData.type.replace('_', ' ')}}</div>
                        <div class="field-count">${{fieldCount}} fields</div>
                        ${{tableData.json_source ? `<div class="json-source">JSON: ${{tableData.json_source}}</div>` : ''}}
                    </div>
                    <div class="expand-icon" id="icon-${{tableName}}">▶</div>
                </div>
                <div class="fields-container" id="fields-${{tableName}}">
                    ${{Object.entries(tableData.fields).map(([fieldName, fieldData]) => 
                        createFieldRow(tableName, fieldName, fieldData)
                    ).join('')}}
                </div>
            `;
            
            return node;
        }}
        
        function createFieldRow(tableName, fieldName, fieldData) {{
            const isRequired = fieldData.required ? '<span class="required-badge">REQ</span>' : '';
            const jsonSource = fieldData.json_source ? `<span class="json-source">JSON: ${{fieldData.json_source}}</span>` : '';
            const link = fieldData.link ? `<a class="field-link" onclick="scrollToTable('${{fieldData.link}}')" title="Click to go to ${{fieldData.link}} table">🔗 ${{fieldData.link}}</a>` : '';
            
            let typeClass = 'field-type';
            if (fieldData.type.includes('PRIMARY KEY')) typeClass += ' primary-key';
            if (fieldData.type.includes('FOREIGN KEY')) typeClass += ' foreign-key';
            
            return `
                <div class="field-row" data-field="${{tableName}}.${{fieldName}}">
                    <div class="field-name">${{fieldName}}</div>
                    <div class="${{typeClass}}">${{fieldData.type}}</div>
                    <div class="field-description">
                        ${{fieldData.description}}
                        ${{isRequired}}
                        ${{jsonSource}}
                        ${{link}}
                    </div>
                </div>
            `;
        }}
        
        function toggleTable(tableName) {{
            const fieldsContainer = document.getElementById(`fields-${{tableName}}`);
            const icon = document.getElementById(`icon-${{tableName}}`);
            
            if (fieldsContainer.classList.contains('expanded')) {{
                fieldsContainer.classList.remove('expanded');
                icon.classList.remove('expanded');
            }} else {{
                fieldsContainer.classList.add('expanded');
                icon.classList.add('expanded');
            }}
        }}
        
        function expandAll() {{
            document.querySelectorAll('.fields-container').forEach(container => {{
                container.classList.add('expanded');
            }});
            document.querySelectorAll('.expand-icon').forEach(icon => {{
                icon.classList.add('expanded');
            }});
        }}
        
        function collapseAll() {{
            document.querySelectorAll('.fields-container').forEach(container => {{
                container.classList.remove('expanded');
            }});
            document.querySelectorAll('.expand-icon').forEach(icon => {{
                icon.classList.remove('expanded');
            }});
        }}
        
        function scrollToTable(tableName) {{
            const tableElement = document.querySelector(`[data-table="${{tableName}}"]`);
            if (tableElement) {{
                tableElement.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                tableElement.querySelector('.table-header').style.transform = 'scale(1.02)';
                setTimeout(() => {{
                    tableElement.querySelector('.table-header').style.transform = '';
                }}, 300);
                
                // Expand the table if it's not already expanded
                const fieldsContainer = document.getElementById(`fields-${{tableName}}`);
                const icon = document.getElementById(`icon-${{tableName}}`);
                if (!fieldsContainer.classList.contains('expanded')) {{
                    fieldsContainer.classList.add('expanded');
                    icon.classList.add('expanded');
                }}
            }}
        }}
        
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        // Search functionality
        document.getElementById('searchBox').addEventListener('input', function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            const allNodes = document.querySelectorAll('.tree-node');
            
            if (!searchTerm) {{
                allNodes.forEach(node => {{
                    node.classList.remove('hidden');
                    node.querySelectorAll('.field-row').forEach(row => row.classList.remove('highlight'));
                }});
                return;
            }}
            
            allNodes.forEach(node => {{
                const tableName = node.getAttribute('data-table').toLowerCase();
                const fieldRows = node.querySelectorAll('.field-row');
                let hasMatch = false;
                
                // Check table name
                if (tableName.includes(searchTerm)) {{
                    hasMatch = true;
                }}
                
                // Check field names and descriptions
                fieldRows.forEach(row => {{
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {{
                        hasMatch = true;
                        row.classList.add('highlight');
                    }} else {{
                        row.classList.remove('highlight');
                    }}
                }});
                
                if (hasMatch) {{
                    node.classList.remove('hidden');
                    // Auto-expand if there's a match
                    const fieldsContainer = node.querySelector('.fields-container');
                    const icon = node.querySelector('.expand-icon');
                    if (fieldsContainer && icon) {{
                        fieldsContainer.classList.add('expanded');
                        icon.classList.add('expanded');
                    }}
                }} else {{
                    node.classList.add('hidden');
                }}
            }});
        }});
        
        // Initialize the tree view
        createTreeView();
        
        // Auto-expand game_state table
        setTimeout(() => {{
            toggleTable('game_state');
        }}, 500);
    </script>
</body>
</html>"""
    
    # Save the HTML file
    with open('schema_tree_viewer.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Schema Tree Viewer generated!")
    print(f"📄 File: schema_tree_viewer.html")
    print(f"📊 Coverage: {scalar_count + array_count + object_count + 1} tables")
    print(f"🌳 Features: Nested outline, Search, Expand/Collapse, Clickable links")
    print(f"🎯 Compare with JSON Hero to verify complete coverage!")

if __name__ == "__main__":
    create_tree_viewer()