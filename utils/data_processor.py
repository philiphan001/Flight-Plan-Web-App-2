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

        # Add payroll tax expense for primary income
        if base_salary.payroll_tax:
            expenses.append(base_salary.payroll_tax)

        # Create Investment asset for savings (starts at 0)
        investment = Investment("Savings", 0, location_data['investment_return_rate'])
        assets.append(investment)

        # Add basic living expenses
        # Transportation expense adjusted for car ownership
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
            expenses.append(PreHomeRentExpense("Rent", location_data['housing'] * 12, home_purchase_year))
        else:
            # If no home purchase milestone, add regular rent expense
            expenses.append(FixedExpense("Rent", location_data['housing'] * 12))

        # Add milestone-related financial objects
        if milestones:
            for milestone in milestones:
                # Handle one-time expenses
                if milestone.one_time_expense > 0:
                    expenses.append(OneTimeExpense(
                        f"{milestone.name} Down Payment",
                        milestone.one_time_expense,
                        milestone.trigger_year
                    ))

                # Add recurring expenses starting from milestone year
                for expense in milestone.recurring_expenses:
                    expenses.append(PostMilestoneExpense(expense, milestone.trigger_year))

                # Add assets and liabilities with timing
                for asset in milestone.assets:
                    assets.append(TimedAsset(asset, milestone.trigger_year))

                for liability in milestone.liabilities:
                    liabilities.append(TimedLiability(liability, milestone.trigger_year))

                # For marriage milestone, add spouse's payroll tax
                if milestone.name == "Marriage":
                    for income_adj in milestone.income_adjustments:
                        if isinstance(income_adj, SpouseIncome) and income_adj.payroll_tax:
                            expenses.append(income_adj.payroll_tax)
                income.extend(milestone.income_adjustments)

        return assets, liabilities, income, expenses