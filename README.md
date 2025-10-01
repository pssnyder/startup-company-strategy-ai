# Project Phoenix: Startup Company AI Advisor

An intelligent AI-powered strategic advisor for the business simulation game "Startup Company". This tool analyzes your game saves and provides comprehensive strategic recommendations using Google's Gemini AI.

## 🎯 Features

- **Save File Analysis**: Parse Startup Company save files to extract game state
- **Strategic Insights**: AI-powered analysis of business metrics and performance  
- **Risk Assessment**: Identify critical issues like low user satisfaction or cash flow problems
- **Production Planning**: Optimize resource allocation and component production
- **Financial Analysis**: Track runway, burn rate, and financial health
- **Actionable Recommendations**: Get specific, prioritized action plans

## 🏗️ Architecture

The system follows a clean 5-layer architecture:

1. **Data Layer**: Static game rules and mechanics from the wiki
2. **Input Layer**: Save file parsing and data extraction  
3. **Calculation Layer**: Game state analysis and metrics computation
4. **Strategy Layer**: AI-powered strategic recommendations via Gemini
5. **Presentation Layer**: Dashboard-ready data formatting

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/pssnyder/startup-company-strategy-ai
cd startup-company-strategy-ai

# Install dependencies
pip install -r requirements.txt
```

### Real-Time Game Companion (Recommended)

Start the real-time monitoring dashboard while playing:

```bash
# Set your Gemini API key (optional but recommended)
export GEMINI_API_KEY="your-api-key-here"

# Start real-time monitoring
python startup_monitor.py
```

This creates a **live game companion** that:
- 🔄 **Auto-monitors** your game's autosave files
- 📊 **Real-time alerts** for critical issues (low satisfaction, cash flow)
- 📈 **Trend analysis** tracks your progress over time
- 🤖 **AI insights** every 5 minutes with strategic recommendations
- 💾 **Historical data** logging for pattern analysis

### Manual Analysis

For one-time analysis of save files:

```python
import asyncio
from pathlib import Path
from ai_advisor.main import StartupCompanyAdvisor

async def analyze_my_game():
    # Initialize advisor
    advisor = StartupCompanyAdvisor()
    
    # Load your save file
    save_file = Path("path/to/your/save.json")
    advisor.load_save_file(save_file)
    
    # Analyze and get recommendations
    await advisor.analyze_game_state()
    advisor.print_summary_report()

# Run the analysis
asyncio.run(analyze_my_game())
```

### With AI-Powered Insights

```python
# Get a Gemini API key from Google AI Studio
advisor = StartupCompanyAdvisor(gemini_api_key="your-api-key-here")
# ... rest same as above
```

## 📁 Save File Location

Startup Company save files are typically located at:
- **Windows**: `%APPDATA%/Startup Company/saves/`
- **Mac**: `~/Library/Application Support/Startup Company/saves/`
- **Linux**: `~/.local/share/Startup Company/saves/`

Look for files named `sg_*.json`.

## 🧪 Testing

Run the example analysis with test data:

```bash
python test_example.py
```

This will:
- Create a test save file with realistic game data
- Perform a complete analysis
- Generate a detailed report
- Export results to JSON

## 📊 Output Examples

### Critical Alert Example
```
🚨 CRITICAL ALERTS:
   • User Satisfaction Crisis: User satisfaction is only 42.5% (Target: >75%)

🎯 TOP RECOMMENDATIONS:
   1. Fix User Satisfaction Crisis
      Upgrade Landing Page and other key features to improve satisfaction
      Expected: Increase satisfaction above 75%
      Timeframe: 24-48 hours
```

### Production Plan Example
```
⚙️ PRODUCTION PRIORITIES:
   1. Blueprint Component (1 needed)
   2. Frontend Module (1 needed) 
   3. UI Component (2 needed)
```

## 🔧 API Integration

### Gemini API Setup

1. Get an API key from [Google AI Studio](https://aistudio.google.com/)
2. Pass it to the advisor:

```python
advisor = StartupCompanyAdvisor(gemini_api_key="your-key")
```

### Dashboard Integration

Get structured data for web dashboards:

```python
dashboard_data = advisor.get_dashboard_data()
# Returns JSON-serializable dict with:
# - company_info
# - financial_metrics  
# - alerts
# - recommendations
# - production_plan
# - ai_insights
```

## 📈 Key Metrics Tracked

- **Financial Health**: Cash flow, burn rate, runway months
- **User Metrics**: Total users, satisfaction percentage, growth rate
- **Production Efficiency**: Component shortfalls, employee utilization
- **Feature Quality**: Quality/Efficiency gaps, upgrade requirements
- **Risk Assessment**: Critical alerts and risk level

## 🎮 Game Context

This advisor is designed for the business simulation game [Startup Company](https://www.startupcompanygame.com/), where you build and manage a tech startup. The game involves:

- Hiring developers, designers, and other specialists
- Building software features and products
- Managing finances and user satisfaction
- Competing with other companies
- Growing from startup to tech giant

## 🤝 Contributing

This project is part of "Project Phoenix" - contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

[Add your license here]

## 🙏 Acknowledgments

- Startup Company game by Hovgaard Games
- Game data sourced from the unofficial [Startup Company Wiki](https://startupcompany.fandom.com/wiki/Startup_Company_Wiki)
- Powered by Google's Gemini AI

---

**Project Phoenix Motto**: *Solve. The. Problem.* (By processing the data efficiently.)