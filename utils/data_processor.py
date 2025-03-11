import pandas as pd
from typing import Dict, List, Tuple
from models.financial_models import *

class DataProcessor:
    @staticmethod
    def load_financial_data(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            required_columns = ['Occupation', 'Location', 'Cost_of_Living', 'Home_Price', 'Location_Adjustment']
            if not all(col in df.columns for col in required_columns):
                raise ValueError("CSV file missing required columns")
            return df
        except Exception as e:
            raise Exception(f"Error loading financial data: {str(e)}")

    @staticmethod
    def process_location_data(df: pd.DataFrame, location: str) -> Dict:
        location_data = df[df['Location'] == location].iloc[0]
        return {
            'cost_of_living': location_data['Cost_of_Living'],
            'home_price': location_data['Home_Price'],
            'location_adjustment': location_data['Location_Adjustment']
        }

    @staticmethod
    def create_financial_objects(location_data: Dict, 
                               salary: float,
                               is_homeowner: bool) -> Tuple[List[Asset], List[Liability], List[Income], List[Expense]]:
        assets = []
        liabilities = []
        income = []
        expenses = []

        # Create Income objects
        base_salary = Salary(salary, location_data['location_adjustment'])
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
