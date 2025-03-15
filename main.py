import streamlit as st
import pandas as pd
from difflib import get_close_matches
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from models.financial_models import MilestoneFactory, SpouseIncome as ModelSpouseIncome

def main():
    st.set_page_config(page_title="Financial Projection App", layout="wide")

    st.title("Financial Projection Application")

    try:
        # Load data files
        coli_df = DataProcessor.load_coli_data("COLI by Location.csv")
        occupation_df = DataProcessor.load_occupation_data("Occupational Data.csv")

        # Get available options and remove any NaN values
        locations = sorted([loc for loc in coli_df['Cost of Living'].astype(str).unique().tolist() 
                   if loc.lower() != 'nan'])
        occupations = sorted([occ for occ in occupation_df['Occupation'].astype(str).unique().tolist() 
                     if occ.lower() != 'nan'])

        # Create two columns for location and occupation selection
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Select Your Location 📍")
            location_input = st.text_input("Enter Location", "")

            if location_input:
                matches = get_close_matches(location_input.lower(), 
                                        [loc.lower() for loc in locations], 
                                        n=3, cutoff=0.1)
                matching_locations = [loc for loc in locations if loc.lower() in matches]

                if matching_locations:
                    st.markdown("#### Select from matches:")
                    selected_location = None
                    for loc in matching_locations:
                        if st.button(f"📍 {loc}", key=f"loc_{loc}"):
                            selected_location = loc
                else:
                    st.error("No matching locations found")

        with col2:
            st.markdown("### Select Your Occupation 💼")
            occupation_input = st.text_input("Enter Occupation", "")

            if occupation_input:
                matches = get_close_matches(occupation_input.lower(), 
                                        [occ.lower() for occ in occupations], 
                                        n=3, cutoff=0.1)
                matching_occupations = [occ for occ in occupations if occ.lower() in matches]

                if matching_occupations:
                    st.markdown("#### Select from matches:")
                    selected_occupation = None
                    for occ in matching_occupations:
                        if st.button(f"💼 {occ}", key=f"occ_{occ}"):
                            selected_occupation = occ
                else:
                    st.error("No matching occupations found")

        # Only proceed if both selections are made
        if 'selected_location' in locals() and 'selected_occupation' in locals() and selected_location and selected_occupation:
            st.markdown("---")

            # Investment and projection settings
            col3, col4 = st.columns(2)
            with col3:
                investment_return_rate = st.slider(
                    "Investment Return Rate (%)", 
                    min_value=0.0, 
                    max_value=15.0, 
                    value=7.0, 
                    step=0.5
                ) / 100.0

            with col4:
                projection_years = st.slider("Projection Years", 1, 30, 10)

            # Process data
            location_data = DataProcessor.process_location_data(
                coli_df, occupation_df, 
                selected_location, 
                selected_occupation,
                investment_return_rate
            )

            # Create financial objects
            assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                location_data
            )

            # Calculate projections
            calculator = FinancialCalculator(assets, liabilities, income, expenses)
            projections = calculator.calculate_yearly_projection(projection_years)

            # Display summary metrics
            st.markdown("### Financial Summary")
            col5, col6, col7 = st.columns(3)
            with col5:
                st.metric("Initial Net Worth 💰",
                       f"${projections['net_worth'][0]:,.2f}")
            with col6:
                st.metric("Final Net Worth 🚀",
                       f"${projections['net_worth'][-1]:,.2f}")
            with col7:
                st.metric(
                    "Average Annual Cash Flow 💵",
                    f"${sum(projections['cash_flow'])/len(projections['cash_flow']):,.2f}"
                )

            # Create tabs for different visualizations
            tab1, tab2, tab3 = st.tabs([
                "Net Worth Projection 📈",
                "Cash Flow Analysis 💰",
                "Assets & Liabilities ⚖️"
            ])

            with tab1:
                st.markdown("### Net Worth Over Time")
                FinancialPlotter.plot_net_worth(
                    projections['years'],
                    projections['net_worth'],
                    projections['asset_values'],
                    projections['liability_values']
                )

            with tab2:
                st.markdown("### Cash Flow Analysis")
                FinancialPlotter.plot_cash_flow(
                    projections['years'],
                    projections['total_income'],
                    projections['expense_categories'],
                    projections['total_expenses'],
                    projections['cash_flow']
                )

            with tab3:
                st.markdown("### Assets and Liabilities")
                FinancialPlotter.plot_assets_liabilities(
                    projections['years'],
                    projections['asset_values'],
                    projections['liability_values']
                )

            # Life Milestones Section
            st.markdown("---")
            st.markdown("## Life Milestones 🎯")
            st.markdown("Add life events to see their impact on your financial future:")

            # Create milestone buttons in columns
            milestone_col1, milestone_col2, milestone_col3 = st.columns(3)

            with milestone_col1:
                if st.button("💑 Add Marriage"):
                    st.session_state.adding_milestone = "Marriage"
                if st.button("👶 Add Child"):
                    st.session_state.adding_milestone = "Child"

            with milestone_col2:
                if st.button("🏠 Buy Home"):
                    st.session_state.adding_milestone = "Home"
                if st.button("🚗 Buy Car"):
                    st.session_state.adding_milestone = "Car"

            with milestone_col3:
                if st.button("🎓 Graduate School"):
                    st.session_state.adding_milestone = "Grad School"

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Debug info:", e)

if __name__ == "__main__":
    main()