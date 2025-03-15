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
            'income_streams': {},  # Initialize income_streams dictionary
            'total_expenses': [],
            'expense_categories': {},
            'asset_values': [],
            'asset_breakdown': {},
            'liability_values': [],
            'liability_breakdown': {},
            'investment_growth': []
        }

        # Initialize income streams
        income_streams = {}
        for inc in self.income:
            income_streams[inc.name] = []

        for year in range(projection_years):
            # Calculate income streams for each income source
            for inc in self.income:
                if inc.name not in income_streams:
                    income_streams[inc.name] = []
                income_amount = round(inc.calculate_income(year))
                income_streams[inc.name].append(income_amount)

            # Calculate total income
            total_income = round(sum(inc.calculate_income(year) for inc in self.income))
            projections['total_income'].append(total_income)
            projections['income_streams'] = income_streams  # Store income streams in projections

            # Calculate expenses by category
            total_expenses = 0
            for expense in self.expenses:
                category = expense.name
                if "One-time Cost" in category:
                    milestone_name = category.replace(" One-time Cost", "")
                    category = f"One-time: {milestone_name}"
                    expense_amount = round(expense.calculate_expense(year)) if expense.name.endswith(f"Year {year}") else 0
                else:
                    expense_amount = round(expense.calculate_expense(year))

                if category not in expense_categories:
                    expense_categories[category] = [0] * projection_years
                expense_categories[category].append(expense_amount)
                total_expenses += expense_amount

            projections['total_expenses'].append(total_expenses)
            projections['expense_categories'] = expense_categories

            # Calculate cash flow (savings)
            cash_flow = round(total_income - total_expenses)
            projections['cash_flow'].append(cash_flow)

            # Add cash flow to cumulative savings for investment
            cumulative_savings += cash_flow

            # Update the investment asset with new savings
            for asset in self.assets:
                if isinstance(asset, Investment) and asset.name == "Savings":
                    asset.add_contribution(cash_flow)

            # Calculate asset values including investment growth
            total_asset_value = 0
            for asset in self.assets:
                asset_value = round(asset.calculate_value(year))
                asset_type = asset.__class__.__name__
                asset_key = f"{asset_type}: {asset.name}"
                if asset_key not in asset_breakdown:
                    asset_breakdown[asset_key] = [0] * projection_years
                asset_breakdown[asset_key].append(asset_value)
                total_asset_value += asset_value

            projections['asset_values'].append(total_asset_value)
            projections['asset_breakdown'] = asset_breakdown

            # Calculate investment growth
            investment_growth = round(next(
                (asset.calculate_value(year) for asset in self.assets
                 if isinstance(asset, Investment) and asset.name == "Savings"),
                0
            ))
            projections['investment_growth'].append(investment_growth)

            # Calculate liability values
            total_liability_value = 0
            for liability in self.liabilities:
                liability_value = round(liability.get_balance(year))
                liability_type = liability.__class__.__name__
                liability_key = f"{liability_type}: {liability.name}"
                if liability_key not in liability_breakdown:
                    liability_breakdown[liability_key] = [0] * projection_years
                liability_breakdown[liability_key].append(liability_value)
                total_liability_value += liability_value

            projections['liability_values'].append(total_liability_value)
            projections['liability_breakdown'] = liability_breakdown

            # Calculate net worth
            net_worth = round(total_asset_value - total_liability_value)
            projections['net_worth'].append(net_worth)

        return projections