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
            'expense_categories': {},
            'asset_values': [],
            'liability_values': [],
            'investment_growth': []
        }

        # Initialize expense categories
        expense_categories = {}
        for expense in self.expenses:
            category = expense.name
            if "One-time Cost" in category:
                milestone_name = category.replace(" One-time Cost", "")
                category = f"One-time: {milestone_name}"
            expense_categories[category] = []

        cumulative_savings = 0
        for year in range(projection_years):
            # Calculate total income
            total_income = sum(inc.calculate_income(year) for inc in self.income)
            projections['total_income'].append(total_income)

            # Calculate expenses by category
            total_expenses = 0
            for expense in self.expenses:
                category = expense.name
                if "One-time Cost" in category:
                    milestone_name = category.replace(" One-time Cost", "")
                    category = f"One-time: {milestone_name}"
                    # Only apply one-time costs in their specific year
                    expense_amount = expense.calculate_expense(year) if expense.name.endswith(f"Year {year}") else 0
                else:
                    expense_amount = expense.calculate_expense(year)

                if category not in expense_categories:
                    expense_categories[category] = [0] * projection_years
                expense_categories[category].append(expense_amount)
                total_expenses += expense_amount

            projections['total_expenses'].append(total_expenses)
            projections['expense_categories'] = expense_categories

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