# Streamlit Cloud Deployment Notes

## Data Source Fallback System

The dashboard now implements a robust 3-tier fallback system for data sources:

### Priority 1: Live Game File (Local Development Only)
- **Path**: `C:\Users\patss\Saved Games\Startup Company\testing_v1\sg_momentum ai.json`
- **Features**: Auto-sync with file watching, real-time updates
- **Status**: 🔄 Live Sync Active

### Priority 2: Local Backup Copy (Both Local & Cloud)
- **Path**: `live_analytics/save_data/sg_momentum ai.json`
- **Features**: Cached copy for reliability, works on Streamlit Cloud
- **Status**: 📁 Local Backup or ☁️ Cloud Backup

### Priority 3: Direct Game File Read (Local Fallback)
- **Path**: Same as Priority 1 but without sync
- **Features**: Direct read if sync fails
- **Status**: 📂 Game File (Direct)

## Deployment Strategy

### Local Development
1. **Auto-detection**: System detects local environment automatically
2. **Live monitoring**: Watches game save file for changes
3. **Auto-refresh**: Dashboard updates when game saves
4. **Fallback**: Uses backup copy if live file unavailable

### Streamlit Cloud Deployment
1. **Cloud mode**: Auto-detects cloud environment
2. **Backup file**: Uses `save_data/sg_momentum ai.json` as data source
3. **Placeholder creation**: Creates minimal data if no backup exists
4. **Manual refresh**: Users can refresh data manually

## Data Sync Workflow

```
Local Development:
Game Save → File Watcher → Auto-sync → Local Backup → Dashboard

Cloud Deployment:
Manual Upload → Local Backup → Dashboard
```

## Debug Features

- **Data Source Verification**: Available in sidebar debug panel
- **Environment Status**: Shows current data source and sync status
- **Manual Refresh**: Force reload data with button
- **Source Details**: Expandable info showing exact file paths

## File Upload for Cloud (Future Enhancement)

For cloud deployment, consider adding:
1. File upload widget in sidebar
2. Drag-and-drop save file import
3. Cloud storage integration (AWS S3, Google Drive)
4. Automatic sync via API webhooks