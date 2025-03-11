import pandas as pd
from typing import Dict, List, Tuple, Optional
from models.financial_models import *

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
        # Convert location and occupation to string for comparison
        location_data = coli_df[coli_df['Cost of Living'].astype(str) == str(location)].iloc[0]
        occupation_data = occupation_df[occupation_df['Occupation'].astype(str) == str(occupation)].iloc[0]

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

    @staticmethod
    def create_financial_objects(location_data: Dict, 
                               is_homeowner: bool,
                               milestones: Optional[List[Milestone]] = None) -> Tuple[List[Asset], List[Liability], List[Income], List[Expense]]:
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

        # Create Income objects
        base_salary = Salary(location_data['base_income'], location_data['location_adjustment'])
        income.append(base_salary)

        # Create Investment asset for savings (starts at 0)
        investment = Investment("Savings", 0, location_data['investment_return_rate'])
        assets.append(investment)

        # Add basic living expenses
        expenses.append(FixedExpense("Transportation", location_data['transportation'] * 12))
        expenses.append(VariableExpense("Food", location_data['food'] * 12))
        expenses.append(FixedExpense("Healthcare", location_data['healthcare'] * 12))
        expenses.append(FixedExpense("Insurance", location_data['insurance'] * 12))
        expenses.append(VariableExpense("Apparel", location_data['apparel'] * 12))
        expenses.append(VariableExpense("Services", location_data['services'] * 12))
        expenses.append(VariableExpense("Entertainment", location_data['entertainment'] * 12))
        expenses.append(VariableExpense("Other", location_data['other'] * 12))

        # Add rent only if not a homeowner from start and no home purchase milestone
        if not is_homeowner and home_purchase_year is None:
            expenses.append(FixedExpense("Rent", location_data['housing'] * 12))
        elif not is_homeowner and home_purchase_year is not None:
            # Add rent expense that only applies before home purchase
            class PreHomeRentExpense(FixedExpense):
                def __init__(self, name: str, annual_amount: float):
                    super().__init__(name, annual_amount)
                    self.trigger_year = home_purchase_year

                def calculate_expense(self, year: int) -> float:
                    return super().calculate_expense(year) if year < self.trigger_year else 0

            expenses.append(PreHomeRentExpense("Rent", location_data['housing'] * 12))

        # Add milestone-related financial objects
        if milestones:
            for milestone in milestones:
                if milestone.one_time_expense > 0:
                    class OneTimeExpense(FixedExpense):
                        def __init__(self, name: str, amount: float, year: int):
                            super().__init__(f"{name} One-time Cost Year {year}", amount, inflation_rate=0)
                            self.trigger_year = year

                        def calculate_expense(self, year: int) -> float:
                            return self.annual_amount if year == self.trigger_year else 0

                    expenses.append(
                        OneTimeExpense(milestone.name,
                                     milestone.one_time_expense,
                                     milestone.trigger_year)
                    )

                # Add recurring expenses starting from milestone year
                for expense in milestone.recurring_expenses:
                    class PostMilestoneExpense(expense.__class__):
                        def __init__(self, base_expense, trigger_year):
                            super().__init__(base_expense.name, base_expense.annual_amount)
                            self.trigger_year = trigger_year

                        def calculate_expense(self, year: int) -> float:
                            return super().calculate_expense(year - self.trigger_year) if year >= self.trigger_year else 0

                    expenses.append(PostMilestoneExpense(expense, milestone.trigger_year))

                # Add assets and liabilities with proper timing
                for asset in milestone.assets:
                    class TimedAsset(asset.__class__):
                        def __init__(self, base_asset, start_year):
                            super().__init__(base_asset.name, base_asset.initial_value)
                            self.start_year = start_year

                        def calculate_value(self, year: int) -> float:
                            if year >= self.start_year:
                                return super().calculate_value(year - self.start_year)
                            return 0

                    assets.append(TimedAsset(asset, milestone.trigger_year))

                for liability in milestone.liabilities:
                    class TimedLiability(liability.__class__):
                        def __init__(self, base_liability, start_year):
                            super().__init__(base_liability.name, base_liability.principal,
                                          base_liability.interest_rate, base_liability.term_years)
                            self.start_year = start_year

                        def get_balance(self, year: int) -> float:
                            if year >= self.start_year:
                                return super().get_balance(year - self.start_year)
                            return 0

                    liabilities.append(TimedLiability(liability, milestone.trigger_year))

                income.extend(milestone.income_adjustments)

        return assets, liabilities, income, expenses