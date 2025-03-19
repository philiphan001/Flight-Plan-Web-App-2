import streamlit as st
import pandas as pd
from difflib import get_close_matches
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from models.financial_models import MilestoneFactory, SpouseIncome as ModelSpouseIncome, Home
from models.user_favorites import UserFavorites  # Added import for UserFavorites

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
    if 'selected_colleges_for_projection' not in st.session_state:
        st.session_state.selected_colleges_for_projection = []
    if 'add_home_milestone' not in st.session_state:
        st.session_state.add_home_milestone = False
    if 'home_milestone_params' not in st.session_state:
        st.session_state.home_milestone_params = {}


def main():
    initialize_session_state()
    # Debug information
    with st.sidebar.expander("Debug Information", expanded=False):
        st.write("Session State:")
        st.json({
            "show_projections": st.session_state.get("show_projections", False),
            "needs_recalculation": st.session_state.get("needs_recalculation", True),
            "selected_location": st.session_state.get("selected_location", None),
            "selected_occupation": st.session_state.get("selected_occupation", None),
            "num_milestones": len(st.session_state.get("milestones", [])),
            "has_home_milestone": any(
                getattr(m, "name", "") == "Home Purchase"
                for m in st.session_state.get("milestones", [])
            )
        })
    # Initialize UserFavorites session state
    UserFavorites.init_session_state()
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

        # Add debug logging for state tracking
        with st.sidebar.expander("🔍 Debug State", expanded=False):
            st.write("Current State:")
            st.write(f"- Show Projections: {st.session_state.show_projections}")
            st.write(f"- Location: {st.session_state.selected_location}")
            st.write(f"- Occupation: {st.session_state.selected_occupation}")
            st.write(f"- Needs Recalculation: {st.session_state.needs_recalculation}")
            st.write(f"- Number of Milestones: {len(st.session_state.milestones)}")

        # Only reset show_projections if explicitly requested
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
                office_area_pct = 0
                if home_office:
                    office_area_pct = st.slider(
                        "Office Area % of Home",
                        1, 30, 10,
                        key="office_area"
                    )

                if st.button("Add Home Purchase", key="add_home_btn"):
                    st.session_state.add_home_milestone = True
                    st.session_state.home_milestone_params = {
                        'year': home_year,
                        'price': home_price,
                        'down_payment_pct': down_payment_pct,
                        'monthly_utilities': monthly_utilities,
                        'monthly_hoa': monthly_hoa,
                        'annual_renovation': annual_renovation,
                        'home_office': home_office,
                        'office_area_pct': office_area_pct
                    }

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

            # Add this block AFTER all other milestone expanders
            if st.session_state.add_home_milestone:
                try:
                    params = st.session_state.home_milestone_params
                    milestone = MilestoneFactory.create_home_purchase(
                        params['year'], 
                        params['price'],
                        params['down_payment_pct'],
                        monthly_utilities=params['monthly_utilities'],
                        monthly_hoa=params['monthly_hoa'],
                        annual_renovation=params['annual_renovation'],
                        home_office_deduction=params['home_office'],
                        office_percentage=params['office_area_pct'] if params['home_office'] else 0
                    )
                    st.session_state.milestones.append(milestone)
                    st.session_state.needs_recalculation = True
                    st.sidebar.success("Home purchase milestone added successfully!")
                except Exception as e:
                    st.sidebar.error(f"Error adding home purchase milestone: {str(e)}")
                finally:
                    st.session_state.add_home_milestone = False
                    st.session_state.home_milestone_params = {}


            # Display current milestones
            if st.session_state.milestones:
                st.sidebar.markdown("---")
                with st.sidebar.expander("✏️ Edit Milestones", expanded=False):
                    st.markdown("### Current Milestones")
                    milestone_to_remove = None  # Track milestone to remove

                    for idx, milestone in enumerate(st.session_state.milestones):
                        st.markdown(f"#### 📌 {milestone.name} (Year {milestone.trigger_year})")

                        if "Marriage" in milestone.name:
                            # Marriage milestone editing
                            new_year = st.slider("Marriage Year", 1, projection_years, milestone.trigger_year, key=f"edit_marriage_year_{idx}")
                            new_cost = st.number_input("Wedding Cost ($)", 10000, 100000, int(milestone.one_time_expense), step=5000, key=f"edit_wedding_cost_{idx}")

                            # Update milestone if changes detected
                            if new_year != milestone.trigger_year or new_cost != milestone.one_time_expense:
                                milestone.trigger_year = new_year
                                milestone.one_time_expense = new_cost
                                st.session_state.needs_recalculation = True

                        elif "Home Purchase" in milestone.name:
                            # Home purchase milestone editing
                            new_year = st.slider("Purchase Year", 1, projection_years, milestone.trigger_year, key=f"edit_home_year_{idx}")
                            new_price = st.number_input("Home Price ($)", 100000, 2000000, int(milestone.home_price), step=50000, key=f"edit_home_price_{idx}")
                            new_down_payment = st.slider("Down Payment %", 5, 40, int(milestone.down_payment_percentage * 100), key=f"edit_down_payment_{idx}") / 100

                            if (new_year != milestone.trigger_year or
                                new_price != milestone.home_price or
                                new_down_payment != milestone.down_payment_percentage):
                                milestone.trigger_year = new_year
                                milestone.home_price = new_price
                                milestone.down_payment_percentage = new_down_payment
                                st.session_state.needs_recalculation = True

                        # Add remove button
                        col1, col2 = st.columns([4, 1])
                        with col2:
                            if st.button("🗑️", key=f"remove_milestone_{idx}", help="Remove this milestone"):
                                milestone_to_remove = idx

                        st.markdown("---")  # Separator between milestones

                    # Remove milestone if button was clicked
                    if milestone_to_remove is not None:
                        st.session_state.milestones.pop(milestone_to_remove)
                        st.session_state.needs_recalculation = True
                        st.rerun()  # Only rerun after removing a milestone

            if st.session_state.selected_colleges_for_projection:
                st.sidebar.markdown("### Selected Colleges 🎓")
                for college_name in st.session_state.selected_colleges_for_projection:
                    # Find the college data from favorites
                    college = next((school for school in UserFavorites.get_favorite_schools()
                                   if school['name'] == college_name), None)
                    if college:
                        st.sidebar.markdown(f"**{college['name']}**")
                        if 'avg_net_price.private' in college and pd.notna(college['avg_net_price.private']):
                            annual_cost = float(college['avg_net_price.private'])
                        elif 'avg_net_price.public' in college and pd.notna(college['avg_net_price.public']):
                            annual_cost = float(college['avg_net_price.public'])
                        else:
                            annual_cost = 30000  # Default annual cost if not available

                        college_years = st.sidebar.slider(
                            "Years of Study",
                            2, 4, 4,
                            key=f"college_years_{college_name}"
                        )

                        st.sidebar.info(f"Note: The {college_years} years of college education will precede your {projection_years}-year financial projection.")

                        # Add college as milestone if button clicked
                        if st.sidebar.button("Add to Financial Plan", key=f"add_college_{college_name}"):
                            milestone = MilestoneFactory.create_education(
                                trigger_year=0,  # Start at year 0 (pre-projection)
                                total_cost=annual_cost * college_years,
                                program_years=college_years,
                                institution_name=college['name'],
                                location=f"{college['city']}, {college['state']}",
                                is_undergraduate=True,
                                pre_projection=True  # New flag to indicate this happens before projection
                            )
                            st.session_state.milestones.append(milestone)
                            st.session_state.needs_recalculation = True
                            st.rerun()


            # Display financial metrics only if we have projections
            if hasattr(st.session_state, 'current_projections'):
                current_projections = st.session_state.current_projections

                try:
                    # Add debug information
                    st.sidebar.markdown("### Debug Information")
                    if st.sidebar.checkbox("Show Debug Info"):
                        st.sidebar.json(current_projections)

                    # Add debug information for milestone detection
                    with st.sidebar.expander("🔍 Debug Information", expanded=False):
                        st.write("Current Milestones:")
                        for milestone in st.session_state.milestones:
                            st.write(f"- {milestone.name} (Year {milestone.trigger_year})")
                            if hasattr(milestone, 'home_price'):
                                st.write(f"  Home Price: ${milestone.home_price:,.2f}")


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
                        scenario_name= st.text_input(
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
                                    details= {
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
                                            'down_payment': milestone.downpayment_percentage * 100,
                                            'monthly_utilities': milestone.monthly_utilities,
                                            'monthly_hoa': milestone.monthly_hoa,
                                            'annual_rerenovation': milestone.annual_renovation
                                        })
                                    elif hasattr(milestone, 'car_price'):
                                        details.update({
                                            'car_price': milestone.car_price,
                                            'car_downpayment': milestone.down_payment_percentage * 100,
                                            'vehicle_type': milestone.vehicle_type,
                                            'monthly_fuel': milestone.monthly_fuel,
                                            'monthly_parking': milestone.monthly_parking,
                                            'tax_incentive': milestone.tax_incentive
                                        })
                                    elif hasattr(milestone, 'education_savings'):
                                        details.update({
                                            'education_savings': milestone.education_savings,
                                            'healthcare_cost': milestone.healthcare_cost,
                                            'insurance_cost': milestone.insurance_cost,
                                            'tax_benefit': milestone.tax_benefit
                                        })
                                    elif hasattr(milestone, 'total_cost'):  # GraduateSchool
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
                    tab_list = ["Net Worth Projection 📈", "Cash Flow Analysis 💰", "Assets & Liabilities ⚖️"]

                    # Add Home Equity tab if there's a home purchase milestone
                    has_home_milestone = False
                    for milestone in st.session_state.milestones:
                        if milestone.name == "Home Purchase":
                            has_home_milestone = True
                            break

                    # Debug information about milestone detection
                    with st.sidebar.expander("🔍 Milestone Detection", expanded=False):
                        st.write("Checking for home purchase milestone:")
                        st.write(f"Number of milestones: {len(st.session_state.milestones)}")
                        st.write(f"Has home milestone: {has_home_milestone}")
                        for idx, milestone in enumerate(st.session_state.milestones):
                            st.write(f"Milestone {idx + 1}:")
                            st.write(f"- Name: {milestone.name}")
                            st.write(f"- Year: {milestone.trigger_year}")
                            if hasattr(milestone, 'home_price'):
                                st.write(f"- Home price: ${milestone.home_price:,.2f}")

                    # Add the Home Equity tab if we found a home milestone
                    if has_home_milestone:
                        tab_list.append("Home Equity Analysis 🏠")
                        st.sidebar.write("Home tab will be added")
                        st.sidebar.write(f"Current tab list: {tab_list}")

                    # Create the tabs
                    tabs = st.tabs(tab_list)
                    st.sidebar.write(f"Number of tabs created: {len(tabs)}")

                    with tabs[0]:
                        st.markdown("### Net Worth Over Time")
                        FinancialPlotter.plot_net_worth(
                            current_projections['years'],
                            current_projections['net_worth'],
                            current_projections['asset_values'],
                            current_projections['liability_values']
                        )

                    with tabs[1]:
                        st.markdown("### Cash Flow Analysis")
                        # Calculate total income by summing income streams
                        total_income = []
                        if 'income_streams' in current_projections:
                            for year_idx in range(len(current_projections['years'])):
                                year_total = sum(
                                    income_stream[year_idx]
                                    for income_stream in current_projections['income_streams'].values()
                                )
                                total_income.append(year_total)
                        else:
                            st.error("Income streams data not found in projections")
                            st.json(current_projections.keys())
                            return

                        FinancialPlotter.plot_cash_flow(
                            current_projections['years'],
                            total_income,
                            current_projections['expense_categories'],
                            current_projections['total_expenses'],
                            current_projections['cash_flow'],
                            current_projections['income_streams']
                        )

                    with tabs[2]:
                        st.markdown("### Assets and Liabilities")
                        FinancialPlotter.plot_assets_liabilities(
                            current_projections['years'],
                            current_projections['asset_values'],
                            current_projections['liability_values'],
                            current_projections['asset_breakdown'],
                            current_projections['liability_breakdown']
                        )

                    # Add Home Equity Analysis tab content if applicable
                    if has_home_milestone and len(tabs) > 3:
                        with tabs[3]:
                            st.markdown("### Home Equity Analysis")

                            # Debug information about projections
                            with st.expander("🔍 Debug Financial Data", expanded=False):
                                st.write("Available Asset Categories:", list(current_projections.get('asset_breakdown', {}).keys()))
                                st.write("Available Liability Categories:", list(current_projections.get('liability_breakdown', {}).keys()))

                            # Extract home value and mortgage data from asset/liability breakdowns
                            home_values = []
                            mortgage_values = []

                            # Find the home purchase milestone
                            home_milestone = next(
                                (m for m in st.session_state.milestones if m.name == "Home Purchase"),
                                None
                            )

                            if home_milestone:
                                purchase_year = home_milestone.trigger_year
                                current_year = current_projections['years'][0]
                                projection_length = len(current_projections['years'])

                                # Initialize arrays with zeros
                                home_values = [0] * projection_length
                                mortgage_values = [0] * projection_length

                                # Only populate values after purchase year
                                if purchase_year <= current_projections['years'][-1]:
                                    home_price = home_milestone.home_price
                                    down_payment = home_milestone.down_payment_percentage * home_price
                                    mortgage_amount = home_price - down_payment

                                    # Calculate mortgage details
                                    annual_rate = 0.065  # Assume 6.5% interest rate
                                    monthly_rate = annual_rate / 12
                                    term_years = 30
                                    num_payments = term_years * 12
                                    monthly_payment = (mortgage_amount * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

                                    # Fill in the values for each year
                                    for i, year in enumerate(current_projections['years']):
                                        if year >= purchase_year:
                                            years_since_purchase = year - purchase_year
                                            home_values[i] = home_price * (1 + 0.03)**years_since_purchase  # Assume 3% annual appreciation

                                            # Calculate remaining mortgage balance
                                            payments_made = years_since_purchase * 12
                                            if payments_made < num_payments:
                                                mortgage_values[i] = (monthly_payment * ((1 - (1 + monthly_rate)**(-(num_payments - payments_made))) / monthly_rate))
                                            else:
                                                mortgage_values[i] = 0

                                if any(home_values) and any(mortgage_values):
                                    FinancialPlotter.plot_home_value_breakdown(
                                        current_projections['years'],
                                        home_values,
                                        mortgage_values
                                    )

                                    # Add a summary of the home purchase details
                                    st.markdown("### Home Purchase Details")
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Purchase Price", f"${home_milestone.home_price:,.0f}")
                                    with col2:
                                        st.metric("Down Payment", f"${down_payment:,.0f}")
                                    with col3:
                                        st.metric("Initial Mortgage", f"${mortgage_amount:,.0f}")
                            else:
                                st.warning("Home purchase is scheduled for a future year. The equity analysis will be available once the purchase occurs.")

                    # Store current projections as previous before any new milestone is added
                    st.session_state.previous_projections = current_projections

                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
                    st.write("Debug info:", e)
                    st.session_state.show_projections = False
                    st.rerun()

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.write("Debug info:", e)
        st.session_state.show_projections = False
        st.rerun()

if __name__ == "__main__":
    main()