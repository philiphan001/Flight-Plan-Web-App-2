import streamlit as st
import pandas as pd
from difflib import get_close_matches
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from models.financial_models import MilestoneFactory, SpouseIncome as ModelSpouseIncome

def main():
    st.set_page_config(page_title="Financial Projection App", layout="wide")

    # Initialize session state variables if they don't exist
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    if 'selected_occupation' not in st.session_state:
        st.session_state.selected_occupation = None
    if 'show_projections' not in st.session_state:
        st.session_state.show_projections = False
    if 'milestones' not in st.session_state:
        st.session_state.milestones = []
    if 'previous_projections' not in st.session_state:
        st.session_state.previous_projections = None

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

        if not st.session_state.show_projections:
            # Create two columns for location and occupation selection
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Select Your Location 📍")
                if st.session_state.selected_location:
                    st.markdown(f"**Selected Location:** {st.session_state.selected_location}")
                else:
                    location_input = st.text_input("Enter Location", key="location_input")
                    if location_input:
                        matches = get_close_matches(location_input.lower(), 
                                                [loc.lower() for loc in locations], 
                                                n=3, cutoff=0.1)
                        matching_locations = [loc for loc in locations if loc.lower() in matches]
                        if matching_locations:
                            st.markdown("#### Select from matches:")
                            for loc in matching_locations:
                                if st.button(f"📍 {loc}", key=f"loc_{loc}"):
                                    st.session_state.selected_location = loc
                                    st.rerun()
                        else:
                            st.error("No matching locations found")

            with col2:
                st.markdown("### Select Your Occupation 💼")
                if st.session_state.selected_occupation:
                    st.markdown(f"**Selected Occupation:** {st.session_state.selected_occupation}")
                else:
                    occupation_input = st.text_input("Enter Occupation", key="occupation_input")
                    if occupation_input:
                        matches = get_close_matches(occupation_input.lower(), 
                                                [occ.lower() for occ in occupations], 
                                                n=3, cutoff=0.1)
                        matching_occupations = [occ for occ in occupations if occ.lower() in matches]
                        if matching_occupations:
                            st.markdown("#### Select from matches:")
                            for occ in matching_occupations:
                                if st.button(f"💼 {occ}", key=f"occ_{occ}"):
                                    st.session_state.selected_occupation = occ
                                    st.rerun()
                        else:
                            st.error("No matching occupations found")

            # Show continue button only if both selections are made
            if st.session_state.selected_location and st.session_state.selected_occupation:
                st.markdown("---")
                if st.button("Continue to Financial Projections ➡️"):
                    st.session_state.show_projections = True
                    st.rerun()

        else:
            # Show back button
            if st.button("← Back to Selection"):
                st.session_state.show_projections = False
                st.rerun()

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
                st.session_state.selected_location, 
                st.session_state.selected_occupation,
                investment_return_rate
            )

            # Life Milestones Section in Sidebar
            st.sidebar.markdown("## Life Milestones 🎯")
            st.sidebar.markdown("Add life events to see their impact:")

            # Marriage Milestone
            with st.sidebar.expander("💑 Marriage"):
                milestone_year = st.slider("Marriage Year", 1, projection_years, 2, key="marriage_year")
                wedding_cost = st.number_input("Wedding Cost ($)", 10000, 100000, 30000, step=5000, key="wedding_cost")

                # Spouse occupation input
                spouse_occupation_input = st.text_input("Enter Spouse's Occupation", key="spouse_occ")
                if spouse_occupation_input:
                    matches = get_close_matches(spouse_occupation_input.lower(), 
                                            [occ.lower() for occ in occupations], 
                                            n=3, cutoff=0.1)
                    matching_occupations = [occ for occ in occupations if occ.lower() in matches]
                    if matching_occupations:
                        selected_spouse_occ = st.radio("Select Spouse's Occupation:", matching_occupations)
                        if st.button("Add Marriage Milestone"):
                            # Process spouse's income data
                            spouse_data = DataProcessor.process_location_data(
                                coli_df, occupation_df,
                                st.session_state.selected_location,
                                selected_spouse_occ,
                                investment_return_rate
                            )
                            spouse_income = ModelSpouseIncome(
                                spouse_data['base_income'],
                                spouse_data['location_adjustment']
                            )
                            milestone = MilestoneFactory.create_marriage(
                                milestone_year, wedding_cost, spouse_income)
                            st.session_state.milestones.append(milestone)
                            st.rerun()

            # Child Milestone
            with st.sidebar.expander("👶 New Child"):
                child_year = st.slider("Child Year", 1, projection_years, 3, key="child_year")
                if st.button("Add Child Milestone"):
                    milestone = MilestoneFactory.create_child(child_year)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            # Home Purchase Milestone
            with st.sidebar.expander("🏠 Home Purchase"):
                home_year = st.slider("Purchase Year", 1, projection_years, 5, key="home_year")
                home_price = st.number_input("Home Price ($)", 100000, 2000000, 300000, step=50000)
                down_payment_pct = st.slider("Down Payment %", 5, 40, 20) / 100
                if st.button("Add Home Purchase Milestone"):
                    milestone = MilestoneFactory.create_home_purchase(
                        home_year, home_price, down_payment_pct)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            # Car Purchase Milestone
            with st.sidebar.expander("🚗 Car Purchase"):
                car_year = st.slider("Purchase Year", 1, projection_years, 2, key="car_year")
                car_price = st.number_input("Car Price ($)", 5000, 150000, 30000, step=5000)
                car_down_payment_pct = st.slider("Down Payment %", 5, 100, 20) / 100
                if st.button("Add Car Purchase Milestone"):
                    milestone = MilestoneFactory.create_car_purchase(
                        car_year, car_price, car_down_payment_pct)
                    st.session_state.milestones.append(milestone)
                    st.rerun()

            # Graduate School Milestone
            with st.sidebar.expander("🎓 Graduate School"):
                grad_year = st.slider("Start Year", 1, projection_years, 2, key="grad_year")
                total_cost = st.number_input("Total Cost ($)", 10000, 200000, 100000, step=10000)
                program_years = st.slider("Program Length (Years)", 1, 4, 2)
                if st.button("Add Graduate School Milestone"):
                    milestone = MilestoneFactory.create_grad_school(
                        grad_year, total_cost, program_years)
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

            # Create financial objects with milestones
            assets, liabilities, income, expenses = DataProcessor.create_financial_objects(
                location_data,
                st.session_state.milestones
            )

            # Calculate projections
            calculator = FinancialCalculator(assets, liabilities, income, expenses)
            current_projections = calculator.calculate_yearly_projection(projection_years)

            # Display summary metrics with comparisons
            st.markdown("### Financial Summary")
            col5, col6, col7 = st.columns(3)

            def format_change(current, previous):
                if previous is None:
                    return ""
                change = int(round(current - previous))
                color = "green" if change >= 0 else "red"
                sign = "+" if change >= 0 else ""
                return f'<p style="color: {color}; font-size: 14px; margin-top: 0;">{sign}${change:,}</p>'

            with col5:
                st.metric("Initial Net Worth 💰",
                       f"${int(round(current_projections['net_worth'][0])):,}")
                if st.session_state.previous_projections:
                    st.markdown(
                        format_change(
                            current_projections['net_worth'][0],
                            st.session_state.previous_projections['net_worth'][0]
                        ),
                        unsafe_allow_html=True
                    )

            with col6:
                st.metric("Final Net Worth 🚀",
                       f"${int(round(current_projections['net_worth'][-1])):,}")
                if st.session_state.previous_projections:
                    st.markdown(
                        format_change(
                            current_projections['net_worth'][-1],
                            st.session_state.previous_projections['net_worth'][-1]
                        ),
                        unsafe_allow_html=True
                    )

            with col7:
                current_avg_cash_flow = int(round(sum(current_projections['cash_flow'])/len(current_projections['cash_flow'])))
                st.metric(
                    "Average Annual Cash Flow 💵",
                    f"${current_avg_cash_flow:,}"
                )
                if st.session_state.previous_projections:
                    prev_avg_cash_flow = int(round(sum(st.session_state.previous_projections['cash_flow'])/len(st.session_state.previous_projections['cash_flow'])))
                    st.markdown(
                        format_change(current_avg_cash_flow, prev_avg_cash_flow),
                        unsafe_allow_html=True
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
                    current_projections['years'],
                    current_projections['net_worth'],
                    current_projections['asset_values'],
                    current_projections['liability_values']
                )

            with tab2:
                st.markdown("### Cash Flow Analysis")
                FinancialPlotter.plot_cash_flow(
                    current_projections['years'],
                    current_projections['total_income'],
                    current_projections['expense_categories'],
                    current_projections['total_expenses'],
                    current_projections['cash_flow'],
                    current_projections['income_streams']
                )

            with tab3:
                st.markdown("### Assets and Liabilities")
                FinancialPlotter.plot_assets_liabilities(
                    current_projections['years'],
                    current_projections['asset_values'],
                    current_projections['liability_values']
                )

            # Store current projections as previous before any new milestone is added
            st.session_state.previous_projections = current_projections

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.write("Debug info:", e)

if __name__ == "__main__":
    main()