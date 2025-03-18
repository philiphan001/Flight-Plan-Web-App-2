from typing import List, Dict
from models.financial_models import *
from models.tax_calculator import TaxCalculator

class FinancialCalculator:
    def __init__(self, assets: List[Asset], liabilities: List[Liability],
                 income: List[Income], expenses: List[Expense]):
        self.assets = assets
        self.liabilities = liabilities
        self.income = income
        self.expenses = expenses
        self.tax_calculator = TaxCalculator()

    def calculate_yearly_projection(self, projection_years: int) -> Dict:
        projections = {
            'years': list(range(projection_years)),
            'net_worth': [],
            'cash_flow': [],
            'total_income': [],
            'income_streams': {},
            'total_expenses': [],
            'expense_categories': {},
            'tax_breakdown': {
                'federal_tax': [],
                'state_tax': [],
                'social_security': [],
                'medicare': [],
                'total_tax': []
            },
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
            year_federal_tax = 0
            year_state_tax = 0
            year_social_security = 0
            year_medicare = 0
            year_total_tax = 0

            for inc in self.income:
                income_details = inc.calculate_net_income(year)
                income_amount = income_details['gross_income']
                income_streams[inc.name].append(income_amount)
                total_income += income_amount

                # Accumulate tax totals
                year_federal_tax += income_details['federal_tax']
                year_state_tax += income_details['state_tax']
                year_social_security += income_details['social_security']
                year_medicare += income_details['medicare']
                year_total_tax += income_details['total_tax']

            # Update income and tax projections
            projections['total_income'].append(total_income)
            projections['income_streams'] = income_streams
            projections['tax_breakdown']['federal_tax'].append(year_federal_tax)
            projections['tax_breakdown']['state_tax'].append(year_state_tax)
            projections['tax_breakdown']['social_security'].append(year_social_security)
            projections['tax_breakdown']['medicare'].append(year_medicare)
            projections['tax_breakdown']['total_tax'].append(year_total_tax)

            # Add tax expenses to expense categories
            expense_categories['Federal Income Tax'] = projections['tax_breakdown']['federal_tax']
            expense_categories['State Income Tax'] = projections['tax_breakdown']['state_tax']
            expense_categories['Social Security Tax'] = projections['tax_breakdown']['social_security']
            expense_categories['Medicare Tax'] = projections['tax_breakdown']['medicare']


            # Calculate other expenses
            total_expenses = year_total_tax  # Start with tax expenses
            for expense in self.expenses:
                if not isinstance(expense, TaxExpense):  # Skip tax expenses as they're handled above
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

            # Calculate cash flow (after-tax)
            cash_flow = int(round(total_income - total_expenses))
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