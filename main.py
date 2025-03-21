"""Main application entry point"""
import streamlit as st
import pandas as pd
from difflib import get_close_matches
from utils.data_processor import DataProcessor
from utils.cache_utils import process_location_data, calculate_yearly_projection
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from models.financial_models import MilestoneFactory, SpouseIncome as ModelSpouseIncome, Home, MortgageLoan, FixedExpense, VariableExpense, OneTimeExpense, MortgagePayment, LoanPayment
from models.user_favorites import UserFavorites  # Added import for UserFavorites
import time
import plotly.graph_objects as go
from typing import Dict, List, Optional
import os
from datetime import datetime
from components.ui_components import (
    render_location_selection,
    render_occupation_selection,
    render_milestone_form,
    render_financial_controls,
    render_milestone_list
)

# Set page config - must be the first Streamlit command
st.set_page_config(
    page_title="Flight Plan - Your Financial Journey",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open('.streamlit/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'initial'
if 'needs_recalculation' not in st.session_state:
    st.session_state.needs_recalculation = True
if 'milestones' not in st.session_state:
    st.session_state.milestones = []
if 'selected_colleges_for_projection' not in st.session_state:
    st.session_state.selected_colleges_for_projection = []

# Load custom CSS
load_css()

def handle_continue_to_projections():
    """Handle transition to projections page"""
    st.session_state.show_projections = True
    st.session_state.needs_recalculation = True
    st.rerun()  # Force a rerun

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
    if 'initialized' not in st.session_state:
        st.session_state.clear()
        st.session_state.initialized = True
        st.session_state.show_projections = False
        st.session_state.needs_recalculation = True
        st.session_state.selected_location = ""
        st.session_state.selected_occupation = ""
        st.session_state.milestones = []
        st.session_state.previous_projections = None
        st.session_state.current_projections = None
        st.session_state.show_location_matches = False
        st.session_state.show_occupation_matches = False
        st.session_state.sidebar_location_input = ""
        st.session_state.sidebar_occupation_input = ""
        st.session_state.selected_spouse_occ = ""
        st.session_state.show_marriage_options = False
        st.session_state.saved_projections = []
        st.session_state.selected_colleges_for_projection = []
        st.session_state.current_page = "home"
        st.session_state.selected_year_idx = -1
        st.session_state.other_breakdown = {}

def main():
    """Main application entry point"""
    try:
        # Initialize session state
        initialize_session_state()
        
        st.title("Financial Projection Application")

        # Get current page from URL parameters
        params = st.query_params
        current_page = params.get("page", "selection")

        # Load data files
        coli_df = DataProcessor.load_coli_data("COLI by Location.csv")
        occupation_df = DataProcessor.load_occupation_data("Occupational Data.csv")

        # Get available options and remove any NaN values
        locations = sorted([loc for loc in coli_df['Cost of Living'].astype(str).unique().tolist()
                           if loc.lower() != 'nan'])
        occupations = sorted([occ for occ in occupation_df['Occupation'].astype(str).unique().tolist()
                             if occ.lower() != 'nan'])

        if current_page == "selection":
            # Create two columns for location and occupation selection
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Select Your Location 📍")
                if st.session_state.selected_location and st.session_state.selected_location != "":
                    st.markdown(f"**Selected Location:** {st.session_state.selected_location}")
                else:
                    location_input = st.text_input("Enter Location")
                    if location_input:
                        matches = get_close_matches(location_input.lower(),
                                                   [loc.lower() for loc in locations],
                                                   n=3, cutoff=0.1)
                        matching_locations = [loc for loc in locations if loc.lower() in matches]
                        if matching_locations:
                            cols = st.columns(3)
                            for idx, loc in enumerate(matching_locations):
                                with cols[idx]:
                                    if st.button(f"📍 {loc}", key=f"loc_{loc}", on_click=update_location,
                                                 args=(loc,)):
                                        st.rerun()

            with col2:
                st.markdown("### Select Your Occupation 💼")
                if st.session_state.selected_occupation and st.session_state.selected_occupation != "":
                    st.markdown(f"**Selected Occupation:** {st.session_state.selected_occupation}")
                else:
                    occupation_input = st.text_input("Enter Occupation")
                    if occupation_input:
                        matches = get_close_matches(occupation_input.lower(),
                                                   [occ.lower() for occ in occupations],
                                                   n=3, cutoff=0.1)
                        matching_occupations = [occ for occ in occupations if occ.lower() in matches]
                        if matching_occupations:
                            cols = st.columns(3)
                            for idx, occ in enumerate(matching_occupations):
                                with cols[idx]:
                                    if st.button(f"💼 {occ}", key=f"occ_{occ}", on_click=update_occupation,
                                                 args=(occ,)):
                                        st.rerun()

            # Show continue button only if both selections are made and not empty
            if (st.session_state.selected_location and st.session_state.selected_location != "" and 
                st.session_state.selected_occupation and st.session_state.selected_occupation != ""):
                if st.button("Continue to Financial Projections ➡️", use_container_width=True):
                    st.session_state.needs_recalculation = True
                    st.query_params["page"] = "projections"
                    st.rerun()

        elif current_page == "projections":
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
                    st.session_state.show_projections = False
                    st.rerun()
                    return

            # Life Milestones Section in Sidebar
            st.sidebar.markdown("## Life Milestones 🎯")
            st.sidebar.markdown("Add life events to see their impact:")

            # Marriage Milestone
            with st.sidebar.expander("💑 Marriage"):
                milestone_year = st.slider("Marriage Year", 1, projection_years, 2, key="marriage_year")
                wedding_cost = st.number_input("Wedding Cost ($)", 1000, 200000, 20000, step=5000, key="wedding_cost")

                # New marriage variables
                joint_lifestyle_adjustment = st.slider(
                    "Joint Lifestyle Cost Adjustment (%)",
                    -20, 50, 0,
                    help="How much will your lifestyle costs change after marriage?",
                    key="joint_lifestyle"
                )
                spouse_savings = st.number_input(
                    "Spouse's Current Savings ($)",
                    0, 2000000, 0,
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
                            annual_amount=spouse_data['base_income'],
                            growth_rate=0.03,  # Default growth rate
                            location_adjustment=spouse_data['location_adjustment'],
                            start_year=milestone_year,
                            lifestyle_adjustment=joint_lifestyle_adjustment / 100
                        )
                        milestone = MilestoneFactory.create_marriage(
                            milestone_year,
                            wedding_cost,
                            spouse_income=spouse_data['base_income'],
                            spouse_income_increase=0.03,  # Default growth rate
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
                    0, 3000, 200,
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
                    100, 2000, 300,
                    step=50,
                    key="utilities"
                )
                monthly_hoa = st.number_input(
                    "Monthly HOA Fees ($)",
                    0, 5000, 0,
                    step=25,
                    key="hoa"
                )
                annual_renovation = st.number_input(
                    "Annual Renovation Budget ($)",
                    0, 100000, 2000,
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
                program_years = st.slider("Program Length (Years)", 1, 6, 2)

                # Scholarship amount applies to each year
                scholarship_amount = st.number_input(
                    "Expected Annual Scholarship ($)",
                    0, 100000, 0,
                    step=1000,
                    key="scholarship"
                )

                # Create yearly cost inputs based on program length
                yearly_costs = []
                yearly_loans = []
                for year in range(program_years):
                    st.markdown(f"#### Year {year + 1} Costs")
                    cost = st.number_input(
                        f"Total Cost for Year {year + 1} ($)",
                        10000, 100000, 50000,
                        step=1000,
                        key=f"grad_year_{year}_cost"
                    )
                    loan_amount = st.number_input(
                        f"Amount to Borrow for Year {year + 1} ($)",
                        0, cost, cost,  # Max loan is the total cost
                        step=1000,
                        key=f"grad_year_{year}_loan"
                    )
                    # Show out of pocket cost for this year
                    out_of_pocket = cost - loan_amount - scholarship_amount
                    st.markdown(f"**Out of Pocket for Year {year + 1}: ${out_of_pocket:,.2f}**")
                    st.markdown("---")

                    yearly_costs.append(cost)
                    yearly_loans.append(loan_amount)

                # Other graduate school variables
                part_time_income = st.number_input(
                    "Estimated Monthly Part-Time Income ($)",
                    0, 10000, 0,
                    step=100,
                    key="part_time"
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
                        grad_year, yearly_costs, program_years,
                        yearly_loans=yearly_loans,  # Add yearly loan amounts
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
                st.sidebar.markdown("---")
                with st.sidebar.expander("✏️ Edit Milestones", expanded=False):
                    st.markdown("### Current Milestones")
                    for idx, milestone in enumerate(st.session_state.milestones):
                        st.markdown(f"#### 📌 {milestone.name} (Year {milestone.trigger_year})")

                        if "Marriage" in milestone.name:
                            # Marriage milestone editing
                            new_year = st.slider("Marriage Year", 1, projection_years, milestone.trigger_year, key=f"edit_marriage_year_{idx}")
                            # Get the wedding cost from one_time_expenses list
                            current_wedding_cost = milestone.one_time_expenses[0] if milestone.one_time_expenses else 30000
                            new_cost = st.number_input("Wedding Cost ($)", 10000, 100000, int(current_wedding_cost), step=5000, key=f"edit_wedding_cost_{idx}")

                            # Update milestone if changes detected
                            if new_year != milestone.trigger_year or new_cost != current_wedding_cost:
                                milestone.trigger_year = new_year
                                milestone.one_time_expenses[0] = new_cost
                                st.session_state.needs_recalculation = True

                        elif "Child" in milestone.name:
                            # Child milestone editing
                            new_year = st.slider("Child Year", 1, projection_years, milestone.trigger_year, key=f"edit_child_year_{idx}")
                            education_savings = next((exp.annual_amount for exp in milestone.recurring_expenses if "Education Savings" in exp.name), 0)
                            new_education_savings = st.number_input("Monthly Education Savings ($)", 0, 2000, int(education_savings/12), step=50, key=f"edit_edu_savings_{idx}")

                            if new_year != milestone.trigger_year or new_education_savings*12 != education_savings:
                                milestone.trigger_year = new_year
                                # Update education savings expense
                                for exp in milestone.recurring_expenses:
                                    if "Education Savings" in exp.name:
                                        exp.annual_amount = new_education_savings * 12
                                st.session_state.needs_recalculation = True

                        elif "Home Purchase" in milestone.name:
                            # Home purchase milestone editing
                            st.markdown(f"**Current Home Purchase Details**")
                            new_year = st.slider("Purchase Year", 1, projection_years, milestone.trigger_year, key=f"edit_home_year_{idx}")
                            home_asset = next((asset for asset in milestone.assets if isinstance(asset, Home)), None)
                            mortgage = next((liability for liability in milestone.liabilities if isinstance(liability, MortgageLoan)), None)

                            if home_asset and mortgage:
                                new_price = st.number_input("Home Price ($)", 100000, 2000000, int(home_asset.initial_value), step=50000, key=f"edit_home_price_{idx}")
                                new_down_payment_pct = st.slider("Down Payment %", 5, 40, int(home_asset.down_payment_percentage * 100), key=f"edit_down_payment_{idx}")

                                # Add all the original options
                                new_monthly_utilities = st.number_input(
                                    "Estimated Monthly Utilities ($)",
                                    100, 1000, int(home_asset.monthly_utilities),
                                    step=50,
                                    key=f"edit_utilities_{idx}"
                                )
                                new_monthly_hoa = st.number_input(
                                    "Monthly HOA Fees ($)",
                                    0, 1000, int(home_asset.monthly_hoa),
                                    step=25,
                                    key=f"edit_hoa_{idx}"
                                )
                                new_annual_renovation = st.number_input(
                                    "Annual Renovation Budget ($)",
                                    0, 50000, int(home_asset.annual_renovation),
                                    step=500,
                                    key=f"edit_renovation_{idx}"
                                )
                                new_home_office = st.checkbox(
                                    "Home Office Deduction",
                                    value=home_asset.home_office_deduction,
                                    help="Include home office tax deduction",
                                    key=f"edit_home_office_{idx}"
                                )

                                if new_home_office:
                                    new_office_area_pct = st.slider(
                                        "Office Area % of Home",
                                        1, 30, int(home_asset.office_percentage),
                                        key=f"edit_office_area_{idx}"
                                    )
                                else:
                                    new_office_area_pct = 0

                                # Create two columns for the buttons
                                col1, col2 = st.columns(2)

                                with col1:
                                    if st.button("Apply Changes", key=f"apply_home_changes_{idx}"):
                                        # Update home asset attributes
                                        home_asset.initial_value = new_price
                                        home_asset.down_payment_percentage = new_down_payment_pct / 100
                                        home_asset.monthly_utilities = new_monthly_utilities
                                        home_asset.monthly_hoa = new_monthly_hoa
                                        home_asset.annual_renovation = new_annual_renovation
                                        home_asset.home_office_deduction = new_home_office
                                        home_asset.office_percentage = new_office_area_pct

                                        # Recalculate mortgage based on new values
                                        new_loan_amount = new_price * (1 - new_down_payment_pct / 100)
                                        new_mortgage = MortgageLoan(new_loan_amount, mortgage.interest_rate, mortgage.term_years)

                                        # Update milestone attributes
                                        milestone.trigger_year = new_year
                                        milestone.one_time_expenses[0] = new_price * (new_down_payment_pct / 100)  # Update down payment

                                        # Update milestone liabilities
                                        milestone.liabilities = [liability for liability in milestone.liabilities if not isinstance(liability, MortgageLoan)]
                                        milestone.liabilities.append(new_mortgage)

                                        # Update recurring expenses
                                        property_tax_rate = 0.015  # Same as in create_home_purchase
                                        insurance_rate = 0.005
                                        maintenance_rate = 0.01

                                        # Remove all home-related expenses
                                        milestone.recurring_expenses = [exp for exp in milestone.recurring_expenses 
                                                                      if not any(name in exp.name for name in 
                                                                               ["Mortgage Payment", "Property Tax", "Home Insurance", 
                                                                                "Home Maintenance", "Utilities", "HOA Fees", "Renovation"])]

                                        # Add all updated recurring expenses
                                        monthly_payment = new_mortgage.calculate_payment()
                                        milestone.add_recurring_expense(
                                            MortgagePayment(monthly_payment * 12, mortgage.term_years, milestone.trigger_year)
                                        )
                                        milestone.add_recurring_expense(
                                            LoanPayment("Property Tax", new_price * property_tax_rate, mortgage.term_years, milestone.trigger_year)
                                        )
                                        milestone.add_recurring_expense(
                                            LoanPayment("Home Insurance", new_price * insurance_rate, mortgage.term_years, milestone.trigger_year)
                                        )
                                        milestone.add_recurring_expense(
                                            LoanPayment("Home Maintenance", new_price * maintenance_rate, mortgage.term_years, milestone.trigger_year)
                                        )

                                        # Add utility, HOA, and renovation expenses that continue indefinitely
                                        if new_monthly_utilities > 0:
                                            milestone.add_recurring_expense(VariableExpense("Utilities", new_monthly_utilities * 12))
                                        if new_monthly_hoa > 0:
                                            milestone.add_recurring_expense(FixedExpense("HOA Fees", new_monthly_hoa * 12))
                                        if new_annual_renovation > 0:
                                            milestone.add_recurring_expense(VariableExpense("Renovation", new_annual_renovation))

                                        # Add home office deduction if applicable
                                        if new_home_office and new_office_area_pct > 0:
                                            deduction = new_price * (new_office_area_pct / 100) * 0.05  # Simplified deduction calculation
                                            milestone.add_recurring_expense(FixedExpense("Home Office Deduction", -deduction))

                                        st.session_state.needs_recalculation = True
                                        st.rerun()

                                with col2:
                                    if st.button("🗑️ Remove Milestone", key=f"remove_home_{idx}"):
                                        st.session_state.milestones.pop(idx)
                                        st.session_state.needs_recalculation = True
                                        st.rerun()

                        elif "Education" in milestone.name:
                            # Education milestone editing
                            st.write("Current Education Plan:")
                            current_expense = next((exp for exp in milestone.recurring_expenses if "Tuition" in exp.name), None)
                            if current_expense:
                                annual_cost = current_expense.annual_amount
                                st.write(f"Annual Cost: ${int(annual_cost):,}")

                            # Show other favorite schools as alternatives
                            favorite_schools = UserFavorites.get_favorite_schools()
                            current_school_name = milestone.name.replace("Education: ", "")

                            if favorite_schools:
                                st.write("\nAlternative Schools from Favorites:")
                                for school in favorite_schools:
                                    if school['name'] != current_school_name:
                                        col1, col2 = st.columns([4, 1])
                                        with col1:
                                            st.write(f"🏫 {school['name']}")
                                        with col2:
                                            if st.button("Switch", key=f"switch_school_{idx}_{school['name']}", help="Switch to this school"):
                                                # Calculate new costs
                                                if 'avg_net_price.private' in school and pd.notna(school['avg_net_price.private']):
                                                    new_annual_cost = float(school['avg_net_price.private'])
                                                elif 'avg_net_price.public' in school and pd.notna(school['avg_net_price.public']):
                                                    new_annual_cost = float(school['avg_net_price.public'])
                                                else:
                                                    new_annual_cost = 30000

                                                # Update the milestone
                                                milestone.name = f"Education: {school['name']}"
                                                for exp in milestone.recurring_expenses:
                                                    if "Tuition" in exp.name:
                                                        exp.name = f"{school['name']} Tuition"
                                                        exp.annual_amount = new_annual_cost
                                                st.session_state.needsrecalculation = True
                                                st.rerun()

                        # Add remove button and separator for all milestone types
                        col1, col2 = st.columns([4, 1])
                        with col2:
                            if st.button("🗑️", key=f"remove_milestone_{idx}", help="Remove this milestone"):
                                st.session_state.milestones.pop(idx)
                                st.session_state.needs_recalculation = True
                                st.rerun()

                        st.markdown("---")  # Separator between milestones

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
                
                # Ensure we have all required data for visualizations
                if not all(key in current_projections for key in ['years', 'net_worth', 'asset_values', 'liability_values', 
                                                                'total_income', 'expense_categories', 'total_expenses', 
                                                                'cash_flow', 'income_streams', 'asset_breakdown', 
                                                                'liability_breakdown']):
                    st.error("Missing required data for visualizations. Recalculating...")
                    st.session_state.needs_recalculation = True
                    st.rerun()
                    return

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
                            format_change(current_projections['net_worth'][0],
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
                                elif hasattr(milestone, 'homeprice'):
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


if __name__ == "__main__":
    main()