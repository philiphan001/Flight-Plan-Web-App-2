"""Factory class for creating different types of financial milestones"""
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Milestone:
    """Base milestone class"""
    trigger_year: int
    name: str
    type: str
    
    def __post_init__(self):
        self.creation_date = datetime.now()
        self.assets = []
        self.liabilities = []
        self.recurring_expenses = []
        self.one_time_expenses = []

class MilestoneFactory:
    """Factory class for creating different types of milestones"""
    
    @staticmethod
    def create_milestone(**kwargs) -> Milestone:
        """
        Create a milestone based on the provided type.
        
        Args:
            **kwargs: Milestone parameters including type, year, and type-specific parameters
            
        Returns:
            Milestone object of the appropriate type
        """
        milestone_type = kwargs.get('type')
        year = kwargs.get('year')
        
        if milestone_type == "Marriage":
            return MilestoneFactory.create_marriage(
                year,
                kwargs.get('wedding_cost', 0),
                kwargs.get('spouse_income', None),
                kwargs.get('lifestyle_adjustment', 0),
                kwargs.get('initial_savings', 0),
                kwargs.get('initial_debt', 0),
                kwargs.get('insurance_cost', 0)
            )
        elif milestone_type == "Home":
            return MilestoneFactory.create_home_purchase(
                year,
                kwargs.get('home_cost', 0),
                kwargs.get('down_payment', 0.2),
                kwargs.get('monthly_utilities', 0),
                kwargs.get('monthly_hoa', 0),
                kwargs.get('annual_renovation', 0),
                kwargs.get('home_office_deduction', False),
                kwargs.get('office_percentage', 0)
            )
        elif milestone_type == "Education":
            return MilestoneFactory.create_education(
                year,
                kwargs.get('total_cost', 0),
                kwargs.get('program_years', 1),
                kwargs.get('institution_name', ""),
                kwargs.get('location', ""),
                kwargs.get('is_undergraduate', True),
                kwargs.get('pre_projection', False)
            )
        else:
            raise ValueError(f"Unknown milestone type: {milestone_type}")
    
    @staticmethod
    def create_marriage(year: int, wedding_cost: float, spouse_income: Optional[Dict] = None,
                       lifestyle_adjustment: float = 0, initial_savings: float = 0,
                       initial_debt: float = 0, insurance_cost: float = 0) -> Milestone:
        """Create a marriage milestone"""
        milestone = Milestone(year, "Marriage", "Marriage")
        milestone.wedding_cost = wedding_cost
        milestone.spouse_income = spouse_income
        milestone.lifestyle_adjustment = lifestyle_adjustment
        milestone.spouse_savings = initial_savings
        milestone.spouse_debt = initial_debt
        milestone.insurance_cost = insurance_cost
        return milestone
    
    @staticmethod
    def create_home_purchase(year: int, home_price: float, down_payment_pct: float,
                           monthly_utilities: float = 0, monthly_hoa: float = 0,
                           annual_renovation: float = 0, home_office_deduction: bool = False,
                           office_percentage: float = 0) -> Milestone:
        """Create a home purchase milestone"""
        milestone = Milestone(year, "Home Purchase", "Home")
        milestone.home_price = home_price
        milestone.down_payment_percentage = down_payment_pct
        milestone.monthly_utilities = monthly_utilities
        milestone.monthly_hoa = monthly_hoa
        milestone.annual_renovation = annual_renovation
        milestone.home_office_deduction = home_office_deduction
        milestone.office_percentage = office_percentage
        return milestone
    
    @staticmethod
    def create_education(year: int, total_cost: float, program_years: int,
                        institution_name: str = "", location: str = "",
                        is_undergraduate: bool = True,
                        pre_projection: bool = False) -> Milestone:
        """Create an education milestone"""
        name = f"Education: {institution_name}" if institution_name else "Education"
        milestone = Milestone(year, name, "Education")
        milestone.total_cost = total_cost
        milestone.program_years = program_years
        milestone.institution_name = institution_name
        milestone.location = location
        milestone.is_undergraduate = is_undergraduate
        milestone.pre_projection = pre_projection
        return milestone 