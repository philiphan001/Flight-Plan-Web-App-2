from typing import Dict, List

class FinancialCalculator:
    def calculate_yearly_projection(self, projection_years: int = 40) -> Dict[str, List[float]]:
        """Calculate yearly projections for all financial metrics"""
        # Initialize lists for each metric
        yearly_metrics = {
            'income': [],
            'expenses': [],
            'savings': [],
            'net_worth': [],
            'liability_value': [],
            'asset_value': [],
            'loan_balance': [],
            'loan_payment': [],
            'expense_categories': {},
            'liability_breakdown': {},
            'income_breakdown': {}
        }

        # Initialize expense categories
        expense_categories = {}
        liability_breakdown = {}
        income_breakdown = {}

        # Create a map of paid-off loans for each year
        paid_off_loans = {}
        for liability in self.liabilities:
            if isinstance(liability, Loan):
                paid_off_loans[liability.name] = [
                    year >= (liability.start_year + liability.term_years)
                    for year in range(projection_years)
                ]

        # Calculate projections for each year
        for year in range(projection_years):
            # Calculate income
            total_income = self.calculate_income(year)
            yearly_metrics['income'].append(total_income)

            # Calculate expenses
            total_expenses = 0
            for expense in self.expenses:
                # Check if this is a payment for a paid-off loan
                expense_amount = 0
                for loan_name, is_paid_off in paid_off_loans.items():
                    if loan_name in expense.name and is_paid_off[year]:
                        break
                else:
                    expense_amount = int(round(expense.calculate_expense(year)))
                
                total_expenses += expense_amount
                
                # Track expense categories
                category = expense.name
                if category not in expense_categories:
                    expense_categories[category] = [0] * projection_years
                expense_categories[category][year] = expense_amount

            yearly_metrics['expenses'].append(total_expenses)

            # Calculate savings
            yearly_savings = total_income - total_expenses
            yearly_metrics['savings'].append(yearly_savings)

            # Calculate liability values and track loan details
            total_liability_value = 0
            total_loan_balance = 0
            total_loan_payment = 0

            for liability in self.liabilities:
                if isinstance(liability, Loan):
                    # Calculate loan balance and payment
                    loan_balance = liability.get_balance(year)
                    loan_payment = liability.get_payment(year)
                    
                    # Add to totals
                    total_liability_value += loan_balance
                    total_loan_balance += loan_balance
                    total_loan_payment += loan_payment

                    # Track individual loan details
                    liability_key = liability.name
                    if liability_key not in liability_breakdown:
                        liability_breakdown[liability_key] = [0] * projection_years
                    liability_breakdown[liability_key][year] = loan_balance

                    # Debug output for loan status
                    print(f"Year {year} - Loan: {liability.name}")
                    print(f"  Balance: ${loan_balance:,.2f}")
                    print(f"  Payment: ${loan_payment:,.2f}")
                    print(f"  Start Year: {liability.start_year}")
                    print(f"  Term Years: {liability.term_years}")
                    print(f"  Paid Off: {year >= (liability.start_year + liability.term_years)}")
                else:
                    # Handle non-loan liabilities
                    liability_value = liability.calculate_value(year)
                    total_liability_value += liability_value
                    liability_key = liability.name
                    if liability_key not in liability_breakdown:
                        liability_breakdown[liability_key] = [0] * projection_years
                    liability_breakdown[liability_key][year] = liability_value

            yearly_metrics['liability_value'].append(total_liability_value)
            yearly_metrics['loan_balance'].append(total_loan_balance)
            yearly_metrics['loan_payment'].append(total_loan_payment)

            # Calculate asset values
            total_asset_value = 0
            for asset in self.assets:
                asset_value = asset.calculate_value(year)
                total_asset_value += asset_value
                asset_key = asset.name
                if asset_key not in yearly_metrics:
                    yearly_metrics[asset_key] = [0] * projection_years
                yearly_metrics[asset_key][year] = asset_value

            yearly_metrics['asset_value'].append(total_asset_value)

            # Calculate net worth
            yearly_metrics['net_worth'].append(total_asset_value - total_liability_value)

            # Track income breakdown
            for income in self.income_adjustments:
                income_value = income.calculate_adjustment(year)
                income_key = income.name
                if income_key not in income_breakdown:
                    income_breakdown[income_key] = [0] * projection_years
                income_breakdown[income_key][year] = income_value

        # Add breakdowns to yearly metrics
        yearly_metrics['expense_categories'] = expense_categories
        yearly_metrics['liability_breakdown'] = liability_breakdown
        yearly_metrics['income_breakdown'] = income_breakdown

        return yearly_metrics 