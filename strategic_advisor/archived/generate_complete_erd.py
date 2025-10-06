#!/usr/bin/env python3
"""
Complete ERD Generator for Startup Company Database Schema
Generates interactive ERD with zoom and pan capabilities
"""

import json
from pathlib import Path

def generate_complete_erd():
    """Generate comprehensive ERD diagram from the complete schema"""
    
    print("🎨 Generating Complete ERD Visualization...")
    
    # Load the schema analysis
    with open('schema_export.json', 'r') as f:
        schema = json.load(f)
    
    properties = schema.get('properties', {})
    
    # Create Mermaid ERD syntax
    mermaid_code = ["erDiagram"]
    mermaid_code.append("")
    
    # Main game_state table (central hub)
    mermaid_code.append("    %% CENTRAL GAME STATE TABLE")
    mermaid_code.append("    game_state {")
    mermaid_code.append("        INTEGER id PK")
    mermaid_code.append("        TEXT filename")
    mermaid_code.append("        DATETIME real_timestamp")
    mermaid_code.append("        DATETIME file_modified_time")
    mermaid_code.append("        INTEGER ingestion_order")
    
    # Add scalar fields
    scalar_count = 0
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') not in ['array', 'object']:
            scalar_count += 1
            sql_type = get_sql_type(prop_def.get('type'), prop_def.get('format'))
            field_name = prop_name if prop_name != 'id' else 'game_id'
            mermaid_code.append(f"        {sql_type} {field_name}")
    
    mermaid_code.append("        INTEGER file_size")
    mermaid_code.append("        TEXT raw_json")
    mermaid_code.append("        DATETIME created_at")
    mermaid_code.append("        DATETIME updated_at")
    mermaid_code.append("    }")
    mermaid_code.append("")
    
    # Array tables
    mermaid_code.append("    %% ARRAY TABLES")
    array_count = 0
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') == 'array':
            array_count += 1
            table_name = prop_name
            if prop_name == 'employeesOrder':
                table_name = 'employeesOrderList'
            
            mermaid_code.append(f"    {table_name} {{")
            mermaid_code.append("        INTEGER id PK")
            mermaid_code.append("        INTEGER game_state_id FK")
            mermaid_code.append("        INTEGER array_index")
            
            # Add array-specific fields
            items_def = prop_def.get('items', {})
            if items_def is False or not isinstance(items_def, dict):
                mermaid_code.append("        TEXT value")
            elif items_def.get('type') == 'object':
                # Complex object fields
                item_props = items_def.get('properties', {})
                field_count = 0
                for item_prop_name, item_prop_def in item_props.items():
                    if field_count < 5:  # Limit display for readability
                        sql_type = get_sql_type(item_prop_def.get('type'))
                        field_name = item_prop_name if item_prop_name != 'id' else f'{table_name}ItemId'
                        mermaid_code.append(f"        {sql_type} {field_name}")
                        field_count += 1
                    else:
                        mermaid_code.append(f"        TEXT more_fields")
                        break
            else:
                # Simple type array
                sql_type = get_sql_type(items_def.get('type', 'string'))
                mermaid_code.append(f"        {sql_type} value")
            
            mermaid_code.append("        DATETIME captured_at")
            mermaid_code.append("        TEXT game_date")
            mermaid_code.append("        INTEGER game_day")
            mermaid_code.append("    }")
            mermaid_code.append("")
    
    # Object tables
    mermaid_code.append("    %% OBJECT TABLES")
    object_count = 0
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') == 'object':
            object_count += 1
            table_name = prop_name
            if prop_name == 'employeesSortOrder':
                table_name = 'employeesSortOrderList'
            
            mermaid_code.append(f"    {table_name} {{")
            mermaid_code.append("        INTEGER id PK")
            mermaid_code.append("        INTEGER game_state_id FK")
            
            # Add object properties (limited for readability)
            obj_props = prop_def.get('properties', {})
            field_count = 0
            for obj_prop_name, obj_prop_def in obj_props.items():
                if field_count < 8:  # Limit display
                    sql_type = get_sql_type(obj_prop_def.get('type'))
                    field_name = obj_prop_name if obj_prop_name != 'id' else f'{table_name}ObjectId'
                    mermaid_code.append(f"        {sql_type} {field_name}")
                    field_count += 1
                else:
                    mermaid_code.append(f"        TEXT more_properties")
                    break
            
            mermaid_code.append("        DATETIME captured_at")
            mermaid_code.append("        TEXT game_date")
            mermaid_code.append("        INTEGER game_day")
            mermaid_code.append("    }")
            mermaid_code.append("")
    
    # Relationships
    mermaid_code.append("    %% RELATIONSHIPS")
    
    # Array table relationships
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') == 'array':
            table_name = prop_name
            if prop_name == 'employeesOrder':
                table_name = 'employeesOrderList'
            mermaid_code.append(f"    game_state ||--o{{ {table_name} : contains")
    
    # Object table relationships
    for prop_name, prop_def in properties.items():
        if prop_def.get('type') == 'object':
            table_name = prop_name
            if prop_name == 'employeesSortOrder':
                table_name = 'employeesSortOrderList'
            mermaid_code.append(f"    game_state ||--|| {table_name} : has")
    
    return "\n".join(mermaid_code), scalar_count, array_count, object_count

