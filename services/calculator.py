from typing import List, Dict, Optional
from models.financial_models import *

class FinancialCalculator:
    def __init__(self, assets: List[Asset], liabilities: List[Liability],
                 income: List[Income], expenses: List[Expense], 
                 taxes: Optional[List[Tax]] = None):
        self.assets = assets
        self.liabilities = liabilities
        self.income = income
        self.expenses = expenses
        self.taxes = taxes or [
            FederalIncomeTax(),
            PayrollTax(),
            StateIncomeTax()
        ]

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
            'tax_expenses': [],  # Total tax expenses
            'tax_breakdown': {   # Detailed tax breakdown
                'federal_income_tax': [],
                'state_income_tax': [],
                'payroll_tax': []
            }
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

        # Add tax categories
        expense_categories['Federal Income Tax'] = [0] * projection_years
        expense_categories['State Income Tax'] = [0] * projection_years
        expense_categories['Payroll Tax'] = [0] * projection_years

        # Initialize asset and liability breakdowns
        asset_breakdown = {}
        liability_breakdown = {}

        cumulative_savings = 0
        for year in range(projection_years):
            # Calculate income streams for each income source
            total_income = 0
            for inc in self.income:
                income_amount = int(round(inc.calculate_income(year)))
                income_streams[inc.name].append(income_amount)
                total_income += income_amount

            # Calculate tax expenses
            federal_tax = 0
            state_tax = 0
            payroll_tax = 0

            for tax in self.taxes:
                tax_amount = int(round(tax.calculate_tax(year, total_income)))
                if isinstance(tax, FederalIncomeTax):
                    federal_tax = tax_amount
                    expense_categories['Federal Income Tax'][year] = federal_tax
                elif isinstance(tax, StateIncomeTax):
                    state_tax = tax_amount
                    expense_categories['State Income Tax'][year] = state_tax
                elif isinstance(tax, PayrollTax):
                    payroll_tax = tax_amount
                    expense_categories['Payroll Tax'][year] = payroll_tax

            # Calculate regular expenses and loan payments
            total_regular_expenses = 0
            for expense in self.expenses:
                category = expense.name
                # For graduate school expenses, handle as one-time costs
                if "Graduate School Year" in category and "Out-of-pocket" in category:
                    # Extract the year number and calculate target year
                    year_num = int(category.split("Year ")[1].split(" ")[0]) - 1
                    target_year = expense._milestone.trigger_year + year_num
                    # Only apply the expense in its specific year
                    if year == target_year:
                        expense_amount = int(round(expense.annual_amount))
                        category = f"One-time: {category}"  # Categorize as one-time expense
                    else:
                        expense_amount = 0
                elif "Graduate School Year" in category and "Loan Payment" in category:
                    # Extract loan year and find corresponding loan
                    year_num = int(category.split("Year ")[1].split(" ")[0]) - 1
                    loan_name = f"Graduate School Year {year_num + 1} Loan"
                    # Find the corresponding loan
                    loan = next((l for l in self.liabilities if l.name == loan_name), None)
                    if loan and isinstance(loan, StudentLoan):
                        # Only apply payment after deferment period
                        expense_amount = int(round(loan.get_payment(year - loan._milestone.trigger_year)))
                        category = f"Loan Payment: Graduate School Year {year_num + 1}"  # Categorize loan payments
                    else:
                        expense_amount = 0
                else:
                    # Regular recurring expenses
                    expense_amount = int(round(expense.calculate_expense(year)))

                # Add to expense categories
                if category not in expense_categories:
                    expense_categories[category] = [0] * projection_years
                expense_categories[category][year] = expense_amount
                total_regular_expenses += expense_amount

            # Update projections
            projections['total_income'].append(total_income)
            projections['income_streams'] = income_streams

            total_tax = federal_tax + state_tax + payroll_tax
            projections['tax_expenses'].append(total_tax)
            projections['tax_breakdown']['federal_income_tax'].append(federal_tax)
            projections['tax_breakdown']['state_income_tax'].append(state_tax)
            projections['tax_breakdown']['payroll_tax'].append(payroll_tax)

            # Total expenses including taxes
            total_expenses = total_regular_expenses + total_tax
            projections['total_expenses'].append(total_expenses)
            projections['expense_categories'] = expense_categories

            # Calculate cash flow (after taxes)
            cash_flow = total_income - total_expenses
            projections['cash_flow'].append(cash_flow)

            # Add cash flow to cumulative savings
            cumulative_savings += cash_flow

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

            # Calculate liability values
            total_liability_value = 0
            for liability in self.liabilities:
                # For graduate school loans, check if we've reached their start year
                liability_value = 0
                if "Graduate School Year" in liability.name:
                    # Extract the year number and calculate when this loan starts
                    year_num = int(liability.name.split("Year ")[1].split(" ")[0]) - 1
                    try: #Attempt to access from liability.  If it fails, assume 0.
                        loan_start_year = liability._milestone.trigger_year + year_num
                    except AttributeError:
                        loan_start_year = 0
                    if year >= loan_start_year:
                        liability_value = int(round(liability.get_balance(year - loan_start_year)))
                else:
                    liability_value = int(round(liability.get_balance(year)))

                liability_type = liability.__class__.__name__
                liability_key = f"{liability_type}: {liability.name}"
                if liability_key not in liability_breakdown:
                    liability_breakdown[liability_key] = [0] * projection_years
                liability_breakdown[liability_key][year] = liability_value
                total_liability_value += liability_value

            # Update remaining projections
            projections['asset_values'].append(total_asset_value)
            projections['asset_breakdown'] = asset_breakdown
            projections['liability_values'].append(total_liability_value)
            projections['liability_breakdown'] = liability_breakdown
            projections['net_worth'].append(total_asset_value - total_liability_value)

        return projections