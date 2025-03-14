import streamlit as st
import pandas as pd
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from models.financial_models import (
    MilestoneFactory, Home, MortgageLoan, Vehicle, CarLoan,
    SpouseIncome
)

st.set_page_config(page_title="ROI Analysis by Major", page_icon="📊")

def main():
    st.title("ROI Analysis by Major 📊")
    st.markdown("""
    Analyze the return on investment (ROI) for different majors and career paths.
    Compare potential earnings against education costs to make informed decisions.
    """)

    # Institution details from session state
    selected_institution = st.session_state.get('selected_institution', None)
    selected_field = st.session_state.get('selected_field', None)

    if selected_institution and selected_field:
        st.info(f"Analyzing ROI for {selected_field} at {selected_institution['name']}")
        
        # Cost inputs
        st.subheader("Education Costs")
        col1, col2 = st.columns(2)
        
        with col1:
            tuition = st.number_input(
                "Annual Tuition ($)",
                value=float(selected_institution.get('in_state_tuition', 30000)),
                step=1000.0
            )
            years = st.number_input(
                "Program Length (years)",
                min_value=1,
                max_value=6,
                value=4
            )
            
        with col2:
            living_expenses = st.number_input(
                "Annual Living Expenses ($)",
                value=15000.0,
                step=1000.0
            )
            books_supplies = st.number_input(
                "Annual Books & Supplies ($)",
                value=1200.0,
                step=100.0
            )

        # Career projections
        st.subheader("Career Projections")
        starting_salary = st.number_input(
            "Expected Starting Salary ($)",
            value=50000.0,
            step=1000.0
        )
        salary_growth = st.slider(
            "Annual Salary Growth (%)",
            min_value=0.0,
            max_value=15.0,
            value=3.0
        ) / 100.0

        # Investment return rate
        investment_return = st.slider(
            "Investment Return Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=7.0
        ) / 100.0

        if st.button("Calculate ROI"):
            # Calculate total costs
            total_cost = (tuition + living_expenses + books_supplies) * years
            
            # Create assets, income, and expenses for calculator
            milestone = MilestoneFactory.create_grad_school(1, total_cost, years)
            
            calculator = FinancialCalculator(
                assets=[],
                liabilities=[milestone.loan] if hasattr(milestone, 'loan') else [],
                income=[milestone.income] if hasattr(milestone, 'income') else [],
                expenses=milestone.expenses if hasattr(milestone, 'expenses') else []
            )

            # Calculate projections
            projection_years = 20
            projections = calculator.calculate_yearly_projection(projection_years)

            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Education Cost", f"${total_cost:,.2f}")
            with col2:
                st.metric("Starting Salary", f"${starting_salary:,.2f}")
            with col3:
                final_salary = starting_salary * (1 + salary_growth) ** projection_years
                st.metric("Projected Salary in 20 Years", f"${final_salary:,.2f}")

            # ROI Chart
            st.subheader("20-Year ROI Projection")
            FinancialPlotter.plot_roi_chart(
                years=projections['years'],
                cumulative_earnings=projections['total_income'],
                cumulative_costs=projections['total_expenses'],
                investment_value=projections['investment_growth']
            )

            # Detailed breakdown
            st.subheader("Year-by-Year Breakdown")
            df_projections = pd.DataFrame({
                'Year': projections['years'],
                'Annual Income': projections['total_income'],
                'Annual Expenses': projections['total_expenses'],
                'Net Worth': projections['net_worth']
            })
            
            st.dataframe(df_projections)
    else:
        st.warning("Please select an institution and field of study first.")
        st.markdown("Go back to the main page to make your selection.")

if __name__ == "__main__":
    main()