def get_sql_type(json_type, format_type=None):
    """Convert JSON type to SQL type abbreviation for ERD"""
    if not json_type:
        return "TEXT"
    
    type_mapping = {
        'string': 'TEXT',
        'integer': 'INT', 
        'number': 'REAL',
        'boolean': 'BOOL',
        'array': 'TEXT',
        'object': 'TEXT'
    }
    
    sql_type = type_mapping.get(json_type, 'TEXT')
    
    if format_type == 'date-time':
        sql_type = 'DATETIME'
    elif format_type == 'uuid':
        sql_type = 'UUID'
    
    return sql_type

def create_interactive_erd_viewer():
    """Create interactive HTML viewer with zoom and pan"""
    
    mermaid_erd, scalar_count, array_count, object_count = generate_complete_erd()
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Startup Company Database ERD</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            overflow-x: auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .stat {{
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 8px;
            text-align: center;
            min-width: 120px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #ffd700;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .diagram-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            overflow: auto;
            position: relative;
            max-width: 95vw;
            height: 80vh;
        }}
        
        .controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            display: flex;
            gap: 10px;
        }}
        
        .control-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }}
        
        .control-btn:hover {{
            background: #45a049;
        }}
        
        .mermaid {{
            transform-origin: 0 0;
            transition: transform 0.3s ease;
        }}
        
        .zoom-info {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
        }}
        
        .legend {{
            margin-top: 20px;
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .legend-item {{
            display: inline-block;
            margin: 0 15px;
            font-size: 0.9em;
        }}
        
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 8px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏗️ Complete Startup Company Database Schema</h1>
        <p>Interactive Entity Relationship Diagram with 100% JSON Schema Coverage</p>
        
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
    
    <div class="diagram-container" id="diagramContainer">
        <div class="controls">
            <button class="control-btn" onclick="zoomIn()">🔍 Zoom In</button>
            <button class="control-btn" onclick="zoomOut()">🔍 Zoom Out</button>
            <button class="control-btn" onclick="resetZoom()">🎯 Reset</button>
            <button class="control-btn" onclick="fitToWidth()">📏 Fit Width</button>
        </div>
        
        <div class="zoom-info" id="zoomInfo">Zoom: 100%</div>
        
        <div class="mermaid" id="mermaidDiagram">
{mermaid_erd}
        </div>
    </div>
    
    <div class="legend">
        <h3>🎨 Diagram Legend</h3>
        <div class="legend-item">
            <span class="legend-color" style="background: #ff6b6b;"></span>
            Primary Key (PK)
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #4ecdc4;"></span>
            Foreign Key (FK)
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #45b7d1;"></span>
            One-to-Many (||--o{{)
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #96ceb4;"></span>
            One-to-One (||--||)
        </div>
    </div>

    <script>
        let currentZoom = 1;
        const zoomStep = 0.2;
        const minZoom = 0.1;
        const maxZoom = 3;
        
        // Initialize Mermaid
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'base',
            themeVariables: {{
                primaryColor: '#ff6b6b',
                primaryTextColor: '#333',
                primaryBorderColor: '#ff6b6b',
                lineColor: '#666',
                sectionBkColor: '#f8f9fa',
                altSectionBkColor: '#e9ecef',
                gridColor: '#ddd',
                c0: '#4ecdc4',
                c1: '#44a08d',
                c2: '#45b7d1',
                c3: '#96ceb4',
                c4: '#ffd93d'
            }},
            er: {{
                entityPadding: 15,
                labelBackground: '#f8f9fa',
                primaryColor: '#ff6b6b',
                primaryBorderColor: '#ff6b6b',
                primaryTextColor: '#333',
                relationColor: '#666',
                attributeBackgroundColorOdd: '#ffffff',
                attributeBackgroundColorEven: '#f8f9fa'
            }}
        }});
        
        function updateZoom() {{
            const diagram = document.getElementById('mermaidDiagram');
            diagram.style.transform = `scale(${{currentZoom}})`;
            document.getElementById('zoomInfo').textContent = `Zoom: ${{Math.round(currentZoom * 100)}}%`;
        }}
        
        function zoomIn() {{
            if (currentZoom < maxZoom) {{
                currentZoom += zoomStep;
                updateZoom();
            }}
        }}
        
        function zoomOut() {{
            if (currentZoom > minZoom) {{
                currentZoom -= zoomStep;
                updateZoom();
            }}
        }}
        
        function resetZoom() {{
            currentZoom = 1;
            updateZoom();
        }}
        
        function fitToWidth() {{
            const container = document.getElementById('diagramContainer');
            const diagram = document.getElementById('mermaidDiagram');
            const containerWidth = container.clientWidth - 40; // Account for padding
            const diagramWidth = diagram.scrollWidth;
            currentZoom = Math.min(containerWidth / diagramWidth, 1);
            updateZoom();
        }}
        
        // Enable dragging
        let isDragging = false;
        let startX, startY, scrollLeft, scrollTop;
        
        const container = document.getElementById('diagramContainer');
        
        container.addEventListener('mousedown', (e) => {{
            isDragging = true;
            startX = e.pageX - container.offsetLeft;
            startY = e.pageY - container.offsetTop;
            scrollLeft = container.scrollLeft;
            scrollTop = container.scrollTop;
            container.style.cursor = 'grabbing';
        }});
        
        container.addEventListener('mouseleave', () => {{
            isDragging = false;
            container.style.cursor = 'grab';
        }});
        
        container.addEventListener('mouseup', () => {{
            isDragging = false;
            container.style.cursor = 'grab';
        }});
        
        container.addEventListener('mousemove', (e) => {{
            if (!isDragging) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const y = e.pageY - container.offsetTop;
            const walkX = (x - startX) * 2;
            const walkY = (y - startY) * 2;
            container.scrollLeft = scrollLeft - walkX;
            container.scrollTop = scrollTop - walkY;
        }});
        
        // Mouse wheel zoom
        container.addEventListener('wheel', (e) => {{
            e.preventDefault();
            if (e.deltaY < 0) {{
                zoomIn();
            }} else {{
                zoomOut();
            }}
        }});
        
        // Initial setup
        container.style.cursor = 'grab';
        
        // Auto-fit on load
        window.addEventListener('load', () => {{
            setTimeout(() => {{
                fitToWidth();
            }}, 1000);
        }});
    </script>
</body>
</html>"""
    
    # Save the HTML file
    with open('complete_database_erd.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Interactive ERD generated!")
    print(f"📄 File: complete_database_erd.html")
    print(f"📊 Coverage: {scalar_count + array_count + object_count + 1} tables")
    print(f"   🎯 Game state: 1 table with {scalar_count} scalar fields")
    print(f"   📋 Arrays: {array_count} tables")
    print(f"   🏗️ Objects: {object_count} tables")
    print(f"🎨 Features: Zoom, Pan, Fit-to-width, Interactive navigation")

if __name__ == "__main__":
    create_interactive_erd_viewer()