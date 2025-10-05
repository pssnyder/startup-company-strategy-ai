# Project Phoenix v2.0 - Enterprise Data Pipeline

> **🔥 Major Architecture Update**: Complete rebuild from dashboard-heavy approach to enterprise-grade cloud data pipeline with Firebase ETL processing.

## 🎯 What Changed

**Before**: Front-end heavy dashboard with abstract "creative" recommendations  
**After**: Quantitative data pipeline with Firebase ETL, static evaluation engine, and actionable game commands

## 🏗️ New Architecture

```
Game Save Files → Cloud Monitor → Firebase ETL Pipeline → Data Lake → Static Evaluation → Actions
```

### 📊 Data Flow

1. **Real-time Monitoring** (`cloud_monitor.py`)
   - Watches Startup Company save files  
   - Dual processing: Cloud ETL + Local evaluation

2. **Firebase ETL Pipeline** (`functions/index.js`)
   - Raw data ingestion → Cloud Storage archive
   - Data lake creation → Firestore collections
   - Conformed layer → Structured analytics

3. **Static Evaluation Engine** (`utilities/static_evaluation_engine.py`)
   - Threshold-based decision making
   - Quantitative game action generation
   - Zero abstract recommendations

4. **Data Lake Schema**
   ```
   raw_save_files/     → Archive with metadata
   data_lake/          → Complete game state extraction  
   conformed_data/     → Structured analytics layer
   time_series/        → Trending and historical data
   etl_queue/          → Processing coordination
   ```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login
```

### 2. Deploy Cloud Pipeline
```bash
# Deploy Firebase functions
./deploy.sh

# OR manually:
cd functions && npm install
firebase deploy --project project-phoenix-v2
```

### 3. Start Monitoring
```bash
# Update paths in cloud_monitor.py, then:
python cloud_monitor.py
```

### 4. Test Pipeline
```bash
# Run comprehensive test suite
python test_cloud_pipeline.py
```

## 📁 Key Files

| File | Purpose | Status |
|------|---------|--------|
| `cloud_monitor.py` | Main monitoring system with dual processing | ✅ Ready |
| `functions/index.js` | Firebase Cloud Functions ETL pipeline | ✅ Ready |
| `utilities/firebase_client.py` | Python → Firebase integration client | ✅ Ready |
| `utilities/static_evaluation_engine.py` | Quantitative decision engine | ✅ Ready |
| `test_cloud_pipeline.py` | Comprehensive test suite | ✅ Ready |

## 🔧 Configuration

### Firebase Setup
- **Project**: `project-phoenix-v2`
- **Functions URL**: `https://us-central1-project-phoenix-v2.cloudfunctions.net/ingestSaveFile`
- **Storage**: `project-phoenix-v2.appspot.com`

### Local Paths (Update These!)
```python
# In cloud_monitor.py
SAVE_DIRECTORY = r"C:\Users\{YOUR_USER}\Saved Games\Startup Company\{COMPANY_FOLDER}"
COMPANY_NAME = "Your Company Name"
```

## 📊 Data Pipeline Features

### 🔍 Complete Data Extraction
- **50+ game data categories** captured dynamically
- **Unknown field detection** for future game updates  
- **Time-series storage** for trending analysis
- **Metadata tracking** with save file lineage

### ⚡ Static Evaluation Engine
```python
# Threshold-based decisions (no AI fluff)
if metrics['financial']['cash_runway_days'] < 30:
    actions.append({
        'command': 'reduce_team_size',
        'target': 'lowest_performing_employees',
        'expected_result': 'Extend cash runway by 45 days'
    })
```

### 🌐 Dual Processing Architecture
- **Cloud Pipeline**: Firebase ETL for data lake and analytics
- **Local Engine**: Static evaluation for immediate actions  
- **Zero Downtime**: Local processing continues if cloud unavailable

## 🧪 Testing

### Automated Test Suite
```bash
python test_cloud_pipeline.py
```

**Tests Include**:
- ✅ Firebase connectivity
- ✅ Mock data ingestion  
- ✅ Real save file processing
- ✅ Duplicate detection
- ✅ Error handling
- ✅ Local static evaluation

### Manual Testing
```bash
# Test Firebase connection
python utilities/firebase_client.py

# Test static evaluation only  
python utilities/static_evaluation_engine.py

# Monitor save files
python cloud_monitor.py
```

## 🔥 Key Benefits

### ✅ What We Fixed
- ❌ **Removed**: Abstract recommendations like "Prepare competitive pricing proposal"
- ❌ **Removed**: Creative fluff and non-actionable content
- ❌ **Removed**: Front-end heavy dashboard calculations
- ✅ **Added**: Quantitative threshold-based decisions
- ✅ **Added**: Enterprise data lake with complete game state
- ✅ **Added**: Specific game commands with expected results

### 🎯 Actionable Output Example
```json
{
  "alerts": [
    {
      "priority": "HIGH",
      "message": "Cash runway critically low: 28 days remaining",
      "metric": "cash_runway_days",
      "threshold": 30
    }
  ],
  "actions": [
    {
      "command": "hire_developers", 
      "count": 2,
      "expected_result": "Increase feature production by 40%",
      "cost_analysis": "ROI positive in 3 months"
    }
  ]
}
```

## 🔧 Development

### Adding New Thresholds
```python
# In utilities/static_evaluation_engine.py
def _evaluate_production_metrics(self, metrics):
    if metrics['inventory_items'] < 5:
        self.actions.append({
            'command': 'increase_component_production',
            'priority': 'HIGH',
            'expected_result': 'Prevent feature development delays'
        })
```

### Extending Data Lake
```javascript
// In functions/index.js - extractAllDataPoints()
dynamicFields: extractDynamicFields(saveFileData)  // Catches unknown fields
```

## 📈 Monitoring & Logs

### Real-time Logs
```bash
# Cloud monitor logs
tail -f cloud_monitor.log

# Firebase function logs  
firebase functions:log --project project-phoenix-v2
```

### Data Lake Queries
```javascript
// Firestore console queries
db.collection('conformed_data')
  .where('financials.cashRunwayDays', '<', 30)
  .orderBy('company.extractedAt', 'desc')
```

## 🚨 Production Readiness

### Security (TODO)
- [ ] Firebase authentication rules
- [ ] API key management
- [ ] Data encryption at rest

### Monitoring
- [ ] Cloud Function error alerting
- [ ] Data lake health checks
- [ ] Performance metrics

### Scaling
- [x] Dynamic data extraction (handles unknown future fields)
- [x] Time-series storage for trending
- [x] Concurrent processing with queue management

---

## 🎉 Result

**"I want no stone unturned and no data point left out from the games save file"** ✅

- **Complete data capture**: 50+ categories with dynamic field detection
- **Quantitative decisions**: Threshold-based engine with specific game commands
- **Enterprise architecture**: Cloud ETL pipeline with proper data lake design
- **Zero creative fluff**: Only actionable, measurable recommendations

**Ready for team stand-ups with data-driven focus on adjustable work queues** 🎯