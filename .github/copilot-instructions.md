# Project Phoenix: Startup Company AI Advisor - Coding Agent Guide

## Architecture Overview

This is a **real-time game companion** for the "Startup Company" business simulation game, built with a clean 5-layer architecture:

1. **Data Layer** (`ai_advisor/data_layer.py`) - Static game rules from wiki
2. **Input Layer** (`ai_advisor/input_layer.py`) - Save file parsing & validation  
3. **Calculation Layer** (`ai_advisor/calculation_layer.py`) - Game state analysis & metrics
4. **Strategy Layer** (`ai_advisor/strategy_layer.py`) - Google Gemini AI integration
5. **Presentation Layer** (`ai_advisor/dashboard.py`) - Dashboard data formatting

## Critical Workflow Patterns

### Entry Points & Execution Modes

- **Real-time monitoring**: `python startup_monitor.py` (primary use case)
- **Manual analysis**: Import `ai_advisor.main.StartupCompanyAdvisor` 
- **Live web dashboard**: `streamlit run live_analytics/dashboard.py`
- **Testing**: `python test_example.py` creates mock data & runs full analysis

### File Watching Architecture

The system monitors Startup Company save files using two approaches:
- **Main system**: `ai_advisor/file_watcher.py` + `ai_advisor/real_time_monitor.py` 
- **Standalone utility**: `live_analytics/utilities/update_save_data.py` (polling-based)

Both watch for changes to `sg_*.json` files and auto-detect manual vs autosave priority.

### AI Integration Pattern

```python
# Always use async for Gemini API calls
advisor = StartupCompanyAdvisor(gemini_api_key="...")
await advisor.analyze_game_state()  # Required async call
```

**Critical**: The `strategy_layer.py` requires async/await for all AI operations. Fallback mode works without API key.

## Data Flow & Dependencies

### Save File Processing Chain
```
Game Save File → SaveFileParser → GameStateAnalyzer → GeminiStrategyAdvisor → Dashboard
```

### Key Data Structures
- `SaveFileMetrics` - Core game state (cash, users, satisfaction, etc.)
- `StrategicAlert` - Critical issues (low satisfaction, cash flow)
- `AIInsight` - Complete AI analysis with recommendations

### External Dependencies
- **Google Gemini API**: Set `GEMINI_API_KEY` environment variable
- **Save file location**: `C:\Users\{user}\Saved Games\Startup Company\{company_name}\`
- **Wiki data**: Embedded in `data_layer.py` (features, employees, components)

## Project-Specific Conventions

### Error Handling Patterns
```python
# Always check save file loading success
if not advisor.load_save_file(save_path):
    raise ValueError(f"Failed to load save file: {save_path}")

# Graceful API failures
if not gemini_api_key:
    print("⚠️ No API key - using fallback analysis")
```

### File Path Management
- Use `pathlib.Path` consistently for cross-platform compatibility
- Default save locations hardcoded in `startup_monitor.py` - update for different users
- Output always goes to `game_saves/` directory (snapshots + timeline data)

### Threading Architecture
The real-time monitor uses three concurrent threads:
1. **File monitoring** - Watches for save file changes
2. **Dashboard processing** - Updates dashboard data
3. **Main analysis loop** - Runs AI analysis every 5 minutes

## Development Commands

### Environment Setup
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"  # Optional but recommended
```

### Testing & Debugging
```bash
python test_example.py          # Full test with mock data
python test_real_time.py        # Real-time monitoring test
python ai_advisor/main.py       # Direct module test
```

### Dashboard Development
```bash
streamlit run live_analytics/dashboard.py  # Web interface
```

## Integration Points & APIs

### Dashboard Data Format
The `get_dashboard_data()` method returns standardized JSON for web interfaces:
```python
{
    "company_info": {...},
    "financial_metrics": {...}, 
    "alerts": [...],
    "recommendations": [...],
    "ai_insights": {...}
}
```

### Live Analytics Connection
Two separate systems exist:
- **Main AI advisor**: Full 5-layer analysis with AI
- **Live analytics**: Streamlit dashboard with simpler metrics

They share save file monitoring but use different processing pipelines.

## Common Patterns

### Async AI Operations
```python
async def analyze_game():
    advisor = StartupCompanyAdvisor(gemini_api_key)
    advisor.load_save_file(save_path)
    await advisor.analyze_game_state()  # Always await
    return advisor.get_dashboard_data()
```

### Real-time Monitoring Setup
```python
advisor = RealTimeGameAdvisor(
    save_directory="path/to/saves",
    output_directory="game_saves", 
    gemini_api_key=api_key
)
advisor.start_monitoring(ai_analysis_interval=300)  # 5 minutes
```

### Component Production Analysis
The calculation layer identifies missing components needed for features and generates production priorities. This is core game logic that drives strategic recommendations.

## Debugging Tips

- **File permissions**: Windows save files may be locked during game writes
- **JSON parsing**: Game saves can be large (>1MB) - use error handling
- **API rate limits**: Gemini API calls are throttled - respect 5-minute intervals
- **Threading**: Use `queue.Queue()` for thread communication in real-time monitor

## Module Dependencies

Never import across layers - follow the clean architecture:
- Data layer imports nothing from other layers
- Each layer only imports from lower layers
- Main coordinator (`main.py`) orchestrates all layers