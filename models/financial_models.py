from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import date

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

class Vehicle(Asset):
    def __init__(self, name: str, initial_value: float, depreciation_rate: float = 0.15):
        super().__init__(name, initial_value)
        self.depreciation_rate = depreciation_rate

    def calculate_value(self, year: int) -> float:
        return self.initial_value * (1 - self.depreciation_rate) ** year

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

    def get_balance(self, year: int) -> float:
        # Return 0 for years before the loan starts
        if year < 0:
            return 0
        # For active years, calculate remaining balance
        if year < self.term_years:
            monthly_rate = self.interest_rate / 12
            num_payments = self.term_years * 12
            payment = self.calculate_payment()
            remaining_payments = (self.term_years - year) * 12
            return (payment * ((1 - (1 + monthly_rate)**(-remaining_payments)) / monthly_rate))
        # After term ends, balance is 0
        return 0

class CarLoan(Loan):
    def __init__(self, principal: float, interest_rate: float, term_years: int = 5):
        super().__init__("Car Loan", principal, interest_rate, term_years)

class StudentLoan(Loan):
    def __init__(self, principal: float, interest_rate: float, term_years: int = 10):
        super().__init__("Student Loan", principal, interest_rate, term_years)

class Income(ABC):
    def __init__(self, name: str, annual_amount: float, growth_rate: float = 0.03, start_year: int = 0):
        self.name = name
        self.annual_amount = annual_amount
        self.growth_rate = growth_rate
        self.start_year = start_year

    def calculate_income(self, year: int) -> float:
        if year < self.start_year:
            return 0
        adjusted_year = year - self.start_year
        return self.annual_amount * (1 + self.growth_rate) ** adjusted_year

class Salary(Income):
    def __init__(self, annual_amount: float, location_adjustment: float = 1.0):
        super().__init__("Primary Income", annual_amount)
        self.location_adjustment = location_adjustment

    def calculate_income(self, year: int) -> float:
        return super().calculate_income(year) * self.location_adjustment

class SpouseIncome(Income):
    def __init__(self, annual_amount: float, location_adjustment: float = 1.0, start_year: int = 0):
        super().__init__("Spouse Income", annual_amount, start_year=start_year)
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

class Milestone:
    def __init__(self, name: str, trigger_year: int, category: str):
        self.name = name
        self.trigger_year = trigger_year
        self.category = category
        self.one_time_expense = 0.0
        self.recurring_expenses: List[Expense] = []
        self.income_adjustments: List[Income] = []
        self.assets: List[Asset] = []
        self.liabilities: List[Liability] = []

    def add_one_time_expense(self, amount: float):
        self.one_time_expense = amount

    def add_recurring_expense(self, expense: Expense):
        self.recurring_expenses.append(expense)

    def add_income_adjustment(self, income: Income):
        self.income_adjustments.append(income)

    def add_asset(self, asset: Asset):
        self.assets.append(asset)

    def add_liability(self, liability: Liability):
        self.liabilities.append(liability)

class MilestoneFactory:
    @staticmethod
    def create_marriage(trigger_year: int, cost: float = 30000, spouse_income: Optional[Income] = None) -> Milestone:
        milestone = Milestone("Marriage", trigger_year, "Family")
        milestone.add_one_time_expense(cost)
        milestone.add_recurring_expense(VariableExpense("Joint Living Expenses", 5000 * 12))
        if spouse_income:
            if isinstance(spouse_income, SpouseIncome):
                spouse_income.start_year = trigger_year
            milestone.add_income_adjustment(spouse_income)
        return milestone

    @staticmethod
    def create_child(trigger_year: int) -> Milestone:
        milestone = Milestone("New Child", trigger_year, "Family")
        milestone.add_one_time_expense(10000)  # Initial costs
        milestone.add_recurring_expense(FixedExpense("Childcare", 15000))
        milestone.add_recurring_expense(VariableExpense("Child Expenses", 10000))
        return milestone

    @staticmethod
    def create_home_purchase(trigger_year: int, home_price: float, down_payment_percentage: float = 0.20,
                           property_tax_rate: float = 0.015, insurance_rate: float = 0.005,
                           maintenance_rate: float = 0.01, appreciation_rate: float = 0.03,
                           mortgage_rate: float = 0.035) -> Milestone:
        milestone = Milestone("Home Purchase", trigger_year, "Asset")
        down_payment = home_price * down_payment_percentage
        loan_amount = home_price * (1 - down_payment_percentage)

        # Create mortgage loan
        mortgage = MortgageLoan(loan_amount, mortgage_rate)  # Configurable interest rate
        monthly_payment = mortgage.calculate_payment()

        # Add the down payment as a one-time expense with specific year
        milestone.add_one_time_expense(down_payment)

        # Add the home as an asset with configurable appreciation rate
        milestone.add_asset(Home("Primary Residence", home_price, appreciation_rate))

        # Add mortgage and recurring housing expenses
        milestone.add_liability(mortgage)
        # Add mortgage payment as a fixed expense (no inflation adjustment)
        milestone.add_recurring_expense(FixedExpense("Mortgage Payment", monthly_payment * 12, inflation_rate=0))
        # Add other housing expenses that do inflate
        milestone.add_recurring_expense(FixedExpense("Property Tax", home_price * property_tax_rate))
        milestone.add_recurring_expense(FixedExpense("Home Insurance", home_price * insurance_rate))
        milestone.add_recurring_expense(FixedExpense("Home Maintenance", home_price * maintenance_rate))

        return milestone

    @staticmethod
    def create_car_purchase(trigger_year: int, car_price: float, down_payment_percentage: float = 0.20,
                          loan_interest_rate: float = 0.045, loan_term_years: int = 5,
                          insurance_rate: float = 0.04, maintenance_rate: float = 0.033,
                          depreciation_rate: float = 0.15) -> Milestone:
        milestone = Milestone("Car Purchase", trigger_year, "Asset")
        down_payment = car_price * down_payment_percentage
        loan_amount = car_price * (1 - down_payment_percentage)

        # Add down payment as one-time expense
        milestone.add_one_time_expense(down_payment)

        # Add the car as an asset with configurable depreciation
        milestone.add_asset(Vehicle("Car", car_price, depreciation_rate))

        # Add car loan with configurable terms
        car_loan = CarLoan(loan_amount, loan_interest_rate, loan_term_years)
        milestone.add_liability(car_loan)

        # Add recurring expenses (insurance and maintenance)
        monthly_payment = car_loan.calculate_payment()
        milestone.add_recurring_expense(FixedExpense("Car Payment", monthly_payment * 12, inflation_rate=0))
        milestone.add_recurring_expense(FixedExpense("Car Insurance", car_price * insurance_rate))
        milestone.add_recurring_expense(FixedExpense("Car Maintenance", car_price * maintenance_rate))

        return milestone

    @staticmethod
    def create_grad_school(trigger_year: int, total_cost: float, years: int = 2) -> Milestone:
        milestone = Milestone("Graduate School", trigger_year, "Education")
        annual_cost = total_cost / years

        milestone.add_liability(StudentLoan(total_cost, 0.06))  # 6% interest rate
        milestone.add_recurring_expense(FixedExpense("Graduate School Expenses", annual_cost))
        # Potential income increase after graduation
        milestone.add_income_adjustment(Salary(30000, 1.0))  # Average salary increase post-grad
        return milestone