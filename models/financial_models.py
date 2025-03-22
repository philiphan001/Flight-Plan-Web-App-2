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
    def __init__(self, name: str, initial_value: float, appreciation_rate: float = 0.03,
                 down_payment_percentage: float = 0.20, monthly_utilities: float = 0,
                 monthly_hoa: float = 0, annual_renovation: float = 0,
                 home_office_deduction: bool = False, office_percentage: float = 0):
        super().__init__(name, initial_value)
        self.appreciation_rate = appreciation_rate
        self.down_payment_percentage = down_payment_percentage
        self.monthly_utilities = monthly_utilities
        self.monthly_hoa = monthly_hoa
        self.annual_renovation = annual_renovation
        self.home_office_deduction = home_office_deduction
        self.office_percentage = office_percentage

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
    def __init__(self, name: str, principal: float, interest_rate: float, term_years: int, loan_id: str = None):
        super().__init__(name, principal, interest_rate, term_years)
        self.loan_id = loan_id or f"{name}_{id(self)}"
        self._milestone = None
        self.start_year = 0

    def calculate_payment(self) -> float:
        monthly_rate = self.interest_rate / 12
        num_payments = self.term_years * 12
        return (self.principal * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    def get_balance(self, year: int) -> float:
        if year < self.start_year:
            return 0
        adjusted_year = year - self.start_year
        if adjusted_year >= self.term_years:
            return 0
        monthly_rate = self.interest_rate / 12
        num_payments = self.term_years * 12
        payment = self.calculate_payment()
        remaining_payments = (self.term_years - adjusted_year) * 12
        return (payment * ((1 - (1 + monthly_rate)**(-remaining_payments)) / monthly_rate))

    def get_payment(self, year: int) -> float:
        if year < self.start_year:
            return 0
        adjusted_year = year - self.start_year
        if adjusted_year >= self.term_years:
            return 0
        return self.calculate_payment() * 12

class MortgageLoan(Loan):
    def __init__(self, principal: float, interest_rate: float, term_years: int = 15, loan_id: str = None):
        super().__init__("Mortgage", principal, interest_rate, term_years, loan_id)

class CarLoan(Loan):
    def __init__(self, principal: float, interest_rate: float, term_years: int = 5, loan_id: str = None):
        super().__init__("Car Loan", principal, interest_rate, term_years, loan_id)

class StudentLoan(Loan):
    def __init__(self, name: str, principal: float, interest_rate: float, 
                 term_years: int = 10, deferment_years: int = 0, 
                 loan_id: str = None, institution: str = None):
        super().__init__(name, principal, interest_rate, term_years, loan_id)
        self.deferment_years = deferment_years
        self.institution = institution

    def get_balance(self, year: int) -> float:
        if year < self.start_year:
            return 0
        adjusted_year = year - self.start_year
        if adjusted_year < self.deferment_years:
            return self.principal * (1 + self.interest_rate) ** adjusted_year
        payment_year = adjusted_year - self.deferment_years
        if payment_year >= self.term_years:
            return 0
        monthly_rate = self.interest_rate / 12
        num_payments = self.term_years * 12
        payment = self.calculate_payment()
        remaining_payments = (self.term_years - payment_year) * 12
        return (payment * ((1 - (1 + monthly_rate)**(-remaining_payments)) / monthly_rate))

    def get_payment(self, year: int) -> float:
        if year < self.start_year:
            return 0
        adjusted_year = year - self.start_year
        if adjusted_year < self.deferment_years or adjusted_year >= (self.deferment_years + self.term_years):
            return 0
        return self.calculate_payment() * 12

class Income(ABC):
    def __init__(self, name: str, annual_amount: float, growth_rate: float = 0.03, start_year: int = 0):
        self.name = name
        self.annual_amount = annual_amount
        self.growth_rate = growth_rate
        self.start_year = start_year
        self.end_year = None

    def calculate_income(self, year: int) -> float:
        try:
            year_int = int(year)
            if year_int < self.start_year or (self.end_year is not None and year_int >= self.end_year):
                return 0
            adjusted_year = year_int - self.start_year
            return self.annual_amount * (1 + self.growth_rate) ** adjusted_year
        except (TypeError, ValueError):
            return 0  # Return 0 if year cannot be converted to int

class Salary(Income):
    def __init__(self, annual_amount: float, location_adjustment: float = 1.0):
        super().__init__("Primary Income", annual_amount)
        self.location_adjustment = location_adjustment

    def calculate_income(self, year: int) -> float:
        return super().calculate_income(year) * self.location_adjustment

class SpouseIncome(Income):
    """Income class for handling spouse's income with location and lifestyle adjustments"""
    def __init__(self, annual_amount: float, growth_rate: float = 0.03,
                 location_adjustment: float = 1.0, start_year: int = 0,
                 lifestyle_adjustment: float = 0.0):
        super().__init__("Spouse Income", annual_amount, growth_rate=growth_rate, start_year=start_year)
        self.location_adjustment = location_adjustment
        self.lifestyle_adjustment = lifestyle_adjustment

    def calculate_income(self, year: int) -> float:
        try:
            year_int = int(year)
            base_income = super().calculate_income(year_int)
            if base_income == 0:
                return 0
            return base_income * self.location_adjustment * (1 + self.lifestyle_adjustment)
        except (TypeError, ValueError):
            return 0

class Expense(ABC):
    def __init__(self, name: str, annual_amount: float, inflation_rate: float = 0.02):
        self.name = name
        self.annual_amount = annual_amount
        self.inflation_rate = inflation_rate
        self._milestone = None  # Reference to the milestone this expense belongs to

    def calculate_expense(self, year: int) -> float:
        return self.annual_amount * (1 + self.inflation_rate) ** year

class FixedExpense(Expense):
    pass

class OneTimeExpense(Expense):
    """Expense that only occurs in a specific year"""
    def __init__(self, name: str, amount: float, specific_year: int):
        super().__init__(name, amount, inflation_rate=0)
        self.specific_year = specific_year
    
    def calculate_expense(self, year: int) -> float:
        # Only return the amount if it's the specific year
        if year == self.specific_year:
            return self.annual_amount
        return 0.0
    
    def round(self) -> float:
        """Round the annual amount to the nearest integer"""
        return round(self.annual_amount)
    
    def __round__(self, n=None):
        """Python built-in round protocol"""
        if n is None:
            return round(self.annual_amount)
        return round(self.annual_amount, n)

class VariableExpense(Expense):
    def __init__(self, name: str, annual_amount: float, volatility: float = 0.1):
        super().__init__(name, annual_amount)
        self.volatility = volatility

    def calculate_expense(self, year: int) -> float:
        base_expense = super().calculate_expense(year)
        # Only apply volatility if the expense is non-zero (i.e., within valid years)
        if base_expense > 0:
            return base_expense * (1 + self.volatility)
        return 0.0

class LoanPayment(FixedExpense):
    """Base class for loan payments that ensures proper termination"""
    def __init__(self, name: str, annual_amount: float, loan_term_years: int, start_year: int):
        super().__init__(name, annual_amount, inflation_rate=0)
        self.loan_term_years = loan_term_years
        self.start_year = start_year

    def calculate_expense(self, year: int) -> float:
        # Get the associated loan from the milestone
        if not self._milestone:
            return 0
            
        # Find the loan associated with this payment
        loan = next((loan for loan in self._milestone.liabilities 
                    if isinstance(loan, Loan) and loan.name == self.name.replace(" Payment", "")), None)
        
        if not loan:
            return 0
            
        # Use the loan's built-in payment calculation
        return loan.get_payment(year)

class CarLoanPayment(LoanPayment):
    """Fixed expense for car loan payments that stops after the loan term"""
    def __init__(self, annual_amount: float, loan_term_years: int, start_year: int):
        super().__init__("Car Loan", annual_amount, loan_term_years, start_year)

class StudentLoanPayment(LoanPayment):
    """Fixed expense for student loan payments that handles deferment"""
    def __init__(self, name: str, annual_amount: float, loan_term_years: int, start_year: int, deferment_years: int):
        super().__init__(name, annual_amount, loan_term_years, start_year)
        self.deferment_years = deferment_years

    def calculate_expense(self, year: int) -> float:
        # Get the associated loan from the milestone
        if not self._milestone:
            return 0
            
        # Find the loan associated with this payment
        loan = next((loan for loan in self._milestone.liabilities 
                    if isinstance(loan, StudentLoan) and loan.name == self.name.replace(" Payment", "")), None)
        
        if not loan:
            return 0
            
        # Use the loan's built-in payment calculation
        return loan.get_payment(year)

class MortgagePayment(LoanPayment):
    """Fixed expense for mortgage payments"""
    def __init__(self, annual_amount: float, loan_term_years: int, start_year: int):
        super().__init__("Mortgage", annual_amount, loan_term_years, start_year)

class Milestone:
    def __init__(self, name: str, trigger_year: int, category: str):
        self.name = name
        self.trigger_year = trigger_year
        self.category = category
        self.one_time_expenses = []
        self.recurring_expenses = []
        self.income_adjustments = []
        self.assets = []
        self.liabilities = []
        self.duration_years = None  # For time-limited milestones

    def add_one_time_expense(self, amount: float):
        self.one_time_expenses.append(amount)

    def add_recurring_expense(self, expense: Expense):
        expense._milestone = self  # Set the reference to this milestone
        self.recurring_expenses.append(expense)

    def add_income_adjustment(self, income: Income):
        if isinstance(income, Income):
            self.income_adjustments.append(income)
        else:
            raise ValueError("Income adjustment must be an instance of Income class")

    def add_asset(self, asset: Asset):
        self.assets.append(asset)

    def add_liability(self, liability: Liability):
        """Add a liability to the milestone"""
        liability._milestone = self
        self.liabilities.append(liability)

    def add_loan(self, loan: Loan):
        """Add a loan with unique tracking"""
        loan._milestone = self
        self.liabilities.append(loan)

    def get_loans_by_type(self, loan_type: type) -> List[Loan]:
        """Get all loans of a specific type"""
        return [loan for loan in self.liabilities if isinstance(loan, loan_type)]

    def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        """Get a specific loan by its ID"""
        return next((loan for loan in self.liabilities 
                    if isinstance(loan, Loan) and loan.loan_id == loan_id), None)

    def remove_loan(self, loan_id: str) -> bool:
        """Remove a loan by its ID"""
        loan = self.get_loan_by_id(loan_id)
        if loan:
            self.liabilities.remove(loan)
            return True
        return False

    def get_total_loan_balance(self, year: int) -> float:
        """Get the total balance of all loans at a given year"""
        return sum(loan.get_balance(year) for loan in self.liabilities if isinstance(loan, Loan))

    def get_total_loan_payment(self) -> float:
        """Get the total payment for all loans"""
        return sum(loan.calculate_payment() for loan in self.liabilities if isinstance(loan, Loan))

    def calculate_expenses(self, year: int) -> float:
        """Calculate expenses considering duration limits if applicable"""
        if self.duration_years is not None:
            # If milestone has a duration, only apply expenses during that period
            if year < self.trigger_year or year >= (self.trigger_year + self.duration_years):
                return 0.0

        total = 0.0
        # Add one-time expenses
        for expense in self.one_time_expenses:
            if year == self.trigger_year:
                total += expense

        # Add recurring expenses
        for expense in self.recurring_expenses:
            if isinstance(expense, LoanPayment):
                # For loan payments, use their built-in term handling
                total += expense.calculate_expense(year)
            elif self.duration_years is not None:
                # For time-limited milestones, calculate based on years from start
                years_from_start = year - self.trigger_year
                if years_from_start >= 0 and years_from_start < self.duration_years:
                    total += expense.calculate_expense(year)
            else:
                # For permanent milestones, calculate normally
                total += expense.calculate_expense(year)

        return total

    def calculate_income_adjustments(self, year: int) -> float:
        total_adjustment = 0
        for income in self.income_adjustments:
            if isinstance(income, Income):
                total_adjustment += income.calculate_income(year)
        return total_adjustment

@dataclass
class GraduateSchoolMilestone(Milestone):
    def __init__(self, trigger_year: int, program_years: int):
        super().__init__("Graduate School", trigger_year, "Education")
        self.duration_years = program_years  # Set the duration for grad school

class MilestoneFactory:
    @staticmethod
    def create_home_purchase(trigger_year: int, home_price: float, down_payment_percentage: float = 0.20,
                           mortgage_rate: float = 0.045, mortgage_term_years: int = 15,
                           property_tax_rate: float = 0.02, insurance_rate: float = 0.01,
                           maintenance_rate: float = 0.01, appreciation_rate: float = 0.03,
                           monthly_utilities: float = 0, monthly_hoa: float = 0,
                           annual_renovation: float = 0, home_office_deduction: bool = False,
                           office_percentage: float = 0) -> Milestone:
        milestone = Milestone("Home Purchase", trigger_year, "Asset")

        down_payment = home_price * down_payment_percentage
        loan_amount = home_price * (1 - down_payment_percentage)

        milestone.add_one_time_expense(down_payment)
        milestone.add_asset(Home("Primary Residence", home_price, appreciation_rate,
                               down_payment_percentage=down_payment_percentage,
                               monthly_utilities=monthly_utilities,
                               monthly_hoa=monthly_hoa,
                               annual_renovation=annual_renovation,
                               home_office_deduction=home_office_deduction,
                               office_percentage=office_percentage))

        mortgage = MortgageLoan(loan_amount, mortgage_rate, mortgage_term_years)
        mortgage.start_year = trigger_year
        milestone.add_liability(mortgage)

        monthly_payment = mortgage.calculate_payment()
        milestone.add_recurring_expense(
            MortgagePayment(monthly_payment * 12, mortgage_term_years, trigger_year)
        )

        # Add recurring expenses that continue indefinitely as long as the home is owned
        milestone.add_recurring_expense(
            FixedExpense("Property Tax", home_price * property_tax_rate, inflation_rate=0)
        )
        milestone.add_recurring_expense(
            FixedExpense("Home Insurance", home_price * insurance_rate, inflation_rate=0)
        )
        milestone.add_recurring_expense(
            FixedExpense("Home Maintenance", home_price * maintenance_rate, inflation_rate=0)
        )

        # Add other recurring expenses that continue indefinitely
        if monthly_utilities > 0:
            milestone.add_recurring_expense(VariableExpense("Utilities", monthly_utilities * 12))
        if monthly_hoa > 0:
            milestone.add_recurring_expense(FixedExpense("HOA Fees", monthly_hoa * 12, inflation_rate=0))
        if annual_renovation > 0:
            milestone.add_recurring_expense(VariableExpense("Renovation", annual_renovation))

        # Add home office deduction if applicable
        if home_office_deduction and office_percentage > 0:
            deduction = home_price * (office_percentage / 100) * 0.05  # Simplified deduction calculation
            milestone.add_recurring_expense(FixedExpense("Home Office Deduction", -deduction))

        return milestone

    @staticmethod
    def create_marriage(trigger_year: int, wedding_cost: float = 30000,
                       spouse_income: float = 0, spouse_income_increase: float = 0.03,
                       lifestyle_adjustment: float = 0.0, initial_savings: float = 0,
                       initial_debt: float = 0, insurance_cost: float = 0,
                       spouse_debt_rate: float = 0.06, spouse_debt_term: int = 5) -> Milestone:
        milestone = Milestone("Marriage", trigger_year, "Life Event")

        # Add wedding cost if specified
        if wedding_cost > 0:
            milestone.add_one_time_expense(wedding_cost)  # Just pass the float amount

        # Add spouse income if specified
        if spouse_income > 0:
            spouse = SpouseIncome(
                annual_amount=spouse_income,
                growth_rate=spouse_income_increase,
                start_year=trigger_year,
                lifestyle_adjustment=lifestyle_adjustment
            )
            milestone.add_income_adjustment(spouse)

        # Add lifestyle adjustment as a recurring expense
        if lifestyle_adjustment != 0:
            # Calculate base expenses before marriage (30% of spouse income as a rough estimate)
            base_expenses = spouse_income * 0.3
            # Calculate lifestyle adjustment amount
            adjustment_amount = base_expenses * lifestyle_adjustment
            milestone.add_recurring_expense(
                VariableExpense("Joint Lifestyle Adjustment", adjustment_amount)
            )

        # Add insurance costs
        if insurance_cost > 0:
            milestone.add_recurring_expense(
                FixedExpense("Joint Insurance", insurance_cost)
            )

        # Add spouse's initial savings as an investment asset
        if initial_savings > 0:
            savings = Investment(
                name="Spouse Savings",
                initial_value=initial_savings,
                return_rate=0.07  # Standard market return rate
            )
            milestone.add_asset(savings)

        # Add spouse's initial debt as a loan
        if initial_debt > 0:
            spouse_loan = StudentLoan(
                name="Spouse Debt",
                principal=initial_debt,
                interest_rate=spouse_debt_rate,
                term_years=spouse_debt_term
            )
            spouse_loan.start_year = trigger_year
            milestone.add_liability(spouse_loan)

            # Add the corresponding loan payment
            payment = LoanPayment(
                name="Spouse Debt Payment",
                annual_amount=spouse_loan.calculate_payment() * 12,
                loan_term_years=spouse_debt_term,
                start_year=trigger_year
            )
            milestone.add_recurring_expense(payment)

        return milestone

    @staticmethod
    def create_grad_school(trigger_year: int, yearly_costs: List[float], years: int,
                      yearly_loans: List[float] = None,
                      part_time_income: float = 0, scholarship_amount: float = 0,
                      salary_increase_percentage: float = 0.3,
                      networking_cost: float = 0) -> Milestone:
        milestone = GraduateSchoolMilestone(trigger_year, years)

        for year_index, year_cost in enumerate(yearly_costs):
            net_cost = year_cost - scholarship_amount
            if net_cost > 0:
                loan_amount = yearly_loans[year_index] if yearly_loans else 0
                out_of_pocket = net_cost - loan_amount

                if out_of_pocket > 0:
                    expense = OneTimeExpense(
                        f"Graduate School Year {year_index + 1} Out-of-pocket",
                        out_of_pocket,
                        trigger_year + year_index
                    )
                    expense._milestone = milestone
                    milestone.add_recurring_expense(expense)

                if loan_amount > 0:
                    deferment_years = (years - year_index)
                    year_loan = StudentLoan(
                        name=f"Graduate School Year {year_index + 1} Loan",
                        principal=loan_amount,
                        interest_rate=0.06,
                        term_years=10,
                        deferment_years=deferment_years
                    )
                    year_loan.start_year = trigger_year + year_index
                    year_loan._milestone = milestone
                    milestone.add_liability(year_loan)

                    # Add loan payment as a recurring expense starting after deferment
                    payment = StudentLoanPayment(
                        f"Graduate School Year {year_index + 1} Loan Payment",
                        year_loan.calculate_payment() * 12,
                        10,  # term_years
                        trigger_year + deferment_years,  # start_year
                        deferment_years  # deferment_years
                    )
                    payment._milestone = milestone
                    milestone.add_recurring_expense(payment)

        if networking_cost > 0:
            milestone.add_recurring_expense(VariableExpense("Professional Development", networking_cost))

        if part_time_income > 0:
            part_time = Income("Part-Time Work", part_time_income, start_year=trigger_year)
            part_time.end_year = trigger_year + years
            milestone.add_income_adjustment(part_time)

        if salary_increase_percentage > 0:
            base_salary = 30000
            increase_amount = base_salary * salary_increase_percentage
            increased_salary = Income("Salary Increase", increase_amount, start_year=trigger_year + years)
            milestone.add_income_adjustment(increased_salary)

        return milestone

    @staticmethod
    def create_child(trigger_year: int, education_savings: float = 0,
                    healthcare_cost: float = 0, insurance_cost: float = 0,
                    tax_benefit: float = 0) -> Milestone:
        milestone = Milestone("New Child", trigger_year, "Family")
        milestone.add_one_time_expense(10000)  # Initial costs

        # Add education savings as investment
        if education_savings > 0:
            education_investment = Investment("Education Fund", 0, 0.06)  # 6% return rate
            education_investment.add_contribution(education_savings)
            milestone.add_asset(education_investment)
            milestone.add_recurring_expense(FixedExpense("Education Savings", education_savings))

        # Add healthcare and insurance costs
        if healthcare_cost > 0:
            milestone.add_recurring_expense(VariableExpense("Child Healthcare", healthcare_cost))
        if insurance_cost > 0:
            milestone.add_recurring_expense(FixedExpense("Child Insurance", insurance_cost))

        # Add general child expenses
        milestone.add_recurring_expense(VariableExpense("Child Expenses", 10000))

        # Add tax benefits as negative expense (savings)
        if tax_benefit > 0:
            milestone.add_recurring_expense(FixedExpense("Child Tax Benefit", -tax_benefit))

        return milestone

    @staticmethod
    def create_education(trigger_year: int, total_cost: float, program_years: int,
                        institution_name: str = "", location: str = "",
                        is_undergraduate: bool = True, pre_projection: bool = False) -> Milestone:
        """Create an education milestone for college or graduate school"""
        name = f"Education: {institution_name}" if institution_name else "Education"
        milestone = Milestone(name, trigger_year, "Education")

        # Calculate annual cost
        annual_cost = total_cost / program_years

        # Add the total cost as a student loan
        loan_name = f"{institution_name} Student Loan" if institution_name else "Student Loan"
        milestone.add_liability(StudentLoan(
            name=loan_name,
            principal=total_cost,
            interest_rate=0.05  # 5% interest rate for student loans
        ))

        # Add annual expenses for the duration of the program
        milestone.add_recurring_expense(FixedExpense(f"{institution_name} Tuition", annual_cost))

        # Add living expenses if it's undergraduate education
        if is_undergraduate:
            living_expenses = annual_cost * 0.4  # Estimate living expenses as 40% of tuition
            milestone.add_recurring_expense(VariableExpense("College Living Expenses", living_expenses))

        return milestone

    @staticmethod
    def create_car_purchase(trigger_year: int, car_price: float, down_payment_percentage: float = 0.20,
                          loan_interest_rate: float = 0.045, loan_term_years: int = 5,
                          insurance_rate: float = 0.04, maintenance_rate: float = 0.033,
                          depreciation_rate: float = 0.15, vehicle_type: str = "Gas",
                          monthly_fuel: float = 0, monthly_parking: float = 0,
                          tax_incentive: float = 0) -> Milestone:
        milestone = Milestone("Car Purchase", trigger_year, "Asset")
        milestone.duration_years = loan_term_years

        if vehicle_type in ["Electric", "Hybrid"] and tax_incentive > 0:
            car_price = car_price - tax_incentive

        down_payment = car_price * down_payment_percentage
        loan_amount = car_price * (1 - down_payment_percentage)

        milestone.add_one_time_expense(down_payment)

        if vehicle_type == "Electric":
            depreciation_rate *= 1.2
        elif vehicle_type == "Hybrid":
            depreciation_rate *= 1.1

        milestone.add_asset(Vehicle("Car", car_price, depreciation_rate))

        car_loan = CarLoan(loan_amount, loan_interest_rate, loan_term_years)
        car_loan.start_year = trigger_year
        milestone.add_liability(car_loan)

        monthly_payment = car_loan.calculate_payment()
        annual_payment = monthly_payment * 12
        
        car_payment = CarLoanPayment(annual_payment, loan_term_years, trigger_year)
        milestone.add_recurring_expense(car_payment)
        
        # Add other recurring expenses that should also stop after loan term
        milestone.add_recurring_expense(FixedExpense("Car Insurance", car_price * insurance_rate, inflation_rate=0))
        milestone.add_recurring_expense(FixedExpense("Car Maintenance", car_price * maintenance_rate, inflation_rate=0))

        if monthly_fuel > 0:
            milestone.add_recurring_expense(VariableExpense(f"{vehicle_type} Fuel/Charging", monthly_fuel * 12))
        if monthly_parking > 0:
            milestone.add_recurring_expense(FixedExpense("Parking", monthly_parking * 12, inflation_rate=0))

        return milestone

class Tax(ABC):
    def __init__(self, name: str, tax_year: int = 2024):
        self.name = name
        self.tax_year = tax_year

    @abstractmethod
    def calculate_tax(self, year: int, income: float) -> float:
        pass

class FederalIncomeTax(Tax):
    def __init__(self, filing_status: str = "single"):
        super().__init__("Federal Income Tax")
        self.filing_status = filing_status

    def calculate_tax(self, year: int, income: float) -> float:
        # 2024 tax brackets
        if self.filing_status == "single":
            brackets = [
                (0, 11600, 0.10),
                (11601, 47150, 0.12),
                (47151, 100525, 0.22),
                (100526, 191950, 0.24),
                (191951, 243725, 0.32),
                (243726, 609350, 0.35),
                (609351, float('inf'), 0.37)
            ]
        else:  # married
            brackets = [
                (0, 23200, 0.10),
                (23201, 94300, 0.12),
                (94301, 201050, 0.22),
                (201051, 383900, 0.24),
                (383901, 487450, 0.32),
                (487451, 731200, 0.35),
                (731201, float('inf'), 0.37)
            ]

        tax = 0
        for i, (lower, upper, rate) in enumerate(brackets):
            if income > lower:
                taxable_amount = min(income - lower, upper - lower)
                tax += taxable_amount * rate
            else:
                break
        return tax

class PayrollTax(Tax):
    def __init__(self):
        super().__init__("Payroll Tax")
        self.social_security_cap = 168600  # 2024 cap

    def calculate_tax(self, year: int, income: float) -> float:
        ss_tax = min(income, self.social_security_cap) * 0.062  # 6.2% Social Security
        medicare_tax = income * 0.0145  # 1.45% Medicare
        if income > 200000:  # Additional Medicare Tax
            medicare_tax += (income - 200000) * 0.009
        return ss_tax + medicare_tax

class StateIncomeTax(Tax):
    def __init__(self, state: str = "CA", filing_status: str = "single"):
        super().__init__("State Income Tax")
        self.state = state
        self.filing_status = filing_status

    def calculate_tax(self, year: int, income: float) -> float:
        # Example using CA tax brackets
        if self.state == "CA":
            brackets = [
                (0, 10099, 0.01),
                (10100, 23942, 0.02),
                (23943, 37788, 0.04),
                (37789, 52455, 0.06),
                (52456, 66295, 0.08),
                (66296, 338639, 0.093),
                (338640, 406364, 0.103),
                (406365, 677275, 0.113),
                (677276, float('inf'), 0.123)
            ]

            tax = 0
            for lower, upper, rate in brackets:
                if income > lower:
                    taxable_amount = min(income - lower, upper - lower)
                    tax += taxable_amount * rate
                else:
                    break
            return tax
        return 0  # Default for other states

__all__ = [
    'Income', 'SpouseIncome', 'Expense', 'FixedExpense', 'VariableExpense', 'OneTimeExpense',
    'Asset', 'Investment', 'Home', 'Liability', 'Loan', 'MortgageLoan', 'CarLoan', 'StudentLoan',
    'Milestone', 'MilestoneFactory', 'Tax', 'FederalIncomeTax', 'StateIncomeTax', 'PayrollTax'
]