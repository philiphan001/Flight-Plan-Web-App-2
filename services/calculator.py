from typing import List, Dict, Optional
from models.financial_models import *

class FinancialCalculator:
    def __init__(self, assets: List[Asset], liabilities: List[Liability],
                 income: List[Income], expenses: List[Expense], 
                 milestones: Optional[List[Milestone]] = None):
        self.assets = assets
        self.liabilities = liabilities
        self.income = income
        self.expenses = expenses
        self.milestones = milestones or []

    def calculate_yearly_projection(self, projection_years: int) -> Dict:
        projections = {
            'years': list(range(projection_years)),
            'net_worth': [],
            'cash_flow': [],
            'total_income': [],
            'total_expenses': [],
            'asset_values': [],
            'liability_values': [],
            'investment_growth': [],
            'milestones': {}  # Track milestones in projections
        }

        # Sort milestones by year
        sorted_milestones = sorted(self.milestones, key=lambda m: m.year)
        
        # Track active temporary effects (like education)
        active_effects = []
        
        cumulative_savings = 0
        for year in range(projection_years):
            # Apply milestones for this year
            year_milestones = [m for m in sorted_milestones if m.year == year and not m.applied]
            
            for milestone in year_milestones:
                self._apply_milestone(milestone, year)
                milestone.applied = True
                
                # Record milestone in projections
                if year not in projections['milestones']:
                    projections['milestones'][year] = []
                projections['milestones'][year].append(milestone.name)
            
            # Update active effects (e.g., education duration)
            self._update_active_effects(active_effects, year)
            
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
        
    def _apply_milestone(self, milestone: Milestone, year: int) -> None:
        """Apply the financial impact of a milestone."""
        impact = milestone.get_financial_impact()
        
        # Handle income changes
        if "income_multiplier" in impact:
            for inc in self.income:
                if isinstance(inc, Salary):
                    inc.annual_amount *= impact["income_multiplier"]
        
        if "income_increase_pct" in impact:
            for inc in self.income:
                if isinstance(inc, Salary):
                    inc.annual_amount *= (1 + impact["income_increase_pct"])
        
        # Handle expense changes
        if "expense_multiplier" in impact:
            for exp in self.expenses:
                exp.annual_amount *= impact["expense_multiplier"]
        
        if "annual_expense_increase" in impact:
            # Add a new fixed expense
            self.expenses.append(
                FixedExpense(f"Child Expenses ({milestone.name})", 
                           impact["annual_expense_increase"])
            )
            
        if "expense_changes" in impact:
            for exp_name, amount in impact["expense_changes"].items():
                self.expenses.append(FixedExpense(exp_name, amount))
        
        if "remove_expense" in impact:
            self.expenses = [e for e in self.expenses 
                           if e.name != impact["remove_expense"]]
        
        # Handle asset changes
        if "add_asset" in impact:
            asset_info = impact["add_asset"]
            asset_type = asset_info.pop("type")
            
            if asset_type == "Home":
                self.assets.append(Home(**asset_info))
            elif asset_type == "DepreciableAsset":
                self.assets.append(DepreciableAsset(**asset_info))
            elif asset_type == "Investment":
                self.assets.append(Investment(**asset_info))
        
        # Handle liability changes
        if "add_liability" in impact:
            liability_info = impact["add_liability"]
            liability_type = liability_info.pop("type")
            
            if liability_type == "MortgageLoan":
                self.liabilities.append(MortgageLoan(**liability_info))
            elif liability_type == "Loan":
                name = liability_info.pop("name", "Loan")
                self.liabilities.append(
                    Loan(name, **liability_info)
                )
        
        # Handle investment changes
        if "add_investment" in impact:
            inv_info = impact["add_investment"]
            new_investment = Investment(
                name=inv_info["name"],
                initial_value=inv_info["initial_value"],
                return_rate=inv_info["return_rate"]
            )
            self.assets.append(new_investment)
            
            # Add a new expense for the contribution
            if "annual_contribution" in inv_info:
                self.expenses.append(
                    FixedExpense(f"Contribution to {inv_info['name']}", 
                               inv_info["annual_contribution"])
                )
    
    def _update_active_effects(self, active_effects, current_year):
        """Update any active temporary effects from milestones."""
        # This is a placeholder for handling multi-year effects
        # like education or other temporary financial impacts
        pass