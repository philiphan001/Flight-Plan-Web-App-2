from typing import List, Dict, Optional
from models.financial_models import (
    Asset, Liability, Income, Expense, Tax,
    FederalIncomeTax, PayrollTax, StateIncomeTax,
    Investment, Loan, MortgageLoan, CarLoan, StudentLoan,
    LoanPayment
)

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
            'tax_expenses': [],
            'tax_breakdown': {
                'federal_income_tax': [],
                'state_income_tax': [],
                'payroll_tax': []
            },
            'loan_details': {
                'by_type': {},
                'by_id': {},
                'total_balances': [],
                'total_payments': []
            }
        }

        # Initialize loan tracking
        loan_types = {MortgageLoan, CarLoan, StudentLoan, Loan}  # Include base Loan class
        for loan_type in loan_types:
            projections['loan_details']['by_type'][loan_type.__name__] = {
                'balances': [],
                'payments': [],
                'count': 0
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

            projections['total_income'].append(total_income)
            projections['income_streams'] = income_streams

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

            projections['tax_breakdown']['federal_income_tax'].append(federal_tax)
            projections['tax_breakdown']['state_income_tax'].append(state_tax)
            projections['tax_breakdown']['payroll_tax'].append(payroll_tax)

            total_tax = federal_tax + state_tax + payroll_tax
            projections['tax_expenses'].append(total_tax)

            # Calculate regular expenses
            total_regular_expenses = 0
            for expense in self.expenses:
                category = expense.name
                
                # Special handling for loan payments
                if isinstance(expense, LoanPayment):
                    # For loan payments, use their built-in term handling
                    expense_amount = int(round(expense.calculate_expense(year)))
                    
                    # Find the associated loan
                    loan = next((loan for loan in self.liabilities 
                                if isinstance(loan, Loan) and loan.name == expense.name.replace(" Payment", "")), None)
                    
                    # If loan exists and is paid off, set expense to 0
                    if loan and loan.get_balance(year) <= 0:
                        expense_amount = 0
                else:
                    # For other expenses, use their built-in calculation method
                    expense_amount = int(round(expense.calculate_expense(year)))
                
                # Special categorization for graduate school expenses
                if "Graduate School Year" in category and "Out-of-pocket" in category and expense_amount > 0:
                    category = f"One-time: {category}"  # Categorize as one-time expense
                elif "Graduate School Year" in category and "Loan Payment" in category and expense_amount > 0:
                    year_num = int(category.split("Year ")[1].split(" ")[0])
                    category = f"Loan Payment: Graduate School Year {year_num}"
                
                # Add non-zero expenses to the categories
                if expense_amount > 0:
                    if category not in expense_categories:
                        expense_categories[category] = [0] * projection_years
                    expense_categories[category][year] = expense_amount
                    total_regular_expenses += expense_amount

            # Total expenses including taxes
            total_expenses = total_regular_expenses + total_tax
            projections['total_expenses'].append(total_expenses)
            projections['expense_categories'] = expense_categories

            # Calculate cash flow (after taxes)
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

            # Calculate liability values and track loan details
            total_liability_value = 0
            total_loan_balance = 0
            total_loan_payment = 0

            for liability in self.liabilities:
                if isinstance(liability, Loan):
                    # Track loan by type
                    loan_type = liability.__class__.__name__
                    if loan_type in projections['loan_details']['by_type']:
                        loan_type_data = projections['loan_details']['by_type'][loan_type]
                        loan_type_data['count'] += 1
                        
                        # Calculate loan balance and payment
                        loan_balance = int(round(liability.get_balance(year)))
                        loan_payment = int(round(liability.get_payment(year)))
                        
                        # Update type-specific tracking
                        loan_type_data['balances'].append(loan_balance)
                        loan_type_data['payments'].append(loan_payment)
                        
                        # Update total loan values
                        total_loan_balance += loan_balance
                        total_loan_payment += loan_payment
                        
                        # Track individual loan by ID
                        if liability.loan_id not in projections['loan_details']['by_id']:
                            projections['loan_details']['by_id'][liability.loan_id] = {
                                'name': liability.name,
                                'type': loan_type,
                                'balances': [],
                                'payments': [],
                                'institution': getattr(liability, 'institution', None)
                            }
                        
                        # Update individual loan tracking
                        loan_data = projections['loan_details']['by_id'][liability.loan_id]
                        loan_data['balances'].append(loan_balance)
                        loan_data['payments'].append(loan_payment)
                        
                        # Update liability breakdown
                        liability_key = f"{loan_type}: {liability.name}"
                        if liability_key not in liability_breakdown:
                            liability_breakdown[liability_key] = [0] * projection_years
                        liability_breakdown[liability_key][year] = loan_balance
                        
                        total_liability_value += loan_balance

            # Update loan summary data
            projections['loan_details']['total_balances'].append(total_loan_balance)
            projections['loan_details']['total_payments'].append(total_loan_payment)

            projections['liability_values'].append(total_liability_value)
            projections['liability_breakdown'] = liability_breakdown

            # Calculate net worth
            net_worth = int(round(total_asset_value - total_liability_value))
            projections['net_worth'].append(net_worth)

        return projections