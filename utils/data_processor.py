import pandas as pd
from typing import Dict, List, Tuple, Optional
from models.financial_models import *
from utils.tax_calculator import TaxCalculator

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
        Process location and occupation data, with proper error handling and tax considerations
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

            # Initialize tax calculator
            tax_calculator = TaxCalculator()
            state = tax_calculator.get_state_from_city(location)

            # Calculate base annual income
            base_income = float(occupation_data['Monthly Income']) * 12

            # Get initial tax calculation for single status
            tax_result = tax_calculator.calculate_total_tax(
                income=base_income,
                state=state,
                filing_status='single'
            )

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
                'base_income': base_income,
                'investment_return_rate': investment_return_rate,
                'state': state,
                'initial_tax_burden': {
                    'federal': tax_result['federal_tax'],
                    'state': tax_result['state_tax'],
                    'fica': tax_result['fica_tax'],
                    'total': tax_result['total_tax'],
                    'effective_rate': tax_result['effective_tax_rate']
                }
            }
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error processing location data: {str(e)}")

    @staticmethod
    def create_financial_objects(location_data: Dict, 
                               milestones: Optional[List[Milestone]] = None) -> Tuple[List[Asset], List[Liability], List[Income], List[Expense]]:
        """
        Create financial objects with tax considerations
        """
        assets = []
        liabilities = []
        income = []
        expenses = []

        # Find home purchase milestone year if it exists
        home_purchase_year = None
        marriage_year = None
        if milestones:
            for milestone in milestones:
                if milestone.name == "Home Purchase":
                    home_purchase_year = milestone.trigger_year
                elif milestone.name == "Marriage":
                    marriage_year = milestone.trigger_year

        # Create Income objects with tax considerations
        base_salary = Salary(location_data['base_income'], location_data['location_adjustment'])
        base_salary.set_location(location_data.get('state'))
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
                # Handle one-time expenses
                if milestone.one_time_expense > 0:
                    class OneTimeExpense(FixedExpense):
                        def __init__(self, name: str, amount: float, trigger_year: int):
                            super().__init__(name, amount, inflation_rate=0)
                            self.trigger_year = trigger_year

                        def calculate_expense(self, year: int) -> float:
                            return self.annual_amount if year == self.trigger_year else 0

                    one_time_exp = OneTimeExpense(
                        f"{milestone.name} Down Payment",
                        milestone.one_time_expense,
                        milestone.trigger_year
                    )
                    expenses.append(one_time_exp)

                # Add recurring expenses starting from milestone year
                for expense in milestone.recurring_expenses:
                    class PostMilestoneExpense(expense.__class__):
                        def __init__(self, base_expense, trigger_year):
                            super().__init__(base_expense.name, base_expense.annual_amount)
                            self.trigger_year = trigger_year
                            self.inflation_rate = base_expense.inflation_rate  # Preserve inflation rate

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

                for liability in milestone.liabilities:
                    class TimedLiability:
                        def __init__(self, base_liability, start_year):
                            self.name = base_liability.name
                            self.principal = base_liability.principal
                            self.interest_rate = base_liability.interest_rate
                            self.term_years = base_liability.term_years
                            self.start_year = start_year
                            self._payment = self.calculate_payment()  # Calculate payment once

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
                            remaining_payments = (self.term_years - adjusted_year) * 12
                            return (self._payment * ((1 - (1 + monthly_rate)**(-remaining_payments)) / monthly_rate))

                        def get_annual_payment(self) -> float:
                            return self._payment * 12

                    liabilities.append(TimedLiability(liability, milestone.trigger_year))

                income.extend(milestone.income_adjustments)

        return assets, liabilities, income, expenses