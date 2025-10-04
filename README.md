# Project Phoenix: Startup Company Static Evaluation Engine

A data-driven static evaluation engine for the business simulation game "Startup Company". This project demonstrates industry-standard data intelligence pipeline architecture using game data as a learning laboratory for business decision automation.

## 🎯 Project Vision & Learning Goals

This project serves as a **micro-implementation of an industry-standard data intelligence pipeline**, using the Startup Company game as a controlled environment to explore:

- **Data-Driven Decision Making**: Converting raw business data into quantifiable, actionable insights
- **Static Evaluation Engines**: Building systematic analysis frameworks with defined thresholds and triggers
- **Automated Business Intelligence**: Demonstrating input → calculation → processing → output pipelines
- **Neural Network Preparation**: Creating structured datasets and decision frameworks for future ML integration

**End Goal**: Develop a static evaluation engine so precise that it could theoretically play the game autonomously, eventually feeding this system into a neural network for hyperstrategy optimization.

## 🧠 Architecture Philosophy

### The Data Intelligence Pipeline
```
Raw Game Data → Metric Calculations → Threshold Analysis → Specific Game Actions
```

**Stage 1: Data Collection** - Save file parsing and historical data storage  
**Stage 2: Calculation Engine** - Quantitative metric computation from raw inputs  
**Stage 3: Visual Analytics** - Dashboard representation of organized data with trends  
**Stage 4: Static Evaluation** - Threshold-based analysis generating specific game actions  
**Stage 5: Neural Network Integration** - ML-driven hyperstrategy optimization (future goal)

### Core Principles
- **No Abstract Recommendations**: Only data-driven, quantifiable insights
- **Actionable Outputs**: Every analysis result maps to specific in-game actions
- **Threshold-Based Logic**: Defined numerical triggers for all decision points
- **Measurable Results**: All actions include expected metric improvements

## 🏗️ Technical Architecture

Clean 5-layer architecture designed for data flow optimization:

1. **Data Layer** (`ai_advisor/data_layer.py`) - Static game rules and constants
2. **Input Layer** (`ai_advisor/input_layer.py`) - Save file parsing & validation  
3. **Calculation Layer** (`ai_advisor/calculation_layer.py`) - Core metrics computation
4. **Strategy Layer** (`ai_advisor/strategy_layer.py`) - Static evaluation engine
5. **Presentation Layer** (`ai_advisor/dashboard.py`) - Data visualization

### Static Evaluation Engine

The core `StaticEvaluationEngine` implements the mathematical decision framework:

```python
# Example threshold-based decision making
PRODUCTION_THRESHOLDS = {
    'ui_component_min_rate': 0.4,  # components per hour
    'employee_utilization_max': 90,  # percentage
    'satisfaction_critical': 60,  # percentage
    'cu_utilization_critical': 90,  # percentage
}

# Converts threshold violations into specific game actions
if ui_production_rate < PRODUCTION_THRESHOLDS['ui_component_min_rate']:
    action = {
        'game_command': 'ADD_UI_COMPONENT_TO_WORK_QUEUE',
        'target_employee': 'developer_with_capacity',
        'expected_result': 'Increase production to ≥0.4 components/hour'
    }
```

## 📊 Live Analytics Dashboard

**Production URL**: [Project Phoenix Insights](https://project-phoenix.streamlit.app/)

The dashboard demonstrates real-time data pipeline processing with:
- **Raw Data Visualization**: Game save file metrics and trends
- **Calculated Analytics**: Production rates, utilization percentages, runway calculations
- **Threshold Monitoring**: Color-coded alerts when metrics breach defined limits
- **Action Generation**: Specific game commands triggered by data conditions

## � Running the System

### Real-Time Static Evaluation
```bash
# Start continuous evaluation engine
python startup_monitor.py
```

### Manual Analysis Mode
```python
from live_analytics.utilities.static_evaluation_engine import run_static_evaluation

# Load game data and run evaluation
result = run_static_evaluation(game_data)
print(f"Critical actions required: {result['evaluation_summary']['critical_actions_required']}")
```

### Dashboard Development
```bash
streamlit run live_analytics/dashboard.py
```

## � Data Science Components

### Metrics Calculation Engine
- **Production Rate Analysis**: Component output per hour calculations
- **Team Utilization Tracking**: Employee assignment and capacity analysis  
- **Financial Runway Modeling**: Burn rate and cash flow projections
- **Market Penetration Metrics**: User growth and satisfaction correlations

### Threshold-Based Decision Framework
- **Binary Triggers**: Clear mathematical conditions for action initiation
- **Severity Classification**: CRITICAL/HIGH/MEDIUM/LOW priority assignments
- **Expected Outcomes**: Quantified improvement targets for each action

### Historical Data Pipeline
- **Time Series Storage**: Continuous game state snapshots in JSONL format
- **Trend Analysis**: Rate of change calculations for all key metrics
- **Pattern Recognition**: Identification of recurring optimization opportunities

## 🎮 Game Context & Data Sources

**Target Game**: [Startup Company](https://www.startupcompanygame.com/) - Business simulation with rich financial and operational datasets

**Save File Location**: 
- Windows: `%APPDATA%/Startup Company/saves/sg_*.json`
- Contains comprehensive business metrics: cash flow, employee data, user satisfaction, inventory levels

**Data Structure**: JSON-based save files with nested objects representing:
- Company financials and runway
- Employee assignments and productivity
- User metrics and satisfaction scores  
- Inventory levels and production rates
- Feature development status and dependencies

## 🧪 Development & Testing

This project serves as a **demonstration of data engineering and decision automation skills** rather than a community tool. The codebase showcases:

- **ETL Pipeline Design**: Extract game data, Transform into metrics, Load into decision framework
- **Real-Time Data Processing**: File watching and streaming analytics
- **Threshold-Based Alerting**: Mathematical condition evaluation and action triggering
- **Dashboard Development**: Interactive data visualization with Streamlit
- **API Integration**: Google Gemini AI for enhanced pattern recognition

## 🔮 Future Roadmap: Neural Network Integration

Once sufficient historical data is collected, the static evaluation engine will serve as training data for:

1. **Pattern Recognition ML**: Identify optimal decision timing beyond static thresholds
2. **Hyperstrategy Development**: Neural network-driven strategy optimization
3. **Predictive Analytics**: Forecasting game outcomes based on current state
4. **Automated Decision Making**: Full autonomous game play capability

The current static evaluation engine provides the structured input/output pairs necessary for supervised learning of game strategy optimization.

---

**Learning Focus**: This project demonstrates data pipeline architecture, threshold-based decision automation, and preparation for machine learning integration in a controlled business simulation environment.
