import streamlit as st
import plotly.graph_objects as go
from services.calculator import FinancialCalculator

def show_tax_breakdown(projections: dict):
    """Display detailed tax breakdown visualization"""
    st.subheader("Tax Breakdown Analysis 📊")
    
    # Create tax breakdown chart
    fig = go.Figure()
    
    years = projections['years']
    federal_tax = projections['tax_breakdown']['federal_income_tax']
    state_tax = projections['tax_breakdown']['state_income_tax']
    payroll_tax = projections['tax_breakdown']['payroll_tax']
    
    # Add traces for each tax type
    fig.add_trace(go.Bar(
        name="Federal Income Tax",
        x=years,
        y=federal_tax,
        marker_color='rgb(55, 83, 109)'
    ))
    fig.add_trace(go.Bar(
        name="State Income Tax",
        x=years,
        y=state_tax,
        marker_color='rgb(26, 118, 255)'
    ))
    fig.add_trace(go.Bar(
        name="Payroll Tax",
        x=years,
        y=payroll_tax,
        marker_color='rgb(15, 133, 84)'
    ))
    
    # Update layout for stacked bars
    fig.update_layout(
        barmode='stack',
        title="Annual Tax Breakdown",
        xaxis_title="Year",
        yaxis_title="Tax Amount ($)",
        legend_title="Tax Type",
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display tax summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Federal Tax", f"${sum(federal_tax):,.2f}")
    with col2:
        st.metric("Total State Tax", f"${sum(state_tax):,.2f}")
    with col3:
        st.metric("Total Payroll Tax", f"${sum(payroll_tax):,.2f}")
    
    # Show tax details table
    st.subheader("Yearly Tax Details")
    tax_data = {
        'Year': years,
        'Federal Tax': [f"${x:,.2f}" for x in federal_tax],
        'State Tax': [f"${x:,.2f}" for x in state_tax],
        'Payroll Tax': [f"${x:,.2f}" for x in payroll_tax],
        'Total Tax': [f"${(x+y+z):,.2f}" for x,y,z in zip(federal_tax, state_tax, payroll_tax)]
    }
    
    st.dataframe(tax_data)
