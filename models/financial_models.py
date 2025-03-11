from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable
from datetime import date
from enum import Enum

class Asset(ABC):
    def __init__(self, name: str, initial_value: float):
        self.name = name
        self.initial_value = initial_value
        self.current_value = initial_value

    @abstractmethod
    def calculate_value(self, year: int) -> float:
        pass

class Home(Asset):
    def __init__(self, name: str, initial_value: float, appreciation_rate: float = 0.03):
        super().__init__(name, initial_value)
        self.appreciation_rate = appreciation_rate

    def calculate_value(self, year: int) -> float:
        return self.initial_value * (1 + self.appreciation_rate) ** year

class Investment(Asset):
    def __init__(self, name: str, initial_value: float, return_rate: float = 0.07):
        super().__init__(name, initial_value)
        self.return_rate = return_rate
        self.contributions = []  # Track yearly contributions

    def add_contribution(self, amount: float):
        self.contributions.append(amount)

    def calculate_value(self, year: int) -> float:
        if year >= len(self.contributions):
            return self.current_value

        # Calculate compound growth including contributions
        value = self.initial_value
        for i in range(year + 1):
            value = (value + self.contributions[i]) * (1 + self.return_rate)
            if i == year:
                self.current_value = value

        return self.current_value

class DepreciableAsset(Asset):
    def __init__(self, name: str, initial_value: float, depreciation_rate: float = 0.1):
        super().__init__(name, initial_value)
        self.depreciation_rate = depreciation_rate

    def calculate_value(self, year: int) -> float:
        return max(0, self.initial_value * (1 - self.depreciation_rate) ** year)

class Liability(ABC):
    def __init__(self, name: str, principal: float, interest_rate: float, term_years: int):
        self.name = name
        self.principal = principal
        self.interest_rate = interest_rate
        self.term_years = term_years

    @abstractmethod
    def calculate_payment(self) -> float:
        pass

    @abstractmethod
    def get_balance(self, year: int) -> float:
        pass

class Loan(Liability):
    def calculate_payment(self) -> float:
        monthly_rate = self.interest_rate / 12
        num_payments = self.term_years * 12
        return (self.principal * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    def get_balance(self, year: int) -> float:
        if year >= self.term_years:
            return 0
        monthly_rate = self.interest_rate / 12
        num_payments = self.term_years * 12
        payment = self.calculate_payment()
        remaining_payments = (self.term_years - year) * 12
        return (payment * ((1 - (1 + monthly_rate)**(-remaining_payments)) / monthly_rate))

class MortgageLoan(Loan):
    def __init__(self, principal: float, interest_rate: float, term_years: int = 30):
        super().__init__("Mortgage", principal, interest_rate, term_years)

class Income(ABC):
    def __init__(self, name: str, annual_amount: float, growth_rate: float = 0.03):
        self.name = name
        self.annual_amount = annual_amount
        self.growth_rate = growth_rate

    def calculate_income(self, year: int) -> float:
        return self.annual_amount * (1 + self.growth_rate) ** year

class Salary(Income):
    def __init__(self, annual_amount: float, location_adjustment: float = 1.0):
        super().__init__("Salary", annual_amount)
        self.location_adjustment = location_adjustment

    def calculate_income(self, year: int) -> float:
        return super().calculate_income(year) * self.location_adjustment

class Expense(ABC):
    def __init__(self, name: str, annual_amount: float, inflation_rate: float = 0.02):
        self.name = name
        self.annual_amount = annual_amount
        self.inflation_rate = inflation_rate

    def calculate_expense(self, year: int) -> float:
        return self.annual_amount * (1 + self.inflation_rate) ** year

class FixedExpense(Expense):
    pass

class VariableExpense(Expense):
    def __init__(self, name: str, annual_amount: float, volatility: float = 0.1):
        super().__init__(name, annual_amount)
        self.volatility = volatility

    def calculate_expense(self, year: int) -> float:
        base_expense = super().calculate_expense(year)
        return base_expense * (1 + self.volatility)
class MilestoneType(Enum):
    MARRIAGE = "Marriage"
    CHILD = "Child"
    HOME_PURCHASE = "Home Purchase"
    CAR_PURCHASE = "Car Purchase"
    PROMOTION = "Promotion"
    EDUCATION = "Education"
    RETIREMENT = "Retirement"
    CUSTOM = "Custom"

class Milestone:
    def __init__(self, name: str, year: int, milestone_type: MilestoneType, 
                 financial_impact: Dict[str, Any]):
        self.name = name
        self.year = year
        self.milestone_type = milestone_type
        self.financial_impact = financial_impact
        self.applied = False
    
    def get_financial_impact(self) -> Dict[str, Any]:
        return self.financial_impact

class MarriageMilestone(Milestone):
    def __init__(self, year: int, income_change_pct: float = 0.5, 
                 expense_change_pct: float = 0.25):
        financial_impact = {
            "income_multiplier": 1 + income_change_pct,  # e.g. spouse income
            "expense_multiplier": 1 + expense_change_pct,  # shared expenses
            "tax_status_change": True
        }
        super().__init__("Marriage", year, MilestoneType.MARRIAGE, financial_impact)

class ChildMilestone(Milestone):
    def __init__(self, year: int, annual_child_expense: float = 12000,
                 college_savings_annual: float = 2500):
        financial_impact = {
            "annual_expense_increase": annual_child_expense,
            "college_savings": college_savings_annual,
            "add_investment": {
                "name": f"College Fund (child born year {year})",
                "initial_value": 0,
                "return_rate": 0.06,
                "annual_contribution": college_savings_annual
            }
        }
        super().__init__(f"Child (Year {year})", year, MilestoneType.CHILD, financial_impact)

class HomePurchaseMilestone(Milestone):
    def __init__(self, year: int, home_value: float, down_payment_pct: float = 0.20,
                 interest_rate: float = 0.035, term_years: int = 30):
        down_payment = home_value * down_payment_pct
        loan_amount = home_value - down_payment
        financial_impact = {
            "add_asset": {
                "type": "Home",
                "name": "Primary Residence",
                "initial_value": home_value,
                "appreciation_rate": 0.03
            },
            "add_liability": {
                "type": "MortgageLoan",
                "principal": loan_amount,
                "interest_rate": interest_rate,
                "term_years": term_years
            },
            "expense_changes": {
                "property_tax": home_value * 0.01,  # Approximate property tax
                "home_insurance": home_value * 0.005,  # Approximate insurance
                "maintenance": home_value * 0.01  # Maintenance costs
            },
            "remove_expense": "Rent"  # If applicable
        }
        super().__init__("Home Purchase", year, MilestoneType.HOME_PURCHASE, financial_impact)

class CarPurchaseMilestone(Milestone):
    def __init__(self, year: int, car_value: float, down_payment_pct: float = 0.20,
                 interest_rate: float = 0.045, term_years: int = 5):
        down_payment = car_value * down_payment_pct
        loan_amount = car_value - down_payment
        financial_impact = {
            "add_asset": {
                "type": "DepreciableAsset",
                "name": f"Vehicle (purchased year {year})",
                "initial_value": car_value,
                "depreciation_rate": 0.15
            },
            "add_liability": {
                "type": "Loan",
                "name": "Auto Loan",
                "principal": loan_amount,
                "interest_rate": interest_rate,
                "term_years": term_years
            },
            "expense_changes": {
                "car_insurance": 1200,  # Annual insurance cost
                "maintenance": 800  # Annual maintenance cost
            }
        }
        super().__init__("Car Purchase", year, MilestoneType.CAR_PURCHASE, financial_impact)

class PromotionMilestone(Milestone):
    def __init__(self, year: int, salary_increase_pct: float = 0.15):
        financial_impact = {
            "income_increase_pct": salary_increase_pct
        }
        super().__init__(f"Promotion (+{int(salary_increase_pct*100)}%)", 
                        year, MilestoneType.PROMOTION, financial_impact)

class EducationMilestone(Milestone):
    def __init__(self, year: int, duration_years: int = 2, 
                 annual_tuition: float = 25000, income_reduction_pct: float = 0.5):
        financial_impact = {
            "duration_years": duration_years,
            "annual_expense": annual_tuition,
            "income_multiplier": 1 - income_reduction_pct,  # Reduced income during school
            "post_education_income_multiplier": 1.25  # Income boost after completion
        }
        super().__init__("Graduate Education", year, MilestoneType.EDUCATION, financial_impact)

class CustomMilestone(Milestone):
    def __init__(self, name: str, year: int, income_change: float = 0,
                 expense_change: float = 0, asset_change: float = 0,
                 liability_change: float = 0):
        financial_impact = {
            "income_change": income_change,
            "expense_change": expense_change,
            "asset_change": asset_change,
            "liability_change": liability_change
        }
        super().__init__(name, year, MilestoneType.CUSTOM, financial_impact)
