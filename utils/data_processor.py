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
        """Process location and occupation data"""
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
                'investment_return_rate': investment_return_rate,
                'location': location
            }
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error processing location data: {str(e)}")

    @staticmethod
    def create_financial_objects(location_data: Dict, 
                            milestones: Optional[List[Milestone]] = None) -> Tuple[List[Asset], List[Liability], List[Income], List[Expense]]:
        """Create financial objects based on location data and milestones"""
        assets = []
        liabilities = []
        income = []
        expenses = []

        # Create primary salary income
        base_salary = Salary(location_data['base_income'], location_data['location_adjustment'])
        income.append(base_salary)

        # Create Investment asset
        investment = Investment("Savings", 0, location_data['investment_return_rate'])
        assets.append(investment)

        # Find marriage milestone and spouse income if exists
        marriage_year = None
        spouse_income = None
        if milestones:
            for milestone in milestones:
                if milestone.name == "Marriage":
                    marriage_year = milestone.trigger_year
                    # Find spouse income in marriage milestone
                    for inc in milestone.income_adjustments:
                        if isinstance(inc, SpouseIncome):
                            spouse_income = inc
                            break
                    break

        # Create tax expense with marriage information if applicable
        tax_expense = TaxExpense(
            name="Taxes",
            base_income=location_data['base_income'] * location_data['location_adjustment'],  # Use adjusted base income
            tax_year=2024
        )

        # Set marriage information if applicable
        if marriage_year is not None and spouse_income is not None:
            tax_expense.set_marriage_info(marriage_year, spouse_income.annual_amount)

        expenses.append(tax_expense)

        # Add basic living expenses
        expenses.extend([
            FixedExpense("Housing", location_data['housing'] * 12),
            FixedExpense("Transportation", location_data['transportation'] * 12),
            VariableExpense("Food", location_data['food'] * 12),
            FixedExpense("Healthcare", location_data['healthcare'] * 12),
            FixedExpense("Insurance", location_data['insurance'] * 12),
            VariableExpense("Apparel", location_data['apparel'] * 12),
            VariableExpense("Services", location_data['services'] * 12),
            VariableExpense("Entertainment", location_data['entertainment'] * 12),
            VariableExpense("Other", location_data['other'] * 12)
        ])

        # Add milestone-related financial objects
        if milestones:
            for milestone in milestones:
                # Handle one-time expenses
                if milestone.one_time_expense > 0:
                    expenses.append(FixedExpense(
                        f"{milestone.name} One-time Cost",
                        milestone.one_time_expense
                    ))

                # Add recurring expenses
                expenses.extend(milestone.recurring_expenses)

                # Add assets and liabilities
                assets.extend(milestone.assets)
                liabilities.extend(milestone.liabilities)

                # Add income adjustments
                income.extend(milestone.income_adjustments)

        return assets, liabilities, income, expenses