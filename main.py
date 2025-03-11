import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from difflib import get_close_matches
from models.financial_models import MilestoneFactory

def main():
    st.set_page_config(page_title="Financial Projection App", layout="wide")
    st.title("Financial Projection Application")

    # Sidebar inputs
    st.sidebar.header("Input Parameters")

    try:
        # Load data files directly from filesystem
        coli_df = DataProcessor.load_coli_data("COLI by Location.csv")
        occupation_df = DataProcessor.load_occupation_data("Occupational Data.csv")

        # Get available options and remove any NaN values
        locations = [loc for loc in coli_df['Cost of Living'].astype(str).unique().tolist() 
                    if loc.lower() != 'nan']
        occupations = [occ for occ in occupation_df['Occupation'].astype(str).unique().tolist() 
                      if occ.lower() != 'nan']

        # Initialize session state
        if 'selected_location' not in st.session_state:
            st.session_state.selected_location = None
        if 'selected_occupation' not in st.session_state:
            st.session_state.selected_occupation = None
        if 'milestones' not in st.session_state:
            st.session_state.milestones = []

        # Location input with suggestions
        location_input = st.sidebar.text_input("Enter Location", "")

        if location_input:
            # Find best matches using string similarity
            matches = get_close_matches(location_input.lower(), 
                                     [loc.lower() for loc in locations], 
                                     n=3, cutoff=0.1)

            # Get original case matches
            matching_locations = [
                loc for loc in locations 
                if loc.lower() in matches
            ]

            # Always show at least 2 options
            if len(matching_locations) == 1:
                # Add the next closest match
                other_matches = [
                    loc for loc in locations 
                    if loc not in matching_locations
                ][:1]
                matching_locations.extend(other_matches)

            if matching_locations:
                st.sidebar.markdown("### Select a location:")
                for loc in matching_locations:
                    # Use unique key for each button
                    is_selected = st.session_state.selected_location == loc

                    # Create a styled button
                    if st.sidebar.button(
                        loc,
                        key=f"loc_{loc}",
                        help=f"Select {loc} as your location",
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_location = loc
                        # Force rerun to update button states
                        st.rerun()
            else:
                st.sidebar.error(
                    "No matching locations found. Available locations: " +
                    ", ".join(locations[:3]))
                st.stop()

        # Occupation input with suggestions
        occupation_input = st.sidebar.text_input("Enter Occupation", "")

        if occupation_input:
            # Find best matches using string similarity
            matches = get_close_matches(occupation_input.lower(), 
                                     [occ.lower() for occ in occupations], 
                                     n=3, cutoff=0.1)

            # Get original case matches
            matching_occupations = [
                occ for occ in occupations 
                if occ.lower() in matches
            ]

            # Always show at least 2 options
            if len(matching_occupations) == 1:
                # Add the next closest match
                other_matches = [
                    occ for occ in occupations 
                    if occ not in matching_occupations
                ][:1]
                matching_occupations.extend(other_matches)

            if matching_occupations:
                st.sidebar.markdown("### Select an occupation:")
                for occ in matching_occupations:
                    # Use unique key for each button
                    is_selected = st.session_state.selected_occupation == occ

                    # Create a styled button
                    if st.sidebar.button(
                        occ,
                        key=f"occ_{occ}",
                        help=f"Select {occ} as your occupation",
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_occupation = occ
                        # Force rerun to update button states
                        st.rerun()
            else:
                st.sidebar.error(
                    "No matching occupations found. Available occupations: " +
                    ", ".join(occupations[:3]))
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
            projection_years = st.sidebar.slider("Projection Years", 1, 30, 10)

            # Life Milestones Section
            st.sidebar.markdown("---")
            st.sidebar.subheader("Life Milestones")

            # Add milestone button
            milestone_type = st.sidebar.selectbox(
                "Add a Life Milestone",
                ["Marriage", "New Child", "Home Purchase", "Car Purchase", "Graduate School"]
            )

            milestone_year = st.sidebar.slider(
                "Milestone Year",
                min_value=1,
                max_value=projection_years,
                value=2
            )

            # Additional inputs based on milestone type
            if milestone_type == "Marriage":
                wedding_cost = st.sidebar.number_input("Wedding Cost", value=30000)
                if st.sidebar.button("Add Marriage Milestone"):
                    milestone = MilestoneFactory.create_marriage(milestone_year, wedding_cost)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            elif milestone_type == "New Child":
                if st.sidebar.button("Add Child Milestone"):
                    milestone = MilestoneFactory.create_child(milestone_year)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            elif milestone_type == "Home Purchase":
                home_price = st.sidebar.number_input("Home Price", value=300000)
                down_payment_pct = st.sidebar.slider("Down Payment %", 5, 40, 20) / 100
                if st.sidebar.button("Add Home Purchase Milestone"):
                    milestone = MilestoneFactory.create_home_purchase(
                        milestone_year, home_price, down_payment_pct)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            elif milestone_type == "Car Purchase":
                car_price = st.sidebar.number_input("Car Price", value=30000)
                down_payment_pct = st.sidebar.slider("Down Payment %", 5, 100, 20) / 100
                if st.sidebar.button("Add Car Purchase Milestone"):
                    milestone = MilestoneFactory.create_car_purchase(
                        milestone_year, car_price, down_payment_pct)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            elif milestone_type == "Graduate School":
                total_cost = st.sidebar.number_input("Total Cost", value=100000)
                program_years = st.sidebar.slider("Program Length (Years)", 1, 4, 2)
                if st.sidebar.button("Add Graduate School Milestone"):
                    milestone = MilestoneFactory.create_grad_school(
                        milestone_year, total_cost, program_years)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            # Display current milestones
            if st.session_state.milestones:
                st.sidebar.markdown("### Current Milestones")
                for idx, milestone in enumerate(st.session_state.milestones):
                    st.sidebar.markdown(f"- {milestone.name} (Year {milestone.trigger_year})")
                    if st.sidebar.button(f"Remove {milestone.name}", key=f"remove_{idx}"):
                        st.session_state.milestones.pop(idx)
                        st.rerun()

            # Process data
            location_data = DataProcessor.process_location_data(
                coli_df, occupation_df, 
                st.session_state.selected_location, 
                st.session_state.selected_occupation,
                investment_return_rate
            )

            # Create financial objects with milestones
            assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                location_data,
                is_homeowner,
                st.session_state.milestones
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