# Strategic Advisor - Clean Architecture

## Directory Structure

```
strategic_advisor/
├── src/                    # Source code
│   ├── complete_database.py   # Main database implementation
│   ├── logger_config.py       # Logging configuration
│   ├── file_monitor.py        # File monitoring utilities
│   ├── main.py               # Main entry point
│   └── decision_modules/     # Strategic decision modules
├── config/                 # Configuration files
│   ├── complete_schema.sql    # Complete database schema
│   ├── schema_export.json     # Original JSON schema
│   └── SCHEMA_DESIGN.md      # Schema documentation
├── data/                   # Data storage
│   ├── save_files/           # Game save files
│   └── logs/                # Application logs
├── tests/                  # Test files
│   └── test_complete_integration.py
└── archived/              # Old experimental files
```

## Features

- **100% JSON Schema Coverage**: Complete database schema covering all game save file fields
- **Temporal Tracking**: Full historical data with game time and real time tracking
- **Reporting Layer Foundation**: Calculated metrics and dashboard data ready for analysis
- **Clean Architecture**: Well-organized modular code structure

## Quick Start

1. **Test the system:**
   ```bash
   cd tests
   python test_complete_integration.py
   ```

2. **Use the database:**
   ```python
   from src.complete_database import CompleteGameDatabase
   
   db = CompleteGameDatabase()
   game_state_id = db.ingest_complete_save_file(save_file_path, save_data)
   dashboard_data = db.get_dashboard_summary()
   ```

## Next Steps

1. **Reporting Views**: Define strategic insights and calculated metrics
2. **Real-time Integration**: Connect with game file monitoring
3. **Dashboard Interface**: Build visual reporting interfaces
4. **Decision Engine**: Implement strategic recommendation algorithms