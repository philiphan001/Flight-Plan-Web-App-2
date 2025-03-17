import streamlit as st
import pandas as pd
from difflib import get_close_matches
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from models.financial_models import MilestoneFactory, SpouseIncome as ModelSpouseIncome

def update_location(new_location: str):
    """Callback for location updates"""
    st.session_state.selected_location = new_location
    st.session_state.needs_recalculation = True
    st.session_state.previous_projections = None

def update_occupation(new_occupation: str):
    """Callback for occupation updates"""
    st.session_state.selected_occupation = new_occupation
    st.session_state.needs_recalculation = True
    st.session_state.previous_projections = None

def initialize_session_state():
    """Initialize all session state variables"""
    if 'needs_recalculation' not in st.session_state:
        st.session_state.needs_recalculation = True
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
    if 'show_location_matches' not in st.session_state:
        st.session_state.show_location_matches = False
    if 'show_occupation_matches' not in st.session_state:
        st.session_state.show_occupation_matches = False
    if 'sidebar_location_input' not in st.session_state:
        st.session_state.sidebar_location_input = ""
    if 'sidebar_occupation_input' not in st.session_state:
        st.session_state.sidebar_occupation_input = ""
    if 'selected_spouse_occ' not in st.session_state:
        st.session_state['selected_spouse_occ'] = ""
    if 'show_marriage_options' not in st.session_state:
        st.session_state.show_marriage_options = False
    if 'saved_projections' not in st.session_state:
        st.session_state.saved_projections = []


def main():
    initialize_session_state()
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
                    location_input = st.text_input("Enter Location")
                    if location_input:
                        matches = get_close_matches(location_input.lower(),
                                                   [loc.lower() for loc in locations],
                                                   n=3, cutoff=0.1)
                        matching_locations = [loc for loc in locations if loc.lower() in matches]
                        if matching_locations:
                            st.markdown("#### Select from matches:")
                            for loc in matching_locations:
                                if st.button(f"📍 {loc}", key=f"loc_{loc}", on_click=update_location,
                                             args=(loc,)):
                                    st.rerun()

            with col2:
                st.markdown("### Select Your Occupation 💼")
                if st.session_state.selected_occupation:
                    st.markdown(f"**Selected Occupation:** {st.session_state.selected_occupation}")
                else:
                    occupation_input = st.text_input("Enter Occupation")
                    if occupation_input:
                        matches = get_close_matches(occupation_input.lower(),
                                                   [occ.lower() for occ in occupations],
                                                   n=3, cutoff=0.1)
                        matching_occupations = [occ for occ in occupations if occ.lower() in matches]
                        if matching_occupations:
                            st.markdown("#### Select from matches:")
                            for occ in matching_occupations:
                                if st.button(f"💼 {occ}", key=f"occ_{occ}", on_click=update_occupation,
                                             args=(occ,)):
                                    st.rerun()

            # Show continue button only if both selections are made
            if st.session_state.selected_location and st.session_state.selected_occupation:
                st.markdown("---")
                if st.button("Continue to Financial Projections ➡️"):
                    st.session_state.show_projections = True
                    st.rerun()

        else:
            # Back button
            if st.button("← Back to Selection"):
                st.session_state.show_projections = False
                st.session_state.needs_recalculation = True
                st.rerun()

            # Add location and occupation editing in sidebar
            st.sidebar.markdown("## Current Selections 📍")

            # Location editor
            st.sidebar.markdown(f"**Current Location:** {st.session_state.selected_location}")
            if st.sidebar.checkbox("Change Location"):
                new_location = st.sidebar.text_input(
                    "Enter New Location",
                    key="new_location_input"
                )
                if new_location:
                    matches = get_close_matches(new_location.lower(),
                                               [loc.lower() for loc in locations],
                                               n=3, cutoff=0.1)
                    matching_locations = [loc for loc in locations if loc.lower() in matches]
                    if matching_locations:
                        st.sidebar.markdown("#### Select from matches:")
                        for loc in matching_locations:
                            if st.sidebar.button(f"📍 {loc}", key=f"new_loc_{loc}", on_click=update_location,
                                                 args=(loc,)):
                                st.rerun()

            # Occupation editor
            st.sidebar.markdown(f"**Current Occupation:** {st.session_state.selected_occupation}")
            if st.sidebar.checkbox("Change Occupation"):
                new_occupation = st.sidebar.text_input(
                    "Enter New Occupation",
                    key="new_occupation_input"
                )
                if new_occupation:
                    matches = get_close_matches(new_occupation.lower(),
                                               [occ.lower() for occ in occupations],
                                               n=3, cutoff=0.1)
                    matching_occupations = [occ for occ in occupations if occ.lower() in matches]
                    if matching_occupations:
                        st.sidebar.markdown("#### Select from matches:")
                        for occ in matching_occupations:
                            if st.sidebar.button(f"💼 {occ}", key=f"new_occ_{occ}", on_click=update_occupation,
                                                 args=(occ,)):
                                st.rerun()

            st.sidebar.markdown("---")

            # Investment and projection settings
            col3, col4 = st.columns(2)
            with col3:
                investment_return_rate = st.slider(
                    "Investment Return Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=7.0,
                    step=0.5,
                    key="investment_rate",
                    on_change=lambda: setattr(st.session_state, 'needs_recalculation', True)
                ) / 100.0

            with col4:
                projection_years = st.slider(
                    "Projection Years",
                    1, 30, 10,
                    key="projection_years",
                    on_change=lambda: setattr(st.session_state, 'needs_recalculation', True)
                )

            # Only calculate if we need to
            if st.session_state.needs_recalculation:
                try:
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
                        st.session_state.milestones
                    )

                    # Calculate projections
                    calculator = FinancialCalculator(assets, liabilities, income, expenses)
                    st.session_state.current_projections = calculator.calculate_yearly_projection(projection_years)
                    st.session_state.needs_recalculation = False

                except ValueError as e:
                    st.error(str(e))
                    st.session_state.show_projections = False
                    st.rerun()
                    return

                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")
                    st.write("Debug info:", e)
                    st.session_state.show_projections = False
                    st.rerun()
                    return

            # Life Milestones Section in Sidebar
            st.sidebar.markdown("## Life Milestones 🎯")
            st.sidebar.markdown("Add life events to see their impact:")

            # Marriage Milestone
            with st.sidebar.expander("💑 Marriage"):
                milestone_year = st.slider("Marriage Year", 1, projection_years, 2, key="marriage_year")
                wedding_cost = st.number_input("Wedding Cost ($)", 10000, 100000, 30000, step=5000, key="wedding_cost")

                # New marriage variables
                joint_lifestyle_adjustment = st.slider(
                    "Joint Lifestyle Cost Adjustment (%)",
                    -20, 50, 0,
                    help="How much will your lifestyle costs change after marriage?",
                    key="joint_lifestyle"
                )
                spouse_savings = st.number_input(
                    "Spouse's Current Savings ($)",
                    0, 1000000, 0,
                    step=1000,
                    key="spouse_savings"
                )
                spouse_debt = st.number_input(
                    "Spouse's Current Debt ($)",
                    0, 1000000, 0,
                    step=1000,
                    key="spouse_debt"
                )
                joint_insurance_cost = st.number_input(
                    "Joint Insurance Monthly Cost ($)",
                    0, 2000, 200,
                    step=50,
                    key="joint_insurance"
                )

                # Spouse occupation input and selection
                spouse_occupation_input = st.text_input(
                    "Enter Spouse's Occupation",
                    key="spouse_occ_input"
                )

                if spouse_occupation_input:
                    matches = get_close_matches(spouse_occupation_input.lower(),
                                               [occ.lower() for occ in occupations],
                                               n=3, cutoff=0.1)
                    matching_occupations = [occ for occ in occupations if occ.lower() in matches]
                    if matching_occupations:
                        st.markdown("#### Select Spouse's Occupation:")
                        cols = st.columns(len(matching_occupations))
                        for idx, occ in enumerate(matching_occupations):
                            with cols[idx]:
                                if st.button(f"💼 {occ}", key=f"spouse_occ_{occ}"):
                                    st.session_state.selected_spouse_occ = occ
                                    st.session_state.needs_recalculation = True
                                    st.rerun()
                    else:
                        st.error("No matching occupations found")

                # Show Add Marriage Milestone button only if spouse occupation is selected
                if st.session_state.selected_spouse_occ:
                    st.markdown(f"**Selected Spouse Occupation:** {st.session_state.selected_spouse_occ}")
                    if st.button("Add Marriage Milestone"):
                        # Process spouse's income data
                        spouse_data = DataProcessor.process_location_data(
                            coli_df, occupation_df,
                            st.session_state.selected_location,
                            st.session_state.selected_spouse_occ,
                            investment_return_rate
                        )
                        spouse_income = ModelSpouseIncome(
                            spouse_data['base_income'],
                            spouse_data['location_adjustment'],
                            lifestyle_adjustment=joint_lifestyle_adjustment / 100,
                            initial_savings=spouse_savings,
                            initial_debt=spouse_debt,
                            insurance_cost=joint_insurance_cost * 12
                        )
                        milestone = MilestoneFactory.create_marriage(
                            milestone_year,
                            wedding_cost,
                            spouse_income,
                            lifestyle_adjustment=joint_lifestyle_adjustment / 100,
                            initial_savings=spouse_savings,
                            initial_debt=spouse_debt,
                            insurance_cost=joint_insurance_cost * 12
                        )
                        st.session_state.milestones.append(milestone)
                        st.session_state.needs_recalculation = True
                        st.rerun()

            # Child Milestone
            with st.sidebar.expander("👶 New Child"):
                child_year = st.slider("Child Year", 1, projection_years, 3, key="child_year")
                # New child variables
                education_savings = st.number_input(
                    "Monthly Education Savings ($)",
                    0, 2000, 200,
                    step=50,
                    help="Amount to save monthly for education",
                    key="education_savings"
                )
                healthcare_cost = st.number_input(
                    "Additional Monthly Healthcare ($)",
                    0, 1000, 200,
                    step=50,
                    key="child_healthcare"
                )
                child_insurance = st.number_input(
                    "Additional Monthly Insurance ($)",
                    0, 500, 100,
                    step=25,
                    key="child_insurance"
                )
                tax_benefit = st.number_input(
                    "Estimated Annual Tax Benefit ($)",
                    0, 10000, 2000,
                    step=500,
                    help="Child tax credits and deductions",
                    key="child_tax_benefit"
                )

                if st.button("Add Child Milestone"):
                    milestone = MilestoneFactory.create_child(
                        child_year,
                        education_savings=education_savings * 12,
                        healthcare_cost=healthcare_cost * 12,
                        insurance_cost=child_insurance * 12,
                        tax_benefit=tax_benefit
                    )
                    st.session_state.milestones.append(milestone)
                    st.session_state.needs_recalculation = True
                    st.rerun()

            # Home Purchase Milestone
            with st.sidebar.expander("🏠 Home Purchase"):
                home_year = st.slider("Purchase Year", 1, projection_years, 5, key="home_year")
                home_price = st.number_input("Home Price ($)", 100000, 2000000, 300000, step=50000)
                down_payment_pct = st.slider("Down Payment %", 5, 40, 20) / 100

                # New home variables
                monthly_utilities = st.number_input(
                    "Estimated Monthly Utilities ($)",
                    100, 1000, 300,
                    step=50,
                    key="utilities"
                )
                monthly_hoa = st.number_input(
                    "Monthly HOA Fees ($)",
                    0, 1000, 0,
                    step=25,
                    key="hoa"
                )
                annual_renovation = st.number_input(
                    "Annual Renovation Budget ($)",
                    0, 50000, 2000,
                    step=500,
                    key="renovation"
                )
                home_office = st.checkbox(
                    "Home Office Deduction",
                    help="Include home office tax deduction",
                    key="home_office"
                )
                if home_office:
                    office_area_pct = st.slider(
                        "Office Area % of Home",
                        1, 30, 10,
                        key="office_area"
                    )

                if st.button("Add Home Purchase Milestone"):
                    milestone = MilestoneFactory.create_home_purchase(
                        home_year, home_price, down_payment_pct,
                        monthly_utilities=monthly_utilities,
                        monthly_hoa=monthly_hoa,
                        annual_renovation=annual_renovation,
                        home_office_deduction=home_office,
                        office_percentage=office_area_pct if home_office else 0
                    )
                    st.session_state.milestones.append(milestone)
                    st.session_state.needs_recalculation = True
                    st.rerun()

            # Car Purchase Milestone
            with st.sidebar.expander("🚗 Car Purchase"):
                car_year = st.slider("Purchase Year", 1, projection_years, 2, key="car_year")
                car_price = st.number_input("Car Price ($)", 5000, 150000, 30000, step=5000)
                car_down_payment_pct = st.slider("Down Payment %", 5, 100, 20) / 100

                # New car variables
                car_type = st.selectbox(
                    "Vehicle Type",
                    ["Gas", "Electric", "Hybrid"],
                    key="car_type"
                )
                monthly_fuel = st.number_input(
                    "Estimated Monthly Fuel/Charging ($)",
                    50, 1000, 200,
                    step=25,
                    key="fuel"
                )
                monthly_parking = st.number_input(
                    "Monthly Parking Fees ($)",
                    0, 500, 0,
                    step=25,
                    key="parking"
                )
                tax_incentive = st.number_input(
                    "Tax Incentives ($)",
                    0, 10000, 0,
                    step=500,
                    help="Available tax credits for vehicle type",
                    key="car_tax_incentive"
                )

                if st.button("Add Car Purchase Milestone"):
                    milestone = MilestoneFactory.create_car_purchase(
                        car_year, car_price, car_down_payment_pct,
                        vehicle_type=car_type,
                        monthly_fuel=monthly_fuel,
                        monthly_parking=monthly_parking,
                        tax_incentive=tax_incentive
                    )
                    st.session_state.milestones.append(milestone)
                    st.session_state.needs_recalculation = True
                    st.rerun()

            # Graduate School Milestone
            with st.sidebar.expander("🎓 Graduate School"):
                grad_year = st.slider("Start Year", 1, projection_years, 2, key="grad_year")
                total_cost = st.number_input("Total Cost ($)", 10000, 200000, 100000, step=10000)
                program_years = st.slider("Program Length (Years)", 1, 4, 2)

                # New graduate school variables
                part_time_income = st.number_input(
                    "Estimated Monthly Part-Time Income ($)",
                    0, 5000, 0,
                    step=100,
                    key="part_time"
                )
                scholarship_amount = st.number_input(
                    "Expected Annual Scholarship ($)",
                    0, 50000, 0,
                    step=1000,
                    key="scholarship"
                )
                expected_salary_increase = st.slider(
                    "Expected Salary Increase After Graduation (%)",
                    0, 200, 30,
                    key="salary_increase"
                )
                networking_cost = st.number_input(
                    "Monthly Professional Development ($)",
                    0, 1000, 100,
                    step=50,
                    help="Networking events, certifications, etc.",
                    key="networking"
                )

                if st.button("Add Graduate School Milestone"):
                    milestone = MilestoneFactory.create_grad_school(
                        grad_year, total_cost, program_years,
                        part_time_income=part_time_income * 12,
                        scholarship_amount=scholarship_amount,
                        salary_increase_percentage=expected_salary_increase / 100,
                        networking_cost=networking_cost * 12
                    )
                    st.session_state.milestones.append(milestone)
                    st.session_state.needs_recalculation = True
                    st.rerun()

            # Display current milestones
            if st.session_state.milestones:
                st.sidebar.markdown("### Current Milestones")
                for idx, milestone in enumerate(st.session_state.milestones):
                    st.sidebar.markdown(f"- {milestone.name} (Year {milestone.trigger_year})")
                    if st.sidebar.button(f"Remove {milestone.name}", key=f"remove_{idx}"):
                        st.session_state.milestones.pop(idx)
                        st.session_state.needs_recalculation = True
                        st.rerun()

            # Display financial metrics only if we have projections
            if hasattr(st.session_state, 'current_projections'):
                current_projections = st.session_state.current_projections

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
                    current_avg_cash_flow = int(
                        round(sum(current_projections['cash_flow']) / len(current_projections['cash_flow'])))
                    st.metric(
                        "Average Annual Cash Flow 💵",
                        f"${current_avg_cash_flow:,}"
                    )
                    if st.session_state.previous_projections:
                        prev_avg_cash_flow = int(
                            round(sum(st.session_state.previous_projections['cash_flow']) / len(
                                st.session_state.previous_projections['cash_flow'])))
                        st.markdown(
                            format_change(current_avg_cash_flow, prev_avg_cash_flow),
                            unsafe_allow_html=True
                        )

                # Add save projection button
                col_save1, col_save2 = st.columns([3, 1])
                with col_save1:
                    scenario_name = st.text_input(
                        "Name this scenario",
                        placeholder="e.g., Base Case, With Graduate School, etc.",
                        key="scenario_name"
                    )
                with col_save2:
                    save_clicked = st.button("💾 Save Current Projection", key="save_projection_button")
                    if save_clicked:
                        if scenario_name:
                            # Create a list of milestone details
                            milestone_details = []
                            for milestone in st.session_state.milestones:
                                details = {
                                    'type': milestone.__class__.__name__,
                                    'name': milestone.name,
                                    'year': milestone.trigger_year
                                }

                                # Add specific details based on milestone type
                                if hasattr(milestone, 'wedding_cost'):
                                    details.update({
                                        'wedding_cost': milestone.wedding_cost,
                                        'spouse_occupation': st.session_state.selected_spouse_occ,
                                        'lifestyle_adjustment': milestone.lifestyle_adjustment * 100,
                                        'spouse_savings': milestone.spouse_savings,
                                        'spouse_debt': milestone.spouse_debt
                                    })
                                elif hasattr(milestone, 'home_price'):
                                    details.update({
                                        'home_price': milestone.home_price,
                                        'down_payment': milestone.down_payment_percentage * 100,
                                        'monthly_utilities': milestone.monthly_utilities,
                                        'monthly_hoa': milestone.monthly_hoa,
                                        'annual_renovation': milestone.annual_renovation
                                    })
                                elif hasattr(milestone, 'car_price'):
                                    details.update({
                                        'car_price': milestone.car_price,
                                        'down_payment': milestone.down_payment_percentage * 100,
                                        'vehicle_type': milestone.vehicle_type,
                                        'monthly_fuel': milestone.monthly_fuel,
                                        'monthly_parking': milestone.monthly_parking
                                    })
                                elif hasattr(milestone, 'education_savings'):
                                    details.update({
                                        'education_savings': milestone.education_savings,
                                        'healthcare_cost': milestone.healthcare_cost,
                                        'insurance_cost': milestone.insurance_cost,
                                        'tax_benefit': milestone.tax_benefit
                                    })
                                elif hasattr(milestone, 'total_cost'):  # Graduate School
                                    details.update({
                                        'total_cost': milestone.total_cost,
                                        'program_years': milestone.program_years,
                                        'part_time_income': milestone.part_time_income,
                                        'scholarship_amount': milestone.scholarship_amount,
                                        'salary_increase': milestone.salary_increase_percentage * 100
                                    })

                                milestone_details.append(details)

                            projection = {
                                'name': scenario_name,
                                'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                                'location': st.session_state.selected_location,
                                'occupation': st.session_state.selected_occupation,
                                'investment_rate': investment_return_rate * 100,
                                'final_net_worth': int(round(current_projections['net_worth'][-1])),
                                'milestones': milestone_details,
                                'yearly_data': {
                                    'net_worth': current_projections['net_worth'],
                                    'cash_flow': current_projections['cash_flow'],
                                    'total_income': current_projections['total_income'],
                                    'total_expenses': current_projections['total_expenses'],
                                    'asset_values': current_projections['asset_values'],
                                    'liability_values': current_projections['liability_values']
                                }
                            }
                            st.session_state.saved_projections.append(projection)
                            st.success("Projection saved to your profile!")
                        else:
                            st.warning("Please enter a name for this scenario before saving.")

                # Add profile link
                st.markdown("---")
                if st.button("👤 View Your Profile"):
                    st.switch_page("pages/user_profile.py")


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
                        current_projections['liability_values'],
                        current_projections['asset_breakdown'],
                        current_projections['liability_breakdown']
                    )

                # Store current projections as previous before any new milestone is added
                st.session_state.previous_projections = current_projections

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.write("Debug info:", e)


if __name__ == "__main__":
    main()