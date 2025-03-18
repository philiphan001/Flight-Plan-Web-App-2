from typing import List, Dict
from models.financial_models import *

class FinancialCalculator:
    def __init__(self, assets: List[Asset], liabilities: List[Liability],
                 income: List[Income], expenses: List[Expense]):
        self.assets = assets
        self.liabilities = liabilities
        self.income = income
        # Include tax expenses from income sources
        self.expenses = expenses + [inc.get_tax_expense() for inc in income]

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
            'tax_breakdown': {}
        }

        # Initialize income streams
        income_streams = {}
        for inc in self.income:
            income_streams[inc.name] = []

        # Initialize expense categories including taxes
        expense_categories = {}
        for expense in self.expenses:
            category = expense.name
            if isinstance(expense, TaxExpense):
                category = "Taxes"  # Group all tax expenses under "Taxes" category
            if category not in expense_categories:
                expense_categories[category] = [0] * projection_years

        # Initialize tax breakdown
        tax_categories = {
            'payroll_taxes': [0] * projection_years,
            'income_taxes': [0] * projection_years,
            'total_taxes': [0] * projection_years
        }

        cumulative_savings = 0
        for year in range(projection_years):
            # Calculate income streams
            total_income = 0
            for inc in self.income:
                income_amount = int(round(inc.calculate_income(year)))
                income_streams[inc.name].append(income_amount)
                total_income += income_amount

            projections['total_income'].append(total_income)
            projections['income_streams'] = income_streams

            # Calculate expenses including tax expenses
            total_expenses = 0
            total_taxes = 0
            payroll_taxes = 0
            income_taxes = 0

            for expense in self.expenses:
                category = expense.name
                if isinstance(expense, TaxExpense):
                    category = "Taxes"
                    # Get detailed tax breakdown
                    tax_calc = expense.income_source.calculate_taxes(year)
                    payroll_taxes += tax_calc['fica_taxes']['total_fica']
                    income_taxes += tax_calc['federal_taxes']['federal_tax']

                expense_amount = int(round(expense.calculate_expense(year)))
                expense_categories[category][year] += expense_amount

                if isinstance(expense, TaxExpense):
                    total_taxes += expense_amount
                total_expenses += expense_amount

            # Update tax breakdown
            tax_categories['payroll_taxes'][year] = int(round(payroll_taxes))
            tax_categories['income_taxes'][year] = int(round(income_taxes))
            tax_categories['total_taxes'][year] = int(round(total_taxes))

            projections['total_expenses'].append(total_expenses)
            projections['expense_categories'] = expense_categories
            projections['tax_breakdown'] = tax_categories

            # Calculate cash flow (income minus all expenses including taxes)
            cash_flow = total_income - total_expenses
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