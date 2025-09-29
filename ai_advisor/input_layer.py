"""
Input Layer: Save File Parser

This module handles parsing Startup Company save files (sg_*.json) to extract
current game state data for analysis.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GameMetrics:
    """Current game state metrics extracted from save file."""
    cash_on_hand: float
    monthly_burn_rate: float
    runway_months: float
    total_users: int
    user_satisfaction: float
    total_employees: int
    game_date: str
    company_name: str


@dataclass
class FeatureInstance:
    """Current state of a feature in the game."""
    name: str
    current_quality: int
    max_quality: int
    current_efficiency: int
    max_efficiency: int
    level: int


@dataclass
class EmployeeData:
    """Current employee data from save file."""
    name: str
    employee_type: str
    level: str
    salary: float
    productivity: float
    mood: float
    current_task: Optional[str] = None


@dataclass
class InventoryItem:
    """Inventory item with quantity."""
    item_name: str
    quantity: int


class SaveFileParser:
    """Parses Startup Company save files to extract game state."""
    
    def __init__(self):
        self.raw_data: Dict[str, Any] = {}
        self.metrics: Optional[GameMetrics] = None
        self.features: List[FeatureInstance] = []
        self.employees: List[EmployeeData] = []
        self.inventory: List[InventoryItem] = []
    
    def load_save_file(self, file_path: Path) -> bool:
        """Load and parse a save file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            
            self._extract_metrics()
            self._extract_features()
            self._extract_employees()
            self._extract_inventory()
            
            return True
        except Exception as e:
            print(f"Error loading save file: {e}")
            return False
    
    def _extract_metrics(self):
        """Extract key metrics from the save file."""
        try:
            # Basic financials
            cash = self.raw_data.get('balance', 0.0)
            
            # Calculate burn rate from employee salaries and expenses
            monthly_expenses = self._calculate_monthly_expenses()
            monthly_income = self._calculate_monthly_income()
            burn_rate = monthly_expenses - monthly_income
            
            # Calculate runway
            runway = cash / burn_rate if burn_rate > 0 else float('inf')
            
            # User metrics from first product (assuming single product for now)
            products = self.raw_data.get('progress', {}).get('products', [])
            total_users = 0
            satisfaction = 0.0
            if products:
                product = products[0]
                total_users = product.get('users', {}).get('total', 0)
                satisfaction = product.get('users', {}).get('satisfaction', 0.0)
            
            # Employee count
            workstations = self.raw_data.get('office', {}).get('workstations', [])
            total_employees = sum(1 for ws in workstations if ws.get('employee'))
            
            # Game metadata
            game_date = self.raw_data.get('date', 'Unknown')
            company_name = self.raw_data.get('companyName', 'Unknown Company')
            
            self.metrics = GameMetrics(
                cash_on_hand=cash,
                monthly_burn_rate=burn_rate,
                runway_months=runway,
                total_users=total_users,
                user_satisfaction=satisfaction,
                total_employees=total_employees,
                game_date=game_date,
                company_name=company_name
            )
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            self.metrics = None
    
    def _calculate_monthly_expenses(self) -> float:
        """Calculate total monthly expenses."""
        expenses = 0.0
        
        # Employee salaries
        workstations = self.raw_data.get('office', {}).get('workstations', [])
        for ws in workstations:
            employee = ws.get('employee')
            if employee:
                expenses += employee.get('salary', 0.0)
        
        # Office rent and other fixed costs
        # TODO: Extract from save file structure when available
        
        return expenses
    
    def _calculate_monthly_income(self) -> float:
        """Calculate total monthly income."""
        # TODO: Extract from product revenue and ad contracts
        return 0.0
    
    def _extract_features(self):
        """Extract current feature states."""
        self.features = []
        try:
            feature_instances = self.raw_data.get('featureInstances', [])
            for feature_data in feature_instances:
                feature = FeatureInstance(
                    name=feature_data.get('featureName', 'Unknown'),
                    current_quality=feature_data.get('quality', {}).get('current', 0),
                    max_quality=feature_data.get('quality', {}).get('max', 100),
                    current_efficiency=feature_data.get('efficiency', {}).get('current', 0),
                    max_efficiency=feature_data.get('efficiency', {}).get('max', 100),
                    level=feature_data.get('level', 1)
                )
                self.features.append(feature)
        except Exception as e:
            print(f"Error extracting features: {e}")
    
    def _extract_employees(self):
        """Extract employee data."""
        self.employees = []
        try:
            workstations = self.raw_data.get('office', {}).get('workstations', [])
            for ws in workstations:
                employee_data = ws.get('employee')
                if employee_data:
                    employee = EmployeeData(
                        name=employee_data.get('name', 'Unknown'),
                        employee_type=employee_data.get('type', 'Unknown'),
                        level=employee_data.get('level', 'Beginner'),
                        salary=employee_data.get('salary', 0.0),
                        productivity=employee_data.get('productivity', 100.0),
                        mood=employee_data.get('mood', 100.0),
                        current_task=employee_data.get('currentTask')
                    )
                    self.employees.append(employee)
        except Exception as e:
            print(f"Error extracting employees: {e}")
    
    def _extract_inventory(self):
        """Extract current inventory."""
        self.inventory = []
        try:
            inventory_data = self.raw_data.get('inventory', {})
            for item_name, quantity in inventory_data.items():
                if quantity > 0:
                    self.inventory.append(InventoryItem(item_name, quantity))
        except Exception as e:
            print(f"Error extracting inventory: {e}")
    
    def get_feature_by_name(self, feature_name: str) -> Optional[FeatureInstance]:
        """Get a specific feature by name."""
        for feature in self.features:
            if feature.name.lower() == feature_name.lower():
                return feature
        return None
    
    def get_employees_by_type(self, employee_type: str) -> List[EmployeeData]:
        """Get all employees of a specific type."""
        return [emp for emp in self.employees if emp.employee_type.lower() == employee_type.lower()]
    
    def get_inventory_quantity(self, item_name: str) -> int:
        """Get quantity of a specific inventory item."""
        for item in self.inventory:
            if item.item_name.lower() == item_name.lower():
                return item.quantity
        return 0
    
    def is_critical_satisfaction(self, threshold: float = 50.0) -> bool:
        """Check if user satisfaction is critically low."""
        return self.metrics is not None and self.metrics.user_satisfaction < threshold
    
    def is_low_runway(self, threshold_months: float = 3.0) -> bool:
        """Check if financial runway is critically low."""
        return self.metrics is not None and self.metrics.runway_months < threshold_months