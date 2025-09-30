"""
Real-time dashboard data processor for Startup Company save files.
Analyzes trends, generates alerts, and prepares data for visualization.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import streamlit as st

@dataclass
class TrendAlert:
    """Represents a trend-based alert or insight."""
    level: str  # 'critical', 'warning', 'info'
    title: str
    message: str
    timestamp: datetime
    metric: str
    current_value: Any
    trend_direction: str  # 'up', 'down', 'stable'

@dataclass
class GameMetrics:
    """Current game state metrics."""
    timestamp: datetime
    game_date: str
    balance: float
    total_users: int
    satisfaction: float
    total_employees: int
    features_count: int
    monthly_expenses: float
    runway_months: float
    burn_rate: float
    user_growth_rate: float

class RealTimeDashboard:
    """Processes logged game data to generate real-time insights."""
    
    def __init__(self, data_directory: str = "game_saves"):
        self.data_directory = Path(data_directory)
        self.metrics_file = self.data_directory / "metrics_timeline.jsonl"
        
    def load_metrics_timeline(self, hours_back: int = 24) -> pd.DataFrame:
        """Load recent metrics from the timeline."""
        if not self.metrics_file.exists():
            return pd.DataFrame()
            
        # Load all metrics
        metrics = []
        with open(self.metrics_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    metrics.append(data)
                except json.JSONDecodeError:
                    continue
        
        if not metrics:
            return pd.DataFrame()
            
        df = pd.DataFrame(metrics)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter to recent data
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        df = df[df['timestamp'] >= cutoff_time]
        
        return df.sort_values('timestamp')
    
    def get_current_state(self) -> Optional[GameMetrics]:
        """Get the most recent game state."""
        df = self.load_metrics_timeline(hours_back=1)
        
        if df.empty:
            return None
            
        latest = df.iloc[-1]
        
        # Calculate derived metrics
        burn_rate = self._calculate_burn_rate(df)
        runway_months = latest['balance'] / abs(burn_rate) if burn_rate < 0 else float('inf')
        user_growth_rate = self._calculate_user_growth_rate(df)
        
        return GameMetrics(
            timestamp=latest['timestamp'],
            game_date=latest['game_date'],
            balance=latest['balance'],
            total_users=latest['total_users'],
            satisfaction=latest['satisfaction'],
            total_employees=latest['total_employees'],
            features_count=latest['features_count'],
            monthly_expenses=latest['monthly_expenses'],
            runway_months=runway_months,
            burn_rate=burn_rate,
            user_growth_rate=user_growth_rate
        )
    
    def _calculate_burn_rate(self, df: pd.DataFrame) -> float:
        """Calculate current monthly burn rate from recent data."""
        if len(df) < 2:
            return 0.0
            
        recent_df = df.tail(10)  # Last 10 data points
        
        if len(recent_df) < 2:
            return 0.0
            
        # Calculate balance change over time
        time_diff = (recent_df.iloc[-1]['timestamp'] - recent_df.iloc[0]['timestamp']).total_seconds() / 3600  # hours
        balance_diff = recent_df.iloc[-1]['balance'] - recent_df.iloc[0]['balance']
        
        if time_diff > 0:
            hourly_rate = balance_diff / time_diff
            monthly_rate = hourly_rate * 24 * 30  # Approximate monthly rate
            return monthly_rate
            
        return 0.0
    
    def _calculate_user_growth_rate(self, df: pd.DataFrame) -> float:
        """Calculate user growth rate from recent data."""
        if len(df) < 2:
            return 0.0
            
        recent_df = df.tail(10)
        
        if len(recent_df) < 2:
            return 0.0
            
        # Calculate user growth over time
        time_diff = (recent_df.iloc[-1]['timestamp'] - recent_df.iloc[0]['timestamp']).total_seconds() / 3600  # hours
        user_diff = recent_df.iloc[-1]['total_users'] - recent_df.iloc[0]['total_users']
        
        if time_diff > 0 and recent_df.iloc[0]['total_users'] > 0:
            growth_rate = (user_diff / recent_df.iloc[0]['total_users']) * 100
            return growth_rate
            
        return 0.0
    
    def generate_alerts(self, hours_back: int = 2) -> List[TrendAlert]:
        """Generate alerts based on recent trends."""
        df = self.load_metrics_timeline(hours_back=hours_back)
        alerts = []
        
        if df.empty:
            return alerts
            
        current_metrics = self.get_current_state()
        if not current_metrics:
            return alerts
            
        # Critical satisfaction alert
        if current_metrics.satisfaction < 60:
            alerts.append(TrendAlert(
                level='critical',
                title='User Satisfaction Critical',
                message=f'Satisfaction at {current_metrics.satisfaction:.1f}% - Users may start leaving!',
                timestamp=current_metrics.timestamp,
                metric='satisfaction',
                current_value=current_metrics.satisfaction,
                trend_direction=self._get_trend_direction(df, 'satisfaction')
            ))
        
        # Cash flow warnings
        if current_metrics.runway_months < 3 and current_metrics.burn_rate < 0:
            alerts.append(TrendAlert(
                level='critical',
                title='Cash Flow Emergency',
                message=f'Only {current_metrics.runway_months:.1f} months runway remaining!',
                timestamp=current_metrics.timestamp,
                metric='balance',
                current_value=current_metrics.balance,
                trend_direction='down'
            ))
        elif current_metrics.runway_months < 6 and current_metrics.burn_rate < 0:
            alerts.append(TrendAlert(
                level='warning',
                title='Cash Flow Warning',
                message=f'Runway: {current_metrics.runway_months:.1f} months. Consider reducing expenses.',
                timestamp=current_metrics.timestamp,
                metric='balance',
                current_value=current_metrics.balance,
                trend_direction='down'
            ))
        
        # User growth stagnation
        if current_metrics.user_growth_rate < 1 and current_metrics.total_users > 100:
            alerts.append(TrendAlert(
                level='warning',
                title='User Growth Stagnant',
                message=f'User growth only {current_metrics.user_growth_rate:.1f}% - Consider marketing.',
                timestamp=current_metrics.timestamp,
                metric='total_users',
                current_value=current_metrics.total_users,
                trend_direction=self._get_trend_direction(df, 'total_users')
            ))
        
        # Positive alerts
        if current_metrics.satisfaction > 80:
            alerts.append(TrendAlert(
                level='info',
                title='High User Satisfaction',
                message=f'Excellent satisfaction at {current_metrics.satisfaction:.1f}%!',
                timestamp=current_metrics.timestamp,
                metric='satisfaction',
                current_value=current_metrics.satisfaction,
                trend_direction=self._get_trend_direction(df, 'satisfaction')
            ))
        
        return alerts
    
    def _get_trend_direction(self, df: pd.DataFrame, column: str) -> str:
        """Determine if a metric is trending up, down, or stable."""
        if len(df) < 3 or column not in df.columns:
            return 'stable'
            
        recent_values = df[column].tail(5).values
        
        if len(recent_values) < 3:
            return 'stable'
            
        # Simple trend analysis
        recent_array = np.array(recent_values, dtype=float)
        first_half = np.mean(recent_array[:len(recent_array)//2])
        second_half = np.mean(recent_array[len(recent_array)//2:])
        
        if second_half > first_half * 1.05:  # 5% threshold
            return 'up'
        elif second_half < first_half * 0.95:
            return 'down'
        else:
            return 'stable'
    
    def get_trend_data(self, metric: str, hours_back: int = 24) -> Dict[str, List]:
        """Get trend data for a specific metric suitable for charting."""
        df = self.load_metrics_timeline(hours_back=hours_back)
        
        if df.empty or metric not in df.columns:
            return {'timestamps': [], 'values': []}
            
        # Resample to reasonable intervals for charting
        df_resampled = df.set_index('timestamp').resample('5min')[metric].mean().dropna()
        
        return {
            'timestamps': [ts.isoformat() for ts in df_resampled.index],
            'values': df_resampled.values.tolist()
        }
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate all data needed for the dashboard."""
        current_state = self.get_current_state()
        alerts = self.generate_alerts()
        
        dashboard_data = {
            'current_state': current_state.__dict__ if current_state else None,
            'alerts': [
                {
                    'level': alert.level,
                    'title': alert.title,
                    'message': alert.message,
                    'metric': alert.metric,
                    'trend_direction': alert.trend_direction,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in alerts
            ],
            'trends': {
                'balance': self.get_trend_data('balance', hours_back=12),
                'satisfaction': self.get_trend_data('satisfaction', hours_back=12),
                'total_users': self.get_trend_data('total_users', hours_back=12),
                'total_employees': self.get_trend_data('total_employees', hours_back=12)
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return dashboard_data
    
    def export_dashboard_json(self, output_path: str | None = None) -> str:
        """Export dashboard data as JSON file."""
        if output_path is None:
            output_path = str(self.data_directory / "dashboard_data.json")
        
        dashboard_data = self.generate_dashboard_data()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
            
        return output_path


# Function to load the most recent save file
@st.cache_data
def load_data():
    dashboard = RealTimeDashboard()
    data = dashboard.generate_dashboard_data()
    return data

# Main dashboard layout
st.set_page_config(layout="wide")
st.title("🚀 Phoenix Dashboard: Momentum AI")

data = load_data()

if data:
    # --- Key Metrics Row ---
    st.header("Company KPIs")
    col1, col2, col3, col4 = st.columns(4)
    
    balance = data['current_state']['balance']
    research_points = data.get("researchPoints", 0)
    
    # Extract product data
    products = data.get("products", {})
    total_users = 0
    valuation = 0
    if products:
        # Assuming the first product is the main one
        main_product_id = list(products.keys())[0]
        main_product = products[main_product_id]
        total_users = main_product.get("users", {}).get("total", 0)
        valuation = main_product.get("stats", {}).get("valuation", 0)

    col1.metric("💰 Balance", f"${balance:,.2f}")
    col2.metric("🔬 Research Points", f"{research_points:,}")
    col3.metric("👥 Total Users", f"{int(total_users):,}")
    col4.metric("🏦 Valuation", f"${valuation:,.2f}")

    st.divider()

    # --- Recruitment Intelligence ---
    st.header("👨‍💼 Recruitment Intelligence")
    candidates = data.get("candidates", [])
    if candidates:
        candidate_list = []
        for c in candidates:
            # Extract negotiation data if it exists
            negotiation = c.get("negotiation", {})
            expected_salary = "N/A"
            if negotiation and negotiation.get("completed") is False and negotiation.get("offers"):
                # Find the candidate's last offer to determine their expectation
                for offer in reversed(negotiation["offers"]):
                    if offer.get("fromCandidate"):
                        expected_salary = offer.get("total", "N/A")
                        break
            
            candidate_list.append({
                "Name": c.get("name"),
                "Role": c.get("employeeTypeName"),
                "Level": c.get("level"),
                "Speed": c.get("speed"),
                "Current Salary": f"${c.get('salary', 0):,}",
                "Expected Salary": f"${expected_salary:,.0f}" if isinstance(expected_salary, (int, float)) else "N/A"
            })
        
        df_candidates = pd.DataFrame(candidate_list)
        st.dataframe(df_candidates, use_container_width=True)
    else:
        st.info("No active candidates to display.")

    st.divider()

    # --- Product & Feature Roadmap ---
    st.header("📦 Product & Feature Roadmap")
    feature_instances = data.get("featureInstances", [])
    if feature_instances:
        feature_list = []
        for f in feature_instances:
            reqs = f.get("requirements", {})
            req_str = ", ".join([f"{k}: {v}" for k, v in reqs.items()])
            feature_list.append({
                "Feature": f.get("featureName"),
                "Activated": "✅" if f.get("activated") else "❌",
                "Quality": f.get("quality", {}).get("current", 0),
                "Efficiency": f.get("efficiency", {}).get("current", 0),
                "Requirements": req_str
            })
        df_features = pd.DataFrame(feature_list)
        st.dataframe(df_features, use_container_width=True)
    else:
        st.info("No product features found.")

    st.divider()

    # --- Research & Development ---
    st.header("🔬 Research & Development")
    researched_items = data.get("researchedItems", [])
    
    st.subheader("Unlocked Technologies")
    if researched_items:
        # Display in multiple columns for better readability
        num_columns = 4
        cols = st.columns(num_columns)
        for i, item in enumerate(sorted(researched_items)):
            cols[i % num_columns].markdown(f"- {item}")
    else:
        st.info("No research completed yet.")

else:
    st.error("Could not load save game data. Ensure a valid save file is in the `save_data` directory.")