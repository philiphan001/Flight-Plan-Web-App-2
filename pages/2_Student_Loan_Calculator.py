import streamlit as st
import pandas as pd
from services.calculator import FinancialCalculator
import plotly.graph_objects as go

st.set_page_config(page_title="Student Loan Calculator", page_icon="💳")

def calculate_loan_payment(principal, interest_rate, years):
    r = interest_rate / 12 / 100  # Monthly interest rate
    n = years * 12  # Total number of payments
    if r == 0:
        return principal / n
    payment = principal * (r * (1 + r)**n) / ((1 + r)**n - 1)
    return payment

def main():
    st.title("Student Loan Calculator 💳")
    st.markdown("""
    Plan your student loan repayment and understand the total cost of your education.
    Calculate monthly payments, total interest, and explore different repayment scenarios.
    """)

    # Loan inputs
    col1, col2 = st.columns(2)
    
    with col1:
        loan_amount = st.number_input(
            "Total Loan Amount ($)",
            min_value=1000,
            max_value=500000,
            value=50000,
            step=1000
        )
        
        loan_term = st.number_input(
            "Loan Term (years)",
            min_value=5,
            max_value=30,
            value=10,
            step=1
        )

    with col2:
        interest_rate = st.number_input(
            "Interest Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=5.0,
            step=0.1
        )
        
        additional_payment = st.number_input(
            "Additional Monthly Payment ($)",
            min_value=0,
            max_value=10000,
            value=0,
            step=50
        )

    if st.button("Calculate Loan"):
        # Calculate standard monthly payment
        monthly_payment = calculate_loan_payment(loan_amount, interest_rate, loan_term)
        total_payment = monthly_payment * loan_term * 12
        total_interest = total_payment - loan_amount

        # Calculate with additional payments
        if additional_payment > 0:
            total_monthly = monthly_payment + additional_payment
            remaining_balance = loan_amount
            months = 0
            total_interest_with_extra = 0

            while remaining_balance > 0 and months < loan_term * 12:
                months += 1
                interest = remaining_balance * (interest_rate / 12 / 100)
                total_interest_with_extra += interest
                principal = total_monthly - interest
                remaining_balance -= principal

                if remaining_balance < 0:
                    remaining_balance = 0

            new_term_years = months / 12
            total_payment_with_extra = months * total_monthly
            savings = total_payment - total_payment_with_extra

        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monthly Payment", f"${monthly_payment:,.2f}")
        with col2:
            st.metric("Total Interest", f"${total_interest:,.2f}")
        with col3:
            st.metric("Total Payment", f"${total_payment:,.2f}")

        if additional_payment > 0:
            st.subheader("With Additional Payments")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("New Loan Term", f"{new_term_years:.1f} years")
            with col2:
                st.metric("Total Interest", f"${total_interest_with_extra:,.2f}")
            with col3:
                st.metric("Total Savings", f"${savings:,.2f}")

        # Create amortization schedule
        schedule = []
        balance = loan_amount
        month = 1
        
        while balance > 0 and month <= loan_term * 12:
            interest_payment = balance * (interest_rate / 12 / 100)
            principal_payment = monthly_payment - interest_payment
            
            if additional_payment > 0:
                principal_payment += additional_payment
            
            balance -= principal_payment
            
            if balance < 0:
                principal_payment += balance
                balance = 0
                
            schedule.append({
                'Month': month,
                'Payment': monthly_payment + (additional_payment if additional_payment > 0 else 0),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Remaining Balance': balance
            })
            month += 1
            
            if balance <= 0:
                break

        # Display amortization schedule
        st.subheader("Loan Amortization Schedule")
        df_schedule = pd.DataFrame(schedule)
        
        # Format currency columns
        currency_cols = ['Payment', 'Principal', 'Interest', 'Remaining Balance']
        for col in currency_cols:
            df_schedule[col] = df_schedule[col].apply(lambda x: f"${x:,.2f}")

        st.dataframe(df_schedule)

if __name__ == "__main__":
    main()
