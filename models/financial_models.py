from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
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