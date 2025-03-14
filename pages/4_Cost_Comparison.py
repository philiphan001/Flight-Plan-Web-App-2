import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from services.calculator import FinancialCalculator

st.set_page_config(page_title="Cost Comparison Tool", page_icon="💰")

def calculate_total_cost(tuition, living_expenses, books_supplies, years, aid_amount=0):
    annual_cost = tuition + living_expenses + books_supplies
    total_cost = annual_cost * years
    return total_cost - (aid_amount * years)

def main():
    st.title("Education Cost Comparison Tool 💰")
    st.markdown("""
    Compare the total cost of different educational paths and institutions.
    Factor in tuition, living expenses, financial aid, and more to make informed decisions.
    """)

    # Add institutions to compare
    st.subheader("Add Institutions to Compare")
    
    if 'institutions' not in st.session_state:
        st.session_state.institutions = []

    col1, col2 = st.columns([3, 1])
    
    with col1:
        institution_name = st.text_input("Institution Name")
        
    with col2:
        if st.button("Add Institution"):
            if institution_name:
                st.session_state.institutions.append(institution_name)

    # Create comparison entries
    if st.session_state.institutions:
        comparisons = []
        
        for institution in st.session_state.institutions:
            st.markdown(f"### {institution}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                tuition = st.number_input(
                    f"Annual Tuition for {institution} ($)",
                    value=30000.0,
                    step=1000.0,
                    key=f"tuition_{institution}"
                )
                
                living_expenses = st.number_input(
                    "Annual Living Expenses ($)",
                    value=15000.0,
                    step=1000.0,
                    key=f"living_{institution}"
                )
                
            with col2:
                books_supplies = st.number_input(
                    "Annual Books & Supplies ($)",
                    value=1200.0,
                    step=100.0,
                    key=f"books_{institution}"
                )
                
                years = st.number_input(
                    "Program Length (years)",
                    min_value=1,
                    max_value=6,
                    value=4,
                    key=f"years_{institution}"
                )
                
            aid_amount = st.number_input(
                "Annual Financial Aid/Scholarships ($)",
                value=0.0,
                step=1000.0,
                key=f"aid_{institution}"
            )
            
            total_cost = calculate_total_cost(
                tuition, living_expenses, books_supplies, years, aid_amount
            )
            
            comparisons.append({
                'Institution': institution,
                'Annual Tuition': tuition,
                'Living Expenses': living_expenses,
                'Books & Supplies': books_supplies,
                'Program Length': years,
                'Financial Aid': aid_amount,
                'Total Cost': total_cost
            })
            
            st.markdown("---")

        if len(comparisons) > 0:
            st.subheader("Cost Comparison Results")
            
            # Create comparison table
            df_comparison = pd.DataFrame(comparisons)
            
            # Format currency columns
            currency_cols = ['Annual Tuition', 'Living Expenses', 'Books & Supplies', 
                           'Financial Aid', 'Total Cost']
            for col in currency_cols:
                df_comparison[col] = df_comparison[col].apply(lambda x: f"${x:,.2f}")
                
            st.dataframe(df_comparison)
            
            # Create bar chart comparison
            costs_data = [float(c['Total Cost'].replace('$', '').replace(',', '')) 
                         for c in comparisons]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=[c['Institution'] for c in comparisons],
                    y=costs_data,
                    text=[f"${cost:,.0f}" for cost in costs_data],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title="Total Cost Comparison",
                xaxis_title="Institution",
                yaxis_title="Total Cost ($)",
                showlegend=False
            )
            
            st.plotly_chart(fig)
            
            # Add option to remove institutions
            st.subheader("Remove Institutions")
            institution_to_remove = st.selectbox(
                "Select institution to remove",
                st.session_state.institutions
            )
            
            if st.button("Remove Selected Institution"):
                st.session_state.institutions.remove(institution_to_remove)
                st.rerun()

if __name__ == "__main__":
    main()
