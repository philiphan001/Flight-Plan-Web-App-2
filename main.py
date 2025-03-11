import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter

def main():
    st.set_page_config(page_title="Financial Projection App", layout="wide")
    st.title("Financial Projection Application")

    # Sidebar inputs
    st.sidebar.header("Input Parameters")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader("Upload financial data CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            df = DataProcessor.load_financial_data(uploaded_file)
            
            # Location selection
            locations = df['Location'].unique()
            selected_location = st.sidebar.selectbox("Select Location", locations)
            
            # Salary input
            salary = st.sidebar.number_input("Annual Salary", min_value=0, value=50000)
            
            # Housing choice
            is_homeowner = st.sidebar.checkbox("Are you a homeowner?")
            
            # Projection years
            projection_years = st.sidebar.slider("Projection Years", 1, 20, 10)

            # Process data
            location_data = DataProcessor.process_location_data(df, selected_location)
            assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                location_data, salary, is_homeowner
            )

            # Calculate projections
            calculator = FinancialCalculator(assets, liabilities, income, expenses)
            projections = calculator.calculate_yearly_projection(projection_years)

            # Display summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Initial Net Worth", 
                         f"${projections['net_worth'][0]:,.2f}")
            with col2:
                st.metric("Final Net Worth", 
                         f"${projections['net_worth'][-1]:,.2f}")
            with col3:
                st.metric("Average Annual Cash Flow", 
                         f"${sum(projections['cash_flow'])/len(projections['cash_flow']):,.2f}")

            # Display visualizations
            st.header("Financial Projections")
            
            FinancialPlotter.plot_net_worth(
                projections['years'], 
                projections['net_worth']
            )
            
            FinancialPlotter.plot_cash_flow(
                projections['years'],
                projections['total_income'],
                projections['total_expenses'],
                projections['cash_flow']
            )
            
            FinancialPlotter.plot_assets_liabilities(
                projections['years'],
                projections['asset_values'],
                projections['liability_values']
            )

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
    else:
        st.info("Please upload a CSV file to begin the financial projection analysis.")

if __name__ == "__main__":
    main()
