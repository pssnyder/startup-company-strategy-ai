"""
Data Layer: Static Game Rules and Knowledge Base

This module manages the static game data extracted from the unofficial wiki.
It provides the "Known Universe" of game mechanics, rules, and constants.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ComponentRequirement:
    """Represents a component requirement for features or modules."""
    component_name: str
    quantity: int
    employee_type: str
    base_time_hours: float
    required_level: str = "Beginner"


@dataclass
class FeatureInfo:
    """Static information about a game feature."""
    name: str
    description: str
    hype_bonus: float
    cu_requirement: int
    available_for: List[str]  # Product types
    requirements: List[ComponentRequirement]


@dataclass
class EmployeeInfo:
    """Static information about employee types."""
    type_name: str
    unlock_tier: int
    base_salary_range: tuple
    components_produced: List[str]
    max_roster_size: Dict[str, int]  # level -> max employees


class GameDataManager:
    """Manages static game data from the wiki."""
    
    def __init__(self, data_file_path: Optional[Path] = None):
        self.data_file_path = data_file_path
        self.features: Dict[str, FeatureInfo] = {}
        self.employees: Dict[str, EmployeeInfo] = {}
        self.components: Dict[str, ComponentRequirement] = {}
        self._load_data()
    
    def _load_data(self):
        """Load static game data from JSON file or initialize from wiki parsing."""
        if self.data_file_path and self.data_file_path.exists():
            self._load_from_json()
        else:
            self._initialize_default_data()
    
    def _load_from_json(self):
        """Load data from existing JSON file."""
        if not self.data_file_path:
            return
        with open(self.data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load features
        for feature_data in data.get('features', []):
            requirements = [
                ComponentRequirement(**req) for req in feature_data.get('requirements', [])
            ]
            self.features[feature_data['name']] = FeatureInfo(
                name=feature_data['name'],
                description=feature_data['description'],
                hype_bonus=feature_data['hype_bonus'],
                cu_requirement=feature_data['cu_requirement'],
                available_for=feature_data['available_for'],
                requirements=requirements
            )
        
        # Load employees
        for emp_data in data.get('employees', []):
            self.employees[emp_data['type_name']] = EmployeeInfo(
                type_name=emp_data['type_name'],
                unlock_tier=emp_data['unlock_tier'],
                base_salary_range=tuple(emp_data['base_salary_range']),
                components_produced=emp_data['components_produced'],
                max_roster_size=emp_data['max_roster_size']
            )
    
    def _initialize_default_data(self):
        """Initialize with essential game data from the plan."""
        # Key features from the notebook plan
        self.features = {
            "Landing Page": FeatureInfo(
                name="Landing Page",
                description="The first page your visitors see",
                hype_bonus=10.0,
                cu_requirement=50,
                available_for=["all"],
                requirements=[
                    ComponentRequirement("UI Component", 1, "Developer", 2.0),
                    ComponentRequirement("Backend Component", 1, "Developer", 4.0),
                    ComponentRequirement("Blueprint Component", 1, "Designer", 2.0),
                    ComponentRequirement("Graphics Component", 1, "Designer", 4.0)
                ]
            ),
            "Login System": FeatureInfo(
                name="Login System",
                description="User authentication system",
                hype_bonus=14.0,
                cu_requirement=50,
                available_for=["all"],
                requirements=[
                    ComponentRequirement("Authentication Module", 1, "Lead Developer", 22.0, "Intermediate"),
                    ComponentRequirement("Backend Module", 1, "Lead Developer", 10.0),
                    ComponentRequirement("Frontend Module", 1, "Lead Developer", 21.0),
                    ComponentRequirement("Input Module", 1, "Lead Developer", 6.0)
                ]
            )
        }
        
        # Employee types from the plan
        self.employees = {
            "Developer": EmployeeInfo(
                type_name="Developer",
                unlock_tier=0,
                base_salary_range=(4000, 6000),
                components_produced=["UI Component", "Backend Component", "Network Component", "Database Component"],
                max_roster_size={"Beginner": 99, "Intermediate": 99, "Expert": 99}
            ),
            "Designer": EmployeeInfo(
                type_name="Designer",
                unlock_tier=2,
                base_salary_range=(4000, 5500),
                components_produced=["Blueprint Component", "Wireframe Component", "Graphics Component", "UI Element"],
                max_roster_size={"Beginner": 99, "Intermediate": 99, "Expert": 99}
            ),
            "Lead Developer": EmployeeInfo(
                type_name="Lead Developer",
                unlock_tier=4,
                base_salary_range=(8000, 12000),
                components_produced=["Frontend Module", "Backend Module", "Interface Module", "Authentication Module"],
                max_roster_size={"Beginner": 99, "Intermediate": 99, "Expert": 99}
            )
        }
    
    def get_feature_requirements(self, feature_name: str) -> List[ComponentRequirement]:
        """Get component requirements for a specific feature."""
        feature = self.features.get(feature_name)
        return feature.requirements if feature else []
    
    def get_employee_info(self, employee_type: str) -> Optional[EmployeeInfo]:
        """Get information about an employee type."""
        return self.employees.get(employee_type)
    
    def save_to_json(self, output_path: Path):
        """Save current data to JSON file."""
        data = {
            "features": [],
            "employees": []
        }
        
        # Convert features to dict
        for feature in self.features.values():
            feature_dict = {
                "name": feature.name,
                "description": feature.description,
                "hype_bonus": feature.hype_bonus,
                "cu_requirement": feature.cu_requirement,
                "available_for": feature.available_for,
                "requirements": [
                    {
                        "component_name": req.component_name,
                        "quantity": req.quantity,
                        "employee_type": req.employee_type,
                        "base_time_hours": req.base_time_hours,
                        "required_level": req.required_level
                    } for req in feature.requirements
                ]
            }
            data["features"].append(feature_dict)
        
        # Convert employees to dict
        for employee in self.employees.values():
            emp_dict = {
                "type_name": employee.type_name,
                "unlock_tier": employee.unlock_tier,
                "base_salary_range": list(employee.base_salary_range),
                "components_produced": employee.components_produced,
                "max_roster_size": employee.max_roster_size
            }
            data["employees"].append(emp_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)