import pandas as pd
from typing import Dict, List, Tuple, Optional
from models.financial_models import (
    Asset, Liability, Income, Expense,
    Salary, Investment, FixedExpense, VariableExpense,
    Milestone
)

class DataProcessor:
    @staticmethod
    def load_coli_data(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            required_columns = ['Cost of Living', 'Housing', 'Transportation', 'Food', 'Healthcare', 
                                  'Personal Insurance', 'Apparel', 'Services', 'Entertainment', 'Other',
                                  'Monthly Expense', 'Income Adjustment Factor', 'Average Price of Starter Home']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("COLI CSV file missing required columns")
            return df
        except Exception as e:
            raise Exception(f"Error loading COLI data: {str(e)}")

    @staticmethod
    def load_occupation_data(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            required_columns = ['Occupation', 'Monthly Income']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Occupation CSV file missing required columns")
            return df
        except Exception as e:
            raise Exception(f"Error loading occupation data: {str(e)}")

    @staticmethod
    def process_location_data(coli_df: pd.DataFrame, occupation_df: pd.DataFrame,
                        location: str, occupation: str, investment_return_rate: float) -> Dict:
        """
        Process location and occupation data, with proper error handling
        """
        try:
            # Validate inputs
            if not location or not occupation:
                raise ValueError("Location and occupation must be provided")

            # Find matching location data
            location_matches = coli_df[coli_df['Cost of Living'].astype(str) == str(location)]
            if location_matches.empty:
                raise ValueError(f"Location '{location}' not found in the database")
            location_data = location_matches.iloc[0]

            # Find matching occupation data
            occupation_matches = occupation_df[occupation_df['Occupation'].astype(str) == str(occupation)]
            if occupation_matches.empty:
                raise ValueError(f"Occupation '{occupation}' not found in the database")
            occupation_data = occupation_matches.iloc[0]

            # Process the data
            return {
                'housing': float(location_data['Housing']),
                'transportation': float(location_data['Transportation']),
                'food': float(location_data['Food']),
                'healthcare': float(location_data['Healthcare']),
                'insurance': float(location_data['Personal Insurance']),
                'apparel': float(location_data['Apparel']),
                'services': float(location_data['Services']),
                'entertainment': float(location_data['Entertainment']),
                'other': float(location_data['Other']),
                'monthly_expense': float(location_data['Monthly Expense']),
                'home_price': float(location_data['Average Price of Starter Home']),
                'location_adjustment': float(location_data['Income Adjustment Factor']),
                'base_income': float(occupation_data['Monthly Income']) * 12,  # Convert to annual
                'investment_return_rate': investment_return_rate
            }
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error processing location data: {str(e)}")

    @staticmethod
    def create_financial_objects(location_data: Dict, 
                               milestones: Optional[List[Milestone]] = None) -> Tuple[List[Asset], List[Liability], List[Income], List[Expense]]:
        # Define OneTimeExpense at the method level
        class OneTimeExpense(FixedExpense):
            def __init__(self, name: str, amount: float, trigger_year: int):
                super().__init__(name, amount, inflation_rate=0)
                self.trigger_year = trigger_year

            def calculate_expense(self, year: int) -> float:
                return self.annual_amount if year == self.trigger_year else 0

        assets = []
        liabilities = []
        income = []
        expenses = []

        # Find home purchase milestone year if it exists
        home_purchase_year = None
        if milestones:
            for milestone in milestones:
                if milestone.name == "Home Purchase":
                    home_purchase_year = milestone.trigger_year
                    break

        # Find car purchase milestone years if they exist
        car_purchase_years = []
        if milestones:
            for milestone in milestones:
                if milestone.name == "Car Purchase":
                    car_purchase_years.append(milestone.trigger_year)

        # Create Income objects
        base_salary = Salary(location_data['base_income'], location_data['location_adjustment'])
        income.append(base_salary)

        # Create Investment asset for savings (starts at 0)
        investment = Investment("Savings", 0, location_data['investment_return_rate'])
        assets.append(investment)

        # Add basic living expenses
        # Transportation expense adjusted for car ownership
        class AdjustedTransportationExpense(FixedExpense):
            def __init__(self, name: str, annual_amount: float, car_purchase_years: List[int]):
                super().__init__(name, annual_amount)
                self.car_purchase_years = car_purchase_years

            def calculate_expense(self, year: int) -> float:
                # Check if there's an active car in this year
                # A car remains active from its purchase year onwards until a new car is purchased
                has_car = False
                if self.car_purchase_years:
                    # Sort purchase years to find the most recent purchase before current year
                    relevant_purchases = [y for y in sorted(self.car_purchase_years) if y <= year]
                    has_car = bool(relevant_purchases)  # True if any purchase year is before or equal to current year

                base_expense = super().calculate_expense(year)
                return base_expense * 0.2 if has_car else base_expense

        expenses.append(AdjustedTransportationExpense("Transportation", location_data['transportation'] * 12, car_purchase_years))
        expenses.append(VariableExpense("Food", location_data['food'] * 12))
        expenses.append(FixedExpense("Healthcare", location_data['healthcare'] * 12))
        expenses.append(FixedExpense("Insurance", location_data['insurance'] * 12))
        expenses.append(VariableExpense("Apparel", location_data['apparel'] * 12))
        expenses.append(VariableExpense("Services", location_data['services'] * 12))
        expenses.append(VariableExpense("Entertainment", location_data['entertainment'] * 12))
        expenses.append(VariableExpense("Other", location_data['other'] * 12))

        # Add rent expense that only applies before home purchase (if applicable)
        if home_purchase_year is not None:
            class PreHomeRentExpense(FixedExpense):
                def __init__(self, name: str, annual_amount: float, trigger_year: int):
                    super().__init__(name, annual_amount)
                    self.trigger_year = trigger_year

                def calculate_expense(self, year: int) -> float:
                    return super().calculate_expense(year) if year < self.trigger_year else 0

            expenses.append(PreHomeRentExpense("Rent", location_data['housing'] * 12, home_purchase_year))
        else:
            # If no home purchase milestone, add regular rent expense
            expenses.append(FixedExpense("Rent", location_data['housing'] * 12))

        # Add milestone-related financial objects
        if milestones:
            for milestone in milestones:
                # First, determine if this is a graduate school milestone and its duration
                is_grad_school = milestone.name == "Graduate School"
                program_duration = 0
                if is_grad_school:
                    # Find the highest year number in the recurring expenses to determine program length
                    for expense in milestone.recurring_expenses:
                        if "Graduate School" in str(expense.name):
                            for i in range(1, 5):  # Support up to 4 year programs
                                if f"Year {i}" in str(expense.name):
                                    program_duration = max(program_duration, i)

                # Handle one-time expenses
                if milestone.one_time_expense > 0:
                    one_time_exp = OneTimeExpense(
                        f"{milestone.name} Down Payment",
                        milestone.one_time_expense,
                        milestone.trigger_year
                    )
                    expenses.append(one_time_exp)

                # Add recurring expenses starting from milestone year
                for expense in milestone.recurring_expenses:
                    # Special handling for graduate school expenses
                    if "Graduate School" in str(expense.name):
                        # Extract the program year from the expense name (e.g., "Year 1", "Year 2", etc.)
                        program_year = 0
                        for i in range(1, 5):  # Support up to 4 year programs
                            if f"Year {i}" in str(expense.name):
                                program_year = i
                                break
                        
                        if program_year == 0:
                            # If no year specified, treat as first year
                            program_year = 1

                        # Actual year this expense occurs
                        expense_year = milestone.trigger_year + program_year - 1

                        if "Loan Payment" in str(expense.name):
                            # Loan payments should be recurring, starting after graduation
                            class PostGraduationLoanPayment(expense.__class__):
                                def __init__(self, base_expense, program_start_year, program_duration):
                                    # Copy all attributes from the base expense
                                    for attr, value in base_expense.__dict__.items():
                                        setattr(self, attr, value)
                                    self.program_start_year = program_start_year
                                    self.program_duration = program_duration
                                    # All loan payments start after graduation
                                    self.payment_start_year = program_start_year + program_duration

                                def calculate_expense(self, year: int) -> float:
                                    if year < self.payment_start_year:
                                        return 0
                                    # For years after payment starts, calculate with inflation from the start year
                                    years_since_start = year - self.payment_start_year
                                    return self.annual_amount * (1 + self.inflation_rate) ** years_since_start

                            expenses.append(PostGraduationLoanPayment(expense, milestone.trigger_year, program_duration))
                        else:
                            # Out of pocket/tuition costs should be one-time in the specific program year
                            one_time_exp = OneTimeExpense(
                                expense.name,
                                expense.annual_amount,
                                expense_year  # Use the calculated expense year
                            )
                            expenses.append(one_time_exp)
                        continue

                    # Special handling for OneTimeExpense
                    if isinstance(expense, OneTimeExpense):
                        # For one-time expenses, adjust the specific_year based on milestone trigger
                        one_time_exp = OneTimeExpense(
                            expense.name,
                            expense.annual_amount,
                            milestone.trigger_year + (expense.specific_year if hasattr(expense, 'specific_year') else 0)
                        )
                        expenses.append(one_time_exp)
                        continue

                    # For regular recurring expenses
                    class PostMilestoneExpense(expense.__class__):
                        def __init__(self, base_expense, trigger_year):
                            # Copy all attributes from the base expense
                            for attr, value in base_expense.__dict__.items():
                                setattr(self, attr, value)
                            self.trigger_year = trigger_year

                        def calculate_expense(self, year: int) -> float:
                            if year < self.trigger_year:
                                return 0
                            # For years after trigger, calculate with inflation from the start year
                            years_since_start = year - self.trigger_year
                            return self.annual_amount * (1 + self.inflation_rate) ** years_since_start

                    expenses.append(PostMilestoneExpense(expense, milestone.trigger_year))

                # Add assets and liabilities with timing
                for asset in milestone.assets:
                    class TimedAsset(asset.__class__):
                        def __init__(self, base_asset, start_year):
                            self.name = base_asset.name
                            self.initial_value = base_asset.initial_value
                            self.start_year = start_year
                            for attr, value in base_asset.__dict__.items():
                                if attr not in ['name', 'initial_value']:
                                    setattr(self, attr, value)

                        def calculate_value(self, year: int) -> float:
                            if year >= self.start_year:
                                return super().calculate_value(year - self.start_year)
                            return 0

                    assets.append(TimedAsset(asset, milestone.trigger_year))

                # Add liabilities with proper timing for graduate school
                for liability in milestone.liabilities:
                    if is_grad_school and "Graduate School" in str(liability.name):
                        # Extract the program year from the liability name
                        program_year = 0
                        for i in range(1, 5):
                            if f"Year {i}" in str(liability.name):
                                program_year = i
                                break
                        
                        if program_year == 0:
                            program_year = 1
                            
                        # Set the start year to when this specific year's loan is taken
                        liability.start_year = milestone.trigger_year + program_year - 1
                    else:
                        # For non-graduate school liabilities, use the milestone trigger year
                        liability.start_year = milestone.trigger_year
                        # Ensure loan tracking is set up properly
                        if hasattr(liability, 'loan_id') and not liability.loan_id:
                            liability.loan_id = f"{liability.name}_{id(liability)}"
                    # Add the liability to the main list
                    liabilities.append(liability)

                # Add income adjustments
                income.extend(milestone.income_adjustments)

        return assets, liabilities, income, expenses