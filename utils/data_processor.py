import pandas as pd
from typing import Dict, List, Tuple
from models.financial_models import *

class DataProcessor:
    @staticmethod
    def load_coli_data(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            required_columns = ['Cost of Living', 'Housing', 'Monthly Expense', 'Income Adjustment Factor', 'Average Price of Starter Home']
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
                            location: str, occupation: str) -> Dict:
        # Convert location and occupation to string for comparison
        location_data = coli_df[coli_df['Cost of Living'].astype(str) == str(location)].iloc[0]
        occupation_data = occupation_df[occupation_df['Occupation'].astype(str) == str(occupation)].iloc[0]

        return {
            'cost_of_living': float(location_data['Monthly Expense']),
            'home_price': float(location_data['Average Price of Starter Home']),
            'location_adjustment': float(location_data['Income Adjustment Factor']),
            'base_income': float(occupation_data['Monthly Income']) * 12  # Convert to annual
        }

    @staticmethod
    def create_financial_objects(location_data: Dict, 
                               is_homeowner: bool) -> Tuple[List[Asset], List[Liability], List[Income], List[Expense]]:
        assets = []
        liabilities = []
        income = []
        expenses = []

        # Create Income objects
        base_salary = Salary(location_data['base_income'], location_data['location_adjustment'])
        income.append(base_salary)

        # Create Asset and Liability objects based on housing situation
        if is_homeowner:
            home = Home("Primary Residence", location_data['home_price'])
            mortgage = MortgageLoan(location_data['home_price'] * 0.8, 0.035)
            assets.append(home)
            liabilities.append(mortgage)
            expenses.append(FixedExpense("Property Tax", location_data['home_price'] * 0.015))
            expenses.append(FixedExpense("Home Insurance", location_data['home_price'] * 0.005))
            expenses.append(FixedExpense("Home Maintenance", location_data['home_price'] * 0.01))
        else:
            expenses.append(FixedExpense("Rent", location_data['cost_of_living'] * 0.4))

        # Add basic living expenses
        expenses.append(VariableExpense("Living Expenses", location_data['cost_of_living'] * 0.6))

        return assets, liabilities, income, expenses