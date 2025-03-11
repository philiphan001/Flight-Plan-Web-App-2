from typing import List, Dict
from models.financial_models import *

class FinancialCalculator:
    def __init__(self, assets: List[Asset], liabilities: List[Liability],
                 income: List[Income], expenses: List[Expense]):
        self.assets = assets
        self.liabilities = liabilities
        self.income = income
        self.expenses = expenses

    def calculate_yearly_projection(self, projection_years: int) -> Dict:
        projections = {
            'years': list(range(projection_years)),
            'net_worth': [],
            'cash_flow': [],
            'total_income': [],
            'total_expenses': [],
            'asset_values': [],
            'liability_values': [],
            'investment_growth': []
        }

        cumulative_savings = 0
        for year in range(projection_years):
            # Calculate total income
            total_income = sum(inc.calculate_income(year) for inc in self.income)
            projections['total_income'].append(total_income)

            # Calculate total expenses
            total_expenses = sum(exp.calculate_expense(year) for exp in self.expenses)
            projections['total_expenses'].append(total_expenses)

            # Calculate cash flow (savings)
            cash_flow = total_income - total_expenses
            projections['cash_flow'].append(cash_flow)

            # Add cash flow to cumulative savings for investment
            cumulative_savings += cash_flow

            # Update the investment asset with new savings
            for asset in self.assets:
                if isinstance(asset, Investment) and asset.name == "Savings":
                    asset.add_contribution(cash_flow)

            # Calculate asset values including investment growth
            asset_value = sum(asset.calculate_value(year) for asset in self.assets)
            projections['asset_values'].append(asset_value)

            # Calculate investment growth
            investment_growth = next(
                (asset.calculate_value(year) for asset in self.assets 
                 if isinstance(asset, Investment) and asset.name == "Savings"),
                0
            )
            projections['investment_growth'].append(investment_growth)

            # Calculate liability values
            liability_value = sum(liability.get_balance(year) for liability in self.liabilities)
            projections['liability_values'].append(liability_value)

            # Calculate net worth
            net_worth = asset_value - liability_value
            projections['net_worth'].append(net_worth)

        return projections