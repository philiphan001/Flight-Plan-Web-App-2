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

    try:
        # Load data files directly from filesystem
        coli_df = DataProcessor.load_coli_data("COLI by Location.csv")
        occupation_df = DataProcessor.load_occupation_data(
            "Occupational Data.csv")

        # Get available options
        locations = coli_df['Cost of Living'].astype(str).unique().tolist()
        occupations = occupation_df['Occupation'].astype(str).unique().tolist()

        # Location input with suggestions
        location_input = st.sidebar.text_input("Enter Location", "")
        matching_locations = [
            loc for loc in locations
            if location_input.lower() in str(loc).lower()
        ]
        if location_input:
            if len(matching_locations) > 0:
                selected_location = st.sidebar.radio(
                    "Select from matching locations:", matching_locations)
            else:
                st.sidebar.error(
                    "No matching locations found. Available locations: " +
                    ", ".join(locations))
                st.stop()

        # Occupation input with suggestions
        occupation_input = st.sidebar.text_input("Enter Occupation", "")
        matching_occupations = [
            occ for occ in occupations
            if occupation_input.lower() in str(occ).lower()
        ]
        if occupation_input:
            if len(matching_occupations) > 0:
                selected_occupation = st.sidebar.radio(
                    "Select from matching occupations:", matching_occupations)
            else:
                st.sidebar.error(
                    "No matching occupations found. Available occupations: " +
                    ", ".join(occupations))
                st.stop()

        # Only proceed if both inputs are valid
        if location_input and occupation_input and len(
                matching_locations) > 0 and len(matching_occupations) > 0:
            # Housing choice
            is_homeowner = st.sidebar.checkbox("Are you a homeowner?")

            # Projection years
            projection_years = st.sidebar.slider("Projection Years", 1, 20, 10)

            # Process data
            location_data = DataProcessor.process_location_data(
                coli_df, occupation_df, selected_location, selected_occupation)

            assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                location_data, is_homeowner)

            # Calculate projections
            calculator = FinancialCalculator(assets, liabilities, income,
                                             expenses)
            projections = calculator.calculate_yearly_projection(
                projection_years)

            # Display summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Initial Net Worth",
                          f"${projections['net_worth'][0]:,.2f}")
            with col2:
                st.metric("Final Net Worth",
                          f"${projections['net_worth'][-1]:,.2f}")
            with col3:
                st.metric(
                    "Average Annual Cash Flow",
                    f"${sum(projections['cash_flow'])/len(projections['cash_flow']):,.2f}"
                )

            # Display visualizations
            st.header("Financial Projections")

            FinancialPlotter.plot_net_worth(projections['years'],
                                            projections['net_worth'])

            FinancialPlotter.plot_cash_flow(projections['years'],
                                            projections['total_income'],
                                            projections['total_expenses'],
                                            projections['cash_flow'])

            FinancialPlotter.plot_assets_liabilities(
                projections['years'], projections['asset_values'],
                projections['liability_values'])

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")


if __name__ == "__main__":
    main()
