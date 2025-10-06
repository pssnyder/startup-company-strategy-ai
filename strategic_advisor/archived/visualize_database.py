#!/usr/bin/env python3
"""
Database Schema Visualization for Momentum AI Temporal Database
Generate ER diagrams and relationship analysis
"""

import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

class DatabaseSchemaAnalyzer:
    """Analyze and visualize SQLite database schema"""
    
    def __init__(self, db_path: str = "momentum_ai_historical.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get comprehensive table information"""
        
        cursor = self.connection.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        table_info = {}
        
        for table in tables:
            # Get column information
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default': col[4],
                    'primary_key': bool(col[5])
                })
            
            # Get foreign key information
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            foreign_keys = []
            for fk in cursor.fetchall():
                foreign_keys.append({
                    'id': fk[0],
                    'seq': fk[1],
                    'table': fk[2],
                    'from_column': fk[3],
                    'to_column': fk[4],
                    'on_update': fk[5],
                    'on_delete': fk[6],
                    'match': fk[7]
                })
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table})")
            indexes = []
            for idx in cursor.fetchall():
                cursor.execute(f"PRAGMA index_info({idx[1]})")
                index_columns = [col[2] for col in cursor.fetchall()]
                indexes.append({
                    'name': idx[1],
                    'unique': bool(idx[2]),
                    'columns': index_columns
                })
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            
            table_info[table] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes,
                'row_count': row_count
            }
        
        return table_info
    
    def analyze_relationships(self, table_info: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Analyze relationships between tables"""
        
        relationships = {
            'foreign_key_relationships': [],
            'implied_relationships': [],
            'temporal_relationships': []
        }
        
        # Foreign key relationships
        for table_name, info in table_info.items():
            for fk in info['foreign_keys']:
                relationships['foreign_key_relationships'].append({
                    'from_table': table_name,
                    'from_column': fk['from_column'],
                    'to_table': fk['table'],
                    'to_column': fk['to_column'],
                    'relationship_type': 'foreign_key'
                })
        
        # Implied relationships (common column names)
        common_id_patterns = ['save_file_id', 'game_day', 'day']
        
        for pattern in common_id_patterns:
            tables_with_pattern = []
            for table_name, info in table_info.items():
                for col in info['columns']:
                    if pattern in col['name'].lower():
                        tables_with_pattern.append({
                            'table': table_name,
                            'column': col['name']
                        })
            
            # Create implied relationships
            if len(tables_with_pattern) > 1:
                for i, table1 in enumerate(tables_with_pattern):
                    for table2 in tables_with_pattern[i+1:]:
                        relationships['implied_relationships'].append({
                            'table1': table1['table'],
                            'column1': table1['column'],
                            'table2': table2['table'],
                            'column2': table2['column'],
                            'pattern': pattern,
                            'relationship_type': 'implied'
                        })
        
        # Temporal relationships (time-based connections)
        temporal_tables = []
        for table_name, info in table_info.items():
            has_temporal = any(
                col['name'] in ['game_day', 'day', 'real_timestamp', 'game_date']
                for col in info['columns']
            )
            if has_temporal:
                temporal_tables.append(table_name)
        
        for i, table1 in enumerate(temporal_tables):
            for table2 in temporal_tables[i+1:]:
                relationships['temporal_relationships'].append({
                    'table1': table1,
                    'table2': table2,
                    'relationship_type': 'temporal',
                    'description': 'Time-based relationship for temporal analysis'
                })
        
        return relationships
    
    def generate_text_er_diagram(self) -> str:
        """Generate a text-based ER diagram"""
        
        table_info = self.get_table_info()
        relationships = self.analyze_relationships(table_info)
        
        diagram = []
        diagram.append("🗄️ MOMENTUM AI TEMPORAL DATABASE - ENTITY RELATIONSHIP DIAGRAM")
        diagram.append("=" * 80)
        diagram.append("")
        
        # Tables overview
        diagram.append("📊 TABLES OVERVIEW")
        diagram.append("-" * 50)
        for table_name, info in table_info.items():
            diagram.append(f"📋 {table_name.upper()}")
            diagram.append(f"   📊 Rows: {info['row_count']:,}")
            diagram.append(f"   🔗 Columns: {len(info['columns'])}")
            diagram.append(f"   🔑 Foreign Keys: {len(info['foreign_keys'])}")
            diagram.append(f"   📇 Indexes: {len(info['indexes'])}")
            diagram.append("")
        
        # Detailed table schemas
        diagram.append("🏗️ DETAILED SCHEMA")
        diagram.append("-" * 50)
        
        for table_name, info in table_info.items():
            diagram.append(f"")
            diagram.append(f"📋 TABLE: {table_name.upper()}")
            diagram.append(f"├─ Row Count: {info['row_count']:,}")
            diagram.append(f"├─ Columns:")
            
            for i, col in enumerate(info['columns']):
                is_last_col = i == len(info['columns']) - 1
                prefix = "└─" if is_last_col else "├─"
                
                # Column attributes
                attrs = []
                if col['primary_key']:
                    attrs.append("🔑 PK")
                if col['not_null']:
                    attrs.append("❗ NOT NULL")
                if col['default'] is not None:
                    attrs.append(f"📝 DEFAULT: {col['default']}")
                
                attr_str = f" ({', '.join(attrs)})" if attrs else ""
                diagram.append(f"│  {prefix} {col['name']}: {col['type']}{attr_str}")
            
            # Foreign keys
            if info['foreign_keys']:
                diagram.append(f"├─ Foreign Keys:")
                for i, fk in enumerate(info['foreign_keys']):
                    is_last_fk = i == len(info['foreign_keys']) - 1
                    prefix = "└─" if is_last_fk else "├─"
                    diagram.append(f"│  {prefix} {fk['from_column']} → {fk['table']}.{fk['to_column']}")
            
            # Indexes
            if info['indexes']:
                diagram.append(f"└─ Indexes:")
                for i, idx in enumerate(info['indexes']):
                    is_last_idx = i == len(info['indexes']) - 1
                    prefix = "└─" if is_last_idx else "├─"
                    unique_str = " (UNIQUE)" if idx['unique'] else ""
                    diagram.append(f"   {prefix} {idx['name']}: {', '.join(idx['columns'])}{unique_str}")
        
        # Relationships
        diagram.append("")
        diagram.append("🔗 RELATIONSHIPS")
        diagram.append("-" * 50)
        
        # Foreign key relationships
        if relationships['foreign_key_relationships']:
            diagram.append("🔑 Foreign Key Relationships:")
            for rel in relationships['foreign_key_relationships']:
                diagram.append(f"   {rel['from_table']}.{rel['from_column']} ──→ {rel['to_table']}.{rel['to_column']}")
        
        # Implied relationships
        if relationships['implied_relationships']:
            diagram.append("")
            diagram.append("🔍 Implied Relationships (Common Patterns):")
            for rel in relationships['implied_relationships']:
                diagram.append(f"   {rel['table1']}.{rel['column1']} ⟷ {rel['table2']}.{rel['column2']} (via {rel['pattern']})")
        
        # Temporal relationships
        if relationships['temporal_relationships']:
            diagram.append("")
            diagram.append("⏰ Temporal Relationships:")
            for rel in relationships['temporal_relationships']:
                diagram.append(f"   {rel['table1']} ⟷ {rel['table2']} (time-based)")
        
        return "\n".join(diagram)
    
    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid ER diagram syntax compatible with v11.12.0"""
        
        table_info = self.get_table_info()
        relationships = self.analyze_relationships(table_info)
        
        mermaid = []
        mermaid.append("erDiagram")
        mermaid.append("")
        
        # Define entities with cleaner syntax
        for table_name, info in table_info.items():
            if table_name == 'sqlite_sequence':
                continue  # Skip system table
                
            mermaid.append(f"    {table_name.upper()} {{")
            
            # Add key columns first
            for col in info['columns']:
                if col['primary_key']:
                    mermaid.append(f"        {col['type']} {col['name']} PK")
                elif any(fk['from_column'] == col['name'] for fk in info['foreign_keys']):
                    mermaid.append(f"        {col['type']} {col['name']} FK")
            
            # Add other important columns (limit to key ones for readability)
            important_cols = []
            for col in info['columns']:
                if not col['primary_key'] and not any(fk['from_column'] == col['name'] for fk in info['foreign_keys']):
                    if any(keyword in col['name'].lower() for keyword in ['name', 'balance', 'amount', 'day', 'date', 'text', 'price']):
                        important_cols.append(col)
            
            # Limit to 6 additional columns for readability
            for col in important_cols[:6]:
                mermaid.append(f"        {col['type']} {col['name']}")
            
            mermaid.append("    }")
            mermaid.append("")
        
        # Define relationships with proper syntax
        mermaid.append("    %% Primary Relationships")
        for rel in relationships['foreign_key_relationships']:
            if rel['to_table'] != 'sqlite_sequence' and rel['from_table'] != 'sqlite_sequence':
                mermaid.append(f"    {rel['to_table'].upper()} ||--o{{ {rel['from_table'].upper()} : \"has {rel['from_table']}\"")
        
        return "\n".join(mermaid)
    
    def generate_data_flow_diagram(self) -> str:
        """Generate data flow analysis"""
        
        table_info = self.get_table_info()
        
        diagram = []
        diagram.append("📊 DATA FLOW ANALYSIS")
        diagram.append("=" * 60)
        diagram.append("")
        
        # Identify core vs detail tables
        core_tables = []
        detail_tables = []
        
        for table_name, info in table_info.items():
            if 'save_files' in table_name:
                core_tables.append((table_name, info, 'Central repository'))
            elif any(fk['table'] == 'save_files' for fk in info['foreign_keys']):
                detail_tables.append((table_name, info, f"Details linked to save_files"))
            else:
                detail_tables.append((table_name, info, 'Independent data'))
        
        diagram.append("🏛️ CORE TABLES (Central Data)")
        for table_name, info, description in core_tables:
            diagram.append(f"   📋 {table_name}: {description}")
            diagram.append(f"      📊 {info['row_count']:,} records")
        
        diagram.append("")
        diagram.append("📊 DETAIL TABLES (Related Data)")
        for table_name, info, description in detail_tables:
            diagram.append(f"   📋 {table_name}: {description}")
            diagram.append(f"      📊 {info['row_count']:,} records")
        
        # Data flow paths
        diagram.append("")
        diagram.append("🔄 DATA FLOW PATHS")
        diagram.append("   Game Save File → save_files table (core)")
        diagram.append("   │")
        diagram.append("   ├─→ transactions table (financial data)")
        diagram.append("   ├─→ jeets table (social data)")  
        diagram.append("   ├─→ market_values table (market data)")
        diagram.append("   └─→ candidates table (employee data)")
        diagram.append("")
        diagram.append("⏰ TEMPORAL TRACKING")
        diagram.append("   Real Time: real_timestamp (when data captured)")
        diagram.append("   Game Time: game_day, game_date (in-game progression)")
        
        return "\n".join(diagram)
    
    def close(self):
        """Close database connection"""
        self.connection.close()

def visualize_database_schema():
    """Main function to visualize the database schema"""
    
    print("🗄️ Momentum AI Database Schema Visualization")
    print("="*70)
    
    try:
        analyzer = DatabaseSchemaAnalyzer()
        
        # Generate text ER diagram
        print("\n📋 Generating Entity Relationship Diagram...")
        er_diagram = analyzer.generate_text_er_diagram()
        print(er_diagram)
        
        print("\n" + "="*70)
        
        # Generate data flow diagram
        data_flow = analyzer.generate_data_flow_diagram()
        print(data_flow)
        
        print("\n" + "="*70)
        
        # Generate Mermaid diagram for web visualization
        print("\n🌐 MERMAID ER DIAGRAM (for web visualization)")
        print("-" * 50)
        mermaid_diagram = analyzer.generate_mermaid_diagram()
        print(mermaid_diagram)
        
        # Save diagrams to files
        with open("database_er_diagram.txt", "w", encoding="utf-8") as f:
            f.write(er_diagram)
        
        with open("database_mermaid.md", "w", encoding="utf-8") as f:
            f.write("# Momentum AI Database ER Diagram\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_diagram)
            f.write("\n```")
        
        print(f"\n💾 Diagrams saved:")
        print(f"   📄 database_er_diagram.txt (text format)")
        print(f"   📄 database_mermaid.md (web format)")
        
        analyzer.close()
        
    except Exception as e:
        print(f"❌ Error analyzing database: {str(e)}")

if __name__ == "__main__":
    visualize_database_schema()