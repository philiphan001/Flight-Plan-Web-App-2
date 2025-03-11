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
        occupation_df = DataProcessor.load_occupation_data("Occupational Data.csv")

        # Get available options
        locations = coli_df['Cost of Living'].astype(str).unique().tolist()
        occupations = occupation_df['Occupation'].astype(str).unique().tolist()

        # Location input with suggestions
        location_input = st.sidebar.text_input("Enter Location", "")

        # Session state for selection
        if 'selected_location' not in st.session_state:
            st.session_state.selected_location = None
        if 'selected_occupation' not in st.session_state:
            st.session_state.selected_occupation = None

        if location_input:
            matching_locations = [
                loc for loc in locations
                if location_input.lower() in str(loc).lower()
            ]
            if len(matching_locations) > 0:
                st.sidebar.markdown("### Select a location:")
                # Show at least 2 options if available
                display_locations = matching_locations[:max(2, len(matching_locations))]
                cols = st.sidebar.columns(len(display_locations))
                for idx, loc in enumerate(display_locations):
                    # Create a unique key for each button
                    button_key = f"loc_button_{idx}"
                    # Check if this location is selected
                    is_selected = st.session_state.selected_location == loc
                    # Style based on selection state
                    button_style = """
                        background-color: #0066cc;
                        color: white;
                        """ if is_selected else ""

                    if cols[idx].button(
                        loc, key=button_key,
                        help=f"Select {loc} as your location"):
                        st.session_state.selected_location = loc

            else:
                st.sidebar.error(
                    "No matching locations found. Available locations: " +
                    ", ".join(locations[:3])
                )
                st.stop()

        # Occupation input with suggestions
        occupation_input = st.sidebar.text_input("Enter Occupation", "")
        if occupation_input:
            matching_occupations = [
                occ for occ in occupations
                if occupation_input.lower() in str(occ).lower()
            ]
            if len(matching_occupations) > 0:
                st.sidebar.markdown("### Select an occupation:")
                # Show at least 2 options if available
                display_occupations = matching_occupations[:max(2, len(matching_occupations))]
                cols = st.sidebar.columns(len(display_occupations))
                for idx, occ in enumerate(display_occupations):
                    # Create a unique key for each button
                    button_key = f"occ_button_{idx}"
                    # Check if this occupation is selected
                    is_selected = st.session_state.selected_occupation == occ
                    # Style based on selection state
                    button_style = """
                        background-color: #28a745;
                        color: white;
                        """ if is_selected else ""

                    if cols[idx].button(
                        occ, key=button_key,
                        help=f"Select {occ} as your occupation"):
                        st.session_state.selected_occupation = occ

            else:
                st.sidebar.error(
                    "No matching occupations found. Available occupations: " +
                    ", ".join(occupations[:3])
                )
                st.stop()

        # Only proceed if both selections are valid
        if st.session_state.selected_location and st.session_state.selected_occupation:
            # Investment return rate slider
            investment_return_rate = st.sidebar.slider(
                "Investment Return Rate (%)", 
                min_value=0.0, 
                max_value=15.0, 
                value=7.0, 
                step=0.5,
                help="Annual rate of return for invested savings"
            ) / 100.0

            # Housing choice
            is_homeowner = st.sidebar.checkbox("Are you a homeowner?")

            # Projection years
            projection_years = st.sidebar.slider("Projection Years", 1, 20, 10)

            # Process data
            location_data = DataProcessor.process_location_data(
                coli_df, occupation_df, 
                st.session_state.selected_location, 
                st.session_state.selected_occupation,
                investment_return_rate
            )

            assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                location_data, is_homeowner
            )

            # Calculate projections
            calculator = FinancialCalculator(assets, liabilities, income, expenses, 
                                           st.session_state.milestones if 'milestones' in st.session_state else [])
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
                st.metric(
                    "Average Annual Cash Flow",
                    f"${sum(projections['cash_flow'])/len(projections['cash_flow']):,.2f}"
                )

            # Display visualizations and data tables
            st.header("Financial Projections")

            # Net Worth Section
            st.subheader("Net Worth Projection")
            FinancialPlotter.plot_net_worth(projections['years'],
                                          projections['net_worth'])
            net_worth_df = pd.DataFrame({
                'Year': projections['years'],
                'Net Worth': [f"${x:,.2f}" for x in projections['net_worth']]
            })
            st.dataframe(net_worth_df)

            # Cash Flow Section
            st.subheader("Income, Expenses, and Cash Flow")
            FinancialPlotter.plot_cash_flow(projections['years'],
                                          projections['total_income'],
                                          projections['total_expenses'],
                                          projections['cash_flow'])
            cash_flow_df = pd.DataFrame({
                'Year': projections['years'],
                'Total Income': [f"${x:,.2f}" for x in projections['total_income']],
                'Total Expenses': [f"${x:,.2f}" for x in projections['total_expenses']],
                'Net Savings': [f"${x:,.2f}" for x in projections['cash_flow']],
                'Cumulative Investment Growth': [f"${x:,.2f}" for x in projections['investment_growth']]
            })
            st.dataframe(cash_flow_df)

            # Assets and Liabilities Section
            st.subheader("Assets and Liabilities")
            FinancialPlotter.plot_assets_liabilities(
                projections['years'], projections['asset_values'],
                projections['liability_values'])
            assets_liab_df = pd.DataFrame({
                'Year': projections['years'],
                'Assets': [f"${x:,.2f}" for x in projections['asset_values']],
                'Liabilities': [f"${x:,.2f}" for x in projections['liability_values']],
                'Net Worth': [f"${x:,.2f}" for x in projections['net_worth']]
            })
            st.dataframe(assets_liab_df)

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()