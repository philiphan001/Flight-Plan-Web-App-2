import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from typing import Dict, List

def main():
    st.set_page_config(page_title="Financial Projection App", layout="wide")
    st.title("Financial Projection Application")

    # Debug logging
    st.write("Starting application...")

    try:
        # Initialize session state
        if 'selected_location' not in st.session_state:
            st.session_state.selected_location = ""
        if 'selected_occupation' not in st.session_state:
            st.session_state.selected_occupation = ""

        # Investment return rate slider (moved to top for early testing)
        investment_return_rate = st.sidebar.slider(
            "Investment Return Rate (%)", 
            min_value=0.0, 
            max_value=15.0, 
            value=7.0, 
            step=0.5,
            help="Annual rate of return for invested savings"
        ) / 100.0

        # Load and process CSV files
        try:
            coli_df = pd.read_csv("COLI by Location.csv")
            st.write("COLI CSV loaded successfully")
            locations = coli_df['Cost of Living'].astype(str).unique().tolist()
            st.write(f"Found {len(locations)} locations")

            occupation_df = pd.read_csv("Occupational Data.csv")
            st.write("Occupation CSV loaded successfully")
            occupations = occupation_df['Occupation'].astype(str).unique().tolist()
            st.write(f"Found {len(occupations)} occupations")

        except FileNotFoundError as e:
            st.error("Required CSV files not found. Please ensure both 'COLI by Location.csv' and 'Occupational Data.csv' exist.")
            return
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return

        # Location input
        location_input = st.sidebar.text_input("Enter Location", "")
        if location_input:
            matching_locations = [loc for loc in locations if location_input.lower() in loc.lower()]
            if matching_locations:
                st.sidebar.markdown("### Select a location:")
                display_locations = matching_locations[:max(2, len(matching_locations))]
                cols = st.sidebar.columns(len(display_locations))
                for idx, loc in enumerate(display_locations):
                    if cols[idx].button(
                        loc, 
                        key=f"loc_button_{idx}",
                        type="primary" if st.session_state.selected_location == loc else "secondary"
                    ):
                        st.session_state.selected_location = loc
                        st.write(f"Selected location: {loc}")
            else:
                st.sidebar.error(f"No matching locations found. Try: {', '.join(locations[:3])}")

        # Occupation input
        occupation_input = st.sidebar.text_input("Enter Occupation", "")
        if occupation_input:
            matching_occupations = [occ for occ in occupations if occupation_input.lower() in occ.lower()]
            if matching_occupations:
                st.sidebar.markdown("### Select an occupation:")
                display_occupations = matching_occupations[:max(2, len(matching_occupations))]
                cols = st.sidebar.columns(len(display_occupations))
                for idx, occ in enumerate(display_occupations):
                    if cols[idx].button(
                        occ, 
                        key=f"occ_button_{idx}",
                        type="primary" if st.session_state.selected_occupation == occ else "secondary"
                    ):
                        st.session_state.selected_occupation = occ
                        st.write(f"Selected occupation: {occ}")
            else:
                st.sidebar.error(f"No matching occupations found. Try: {', '.join(occupations[:3])}")

        # Only proceed if both selections are valid
        if st.session_state.selected_location and st.session_state.selected_occupation:
            st.write("Processing selections...")

            # Housing choice
            is_homeowner = st.sidebar.checkbox("Are you a homeowner?")

            # Projection years
            projection_years = st.sidebar.slider("Projection Years", 1, 20, 10)

            try:
                # Process data with debug logging
                st.write("Processing location and occupation data...")
                location_data = DataProcessor.process_location_data(
                    coli_df, occupation_df, 
                    st.session_state.selected_location, 
                    st.session_state.selected_occupation,
                    investment_return_rate
                )

                st.write("Creating financial objects...")
                assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                    location_data, is_homeowner
                )

                st.write("Calculating projections...")
                calculator = FinancialCalculator(assets, liabilities, income, expenses)
                projections = calculator.calculate_yearly_projection(projection_years)

                # Display results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Initial Net Worth", f"${projections['net_worth'][0]:,.2f}")
                with col2:
                    st.metric("Final Net Worth", f"${projections['net_worth'][-1]:,.2f}")
                with col3:
                    avg_cash_flow = sum(projections['cash_flow'])/len(projections['cash_flow'])
                    st.metric("Average Annual Cash Flow", f"${avg_cash_flow:,.2f}")

                st.write("Generating visualizations...")
                # Net Worth Section
                st.subheader("Net Worth Projection")
                FinancialPlotter.plot_net_worth(projections['years'], projections['net_worth'])
                st.dataframe(pd.DataFrame({
                    'Year': projections['years'],
                    'Net Worth': [f"${x:,.2f}" for x in projections['net_worth']]
                }))

                # Cash Flow Section
                st.subheader("Income, Expenses, and Net Savings")
                FinancialPlotter.plot_cash_flow(
                    projections['years'],
                    projections['total_income'],
                    projections['total_expenses'],
                    projections['cash_flow']
                )
                st.dataframe(pd.DataFrame({
                    'Year': projections['years'],
                    'Total Income': [f"${x:,.2f}" for x in projections['total_income']],
                    'Total Expenses': [f"${x:,.2f}" for x in projections['total_expenses']],
                    'Net Savings': [f"${x:,.2f}" for x in projections['cash_flow']],
                    'Investment Growth': [f"${x:,.2f}" for x in projections['investment_growth']]
                }))

                # Assets and Liabilities
                st.subheader("Assets and Liabilities")
                FinancialPlotter.plot_assets_liabilities(
                    projections['years'],
                    projections['asset_values'],
                    projections['liability_values']
                )
                st.dataframe(pd.DataFrame({
                    'Year': projections['years'],
                    'Assets': [f"${x:,.2f}" for x in projections['asset_values']],
                    'Liabilities': [f"${x:,.2f}" for x in projections['liability_values']],
                    'Net Worth': [f"${x:,.2f}" for x in projections['net_worth']]
                }))

            except Exception as e:
                st.error(f"Error in calculations: {str(e)}")
                st.error(f"Error type: {type(e).__name__}")

    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main()