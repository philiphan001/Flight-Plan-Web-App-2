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

        # Create Income objects
        base_salary = Salary(location_data['base_income'], location_data['location_adjustment'])
        income.append(base_salary)

        # Create Investment asset for savings (starts at 0)
        investment = Investment("Savings", 0, location_data['investment_return_rate'])
        assets.append(investment)

        # Create Asset and Liability objects based on housing situation
        if is_homeowner:
            home = Home("Primary Residence", location_data['home_price'])
            mortgage = MortgageLoan(location_data['home_price'] * 0.8, 0.035)  # 80% LTV, 3.5% interest
            assets.append(home)
            liabilities.append(mortgage)
            expenses.append(FixedExpense("Property Tax", location_data['home_price'] * 0.015))
            expenses.append(FixedExpense("Home Insurance", location_data['home_price'] * 0.005))
            expenses.append(FixedExpense("Home Maintenance", location_data['housing'] * 12))
        else:
            expenses.append(FixedExpense("Rent", location_data['housing'] * 12))

        # Add categorized monthly expenses (converted to annual)
        expenses.append(FixedExpense("Transportation", location_data['transportation'] * 12))
        expenses.append(VariableExpense("Food", location_data['food'] * 12))
        expenses.append(FixedExpense("Healthcare", location_data['healthcare'] * 12))
        expenses.append(FixedExpense("Insurance", location_data['insurance'] * 12))
        expenses.append(VariableExpense("Apparel", location_data['apparel'] * 12))
        expenses.append(VariableExpense("Services", location_data['services'] * 12))
        expenses.append(VariableExpense("Entertainment", location_data['entertainment'] * 12))
        expenses.append(VariableExpense("Other", location_data['other'] * 12))

        # Add milestone-related financial objects
        if milestones:
            for milestone in milestones:
                assets.extend(milestone.assets)
                liabilities.extend(milestone.liabilities)
                income.extend(milestone.income_adjustments)
                expenses.extend(milestone.recurring_expenses)
                if milestone.one_time_expense > 0:
                    expenses.append(
                        FixedExpense(f"{milestone.name} One-time Cost", 
                                   milestone.one_time_expense,
                                   inflation_rate=0)  # One-time expenses don't inflate
                    )

        return assets, liabilities, income, expenses