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

    # File uploads
    coli_file = st.sidebar.file_uploader("Upload Cost of Living Index CSV", type="csv", key="coli_upload")
    occupation_file = st.sidebar.file_uploader("Upload Occupational Data CSV", type="csv", key="occupation_upload")

    if coli_file is not None and occupation_file is not None:
        try:
            # Load both data files
            coli_df = DataProcessor.load_coli_data(coli_file)
            occupation_df = DataProcessor.load_occupation_data(occupation_file)

            # Location and occupation selection
            locations = coli_df['Cost of Living'].unique()
            occupations = occupation_df['Occupation'].unique()

            selected_location = st.sidebar.selectbox("Select Location", locations)
            selected_occupation = st.sidebar.selectbox("Select Occupation", occupations)


            # Housing choice
            is_homeowner = st.sidebar.checkbox("Are you a homeowner?")

            # Projection years
            projection_years = st.sidebar.slider("Projection Years", 1, 20, 10)

            # Process data
            location_data = DataProcessor.process_location_data(
                coli_df, occupation_df, selected_location, selected_occupation
            )

            assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                location_data, is_homeowner
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
        st.info("Please upload both CSV files to begin the financial projection analysis.")

if __name__ == "__main__":
    main()