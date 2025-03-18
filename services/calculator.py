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
            'income_streams': {},
            'total_expenses': [],
            'expense_categories': {},
            'asset_values': [],
            'asset_breakdown': {},
            'liability_values': [],
            'liability_breakdown': {},
            'investment_growth': [],
            'tax_breakdown': {}  # New field for tax details
        }

        # Initialize income streams
        income_streams = {}
        for inc in self.income:
            income_streams[inc.name] = []

        # Initialize tax categories
        tax_categories = {
            'payroll_taxes': [],
            'income_taxes': [],
            'total_taxes': []
        }

        # Initialize expense categories
        expense_categories = {}
        for expense in self.expenses:
            category = expense.name
            if "One-time Cost" in category:
                milestone_name = category.replace(" One-time Cost", "")
                category = f"One-time: {milestone_name}"
            if category not in expense_categories:
                expense_categories[category] = [0] * projection_years

        # Initialize asset and liability breakdowns
        asset_breakdown = {}
        liability_breakdown = {}

        cumulative_savings = 0
        for year in range(projection_years):
            # Calculate income and taxes for each income source
            total_income = 0
            total_taxes = 0
            payroll_taxes = 0
            income_taxes = 0

            for inc in self.income:
                income_amount = int(round(inc.calculate_income(year)))
                income_streams[inc.name].append(income_amount)
                total_income += income_amount

                # Calculate taxes for this income stream
                tax_calc = inc.calculate_taxes(year)
                payroll_taxes += tax_calc['fica_taxes']['total_fica']
                income_taxes += tax_calc['federal_taxes']['federal_tax']

            total_taxes = payroll_taxes + income_taxes

            # Add tax information to projections
            tax_categories['payroll_taxes'].append(int(round(payroll_taxes)))
            tax_categories['income_taxes'].append(int(round(income_taxes)))
            tax_categories['total_taxes'].append(int(round(total_taxes)))

            # Update projections with tax breakdown
            projections['tax_breakdown'] = tax_categories

            projections['total_income'].append(total_income)
            projections['income_streams'] = income_streams

            # Calculate expenses by category
            total_expenses = 0
            for expense in self.expenses:
                category = expense.name
                if "One-time Cost" in category:
                    milestone_name = category.replace(" One-time Cost", "")
                    category = f"One-time: {milestone_name}"

                # Handle pre-projection expenses for education
                if "Education:" in category and year == 0:
                    continue

                expense_amount = int(round(expense.calculate_expense(year)))
                expense_categories[category][year] = expense_amount
                total_expenses += expense_amount

            projections['total_expenses'].append(total_expenses)
            projections['expense_categories'] = expense_categories

            # Calculate cash flow
            cash_flow = int(round(total_income - total_expenses - total_taxes)) # Subtract taxes from cash flow
            projections['cash_flow'].append(cash_flow)

            # Add cash flow to cumulative savings
            cumulative_savings += cash_flow

            # Update the investment asset with new savings
            for asset in self.assets:
                if isinstance(asset, Investment) and asset.name == "Savings":
                    asset.add_contribution(cash_flow)

            # Calculate asset values
            total_asset_value = 0
            for asset in self.assets:
                asset_value = int(round(asset.calculate_value(year)))
                asset_type = asset.__class__.__name__
                asset_key = f"{asset_type}: {asset.name}"
                if asset_key not in asset_breakdown:
                    asset_breakdown[asset_key] = [0] * projection_years
                asset_breakdown[asset_key][year] = asset_value
                total_asset_value += asset_value

            projections['asset_values'].append(total_asset_value)
            projections['asset_breakdown'] = asset_breakdown

            # Calculate investment growth
            investment_growth = int(round(next(
                (asset.calculate_value(year) for asset in self.assets
                 if isinstance(asset, Investment) and asset.name == "Savings"),
                0
            )))
            projections['investment_growth'].append(investment_growth)

            # Calculate liability values
            total_liability_value = 0
            for liability in self.liabilities:
                # For education liabilities marked as pre-projection, start them at year 0
                liability_value = int(round(liability.get_balance(year)))
                liability_type = liability.__class__.__name__
                liability_key = f"{liability_type}: {liability.name}"
                if liability_key not in liability_breakdown:
                    liability_breakdown[liability_key] = [0] * projection_years
                liability_breakdown[liability_key][year] = liability_value
                total_liability_value += liability_value

            projections['liability_values'].append(total_liability_value)
            projections['liability_breakdown'] = liability_breakdown

            # Calculate net worth
            net_worth = int(round(total_asset_value - total_liability_value))
            projections['net_worth'].append(net_worth)

        return projections