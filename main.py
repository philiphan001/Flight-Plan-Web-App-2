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

        # Milestone inputs
        st.sidebar.header("Life Milestones")
        
        # Initialize milestones list in session state if not present
        if 'milestones' not in st.session_state:
            st.session_state.milestones = []
            
        # Add milestone section
        add_milestone = st.sidebar.expander("Add New Milestone")
        with add_milestone:
            milestone_type = st.selectbox(
                "Milestone Type", 
                [t.value for t in MilestoneType],
                key="milestone_type"
            )
            
            milestone_year = st.number_input(
                "Year (0 = now)", 
                min_value=0, 
                max_value=projection_years-1 if 'projection_years' in locals() else 30,
                key="milestone_year"
            )
            
            # Specific inputs based on milestone type
            if milestone_type == MilestoneType.MARRIAGE.value:
                income_change = st.slider("Income Change (%)", -100, 100, 50, key="marriage_income")
                expense_change = st.slider("Expense Change (%)", -50, 100, 25, key="marriage_expense")
                
                if st.button("Add Marriage Milestone"):
                    st.session_state.milestones.append(
                        MarriageMilestone(milestone_year, income_change/100, expense_change/100)
                    )
                    st.success(f"Added Marriage milestone at year {milestone_year}")
                    
            elif milestone_type == MilestoneType.CHILD.value:
                child_expense = st.number_input("Annual Child Expenses ($)", 
                                             min_value=0, value=12000, key="child_expense")
                college_savings = st.number_input("Annual College Savings ($)",
                                               min_value=0, value=2500, key="college_savings")
                
                if st.button("Add Child Milestone"):
                    st.session_state.milestones.append(
                        ChildMilestone(milestone_year, child_expense, college_savings)
                    )
                    st.success(f"Added Child milestone at year {milestone_year}")
                    
            elif milestone_type == MilestoneType.HOME_PURCHASE.value:
                home_value = st.number_input("Home Purchase Price ($)", 
                                          min_value=0, value=350000, key="home_value")
                down_payment = st.slider("Down Payment (%)", 0, 100, 20, key="down_payment")
                interest_rate = st.slider("Interest Rate (%)", 2.0, 8.0, 3.5, key="interest_rate")
                mortgage_term = st.selectbox("Mortgage Term (years)", [15, 20, 30], index=2, key="mortgage_term")
                
                if st.button("Add Home Purchase Milestone"):
                    st.session_state.milestones.append(
                        HomePurchaseMilestone(milestone_year, home_value, down_payment/100, 
                                            interest_rate/100, mortgage_term)
                    )
                    st.success(f"Added Home Purchase milestone at year {milestone_year}")
                    
            elif milestone_type == MilestoneType.CAR_PURCHASE.value:
                car_value = st.number_input("Car Purchase Price ($)", 
                                         min_value=0, value=30000, key="car_value")
                car_down_payment = st.slider("Down Payment (%)", 0, 100, 20, key="car_down_payment")
                car_interest = st.slider("Interest Rate (%)", 2.0, 10.0, 4.5, key="car_interest")
                car_term = st.selectbox("Loan Term (years)", [3, 4, 5, 6], index=2, key="car_term")
                
                if st.button("Add Car Purchase Milestone"):
                    st.session_state.milestones.append(

            elif milestone_type == MilestoneType.CAR_PURCHASE.value:
                car_value = st.number_input("Car Purchase Price ($)", 
                                         min_value=0, value=30000, key="car_value")
                car_down_payment = st.slider("Down Payment (%)", 0, 100, 20, key="car_down_payment")
                car_interest = st.slider("Interest Rate (%)", 2.0, 10.0, 4.5, key="car_interest")
                car_term = st.selectbox("Loan Term (years)", [3, 4, 5, 6], index=2, key="car_term")
                
                if st.button("Add Car Purchase Milestone"):
                    st.session_state.milestones.append(
                        CarPurchaseMilestone(milestone_year, car_value, car_down_payment/100, 
                                           car_interest/100, car_term)
                    )
                    st.success(f"Added Car Purchase milestone at year {milestone_year}")
                    
            elif milestone_type == MilestoneType.PROMOTION.value:
                salary_increase = st.slider("Salary Increase (%)", 0, 100, 15, key="promotion_increase")
                
                if st.button("Add Promotion Milestone"):
                    st.session_state.milestones.append(
                        PromotionMilestone(milestone_year, salary_increase/100)
                    )
                    st.success(f"Added Promotion milestone at year {milestone_year}")
                    
            elif milestone_type == MilestoneType.EDUCATION.value:
                edu_years = st.number_input("Duration (years)", min_value=1, max_value=10, value=2, key="edu_years")
                edu_cost = st.number_input("Annual Tuition ($)", min_value=0, value=25000, key="edu_cost")
                income_reduction = st.slider("Income Reduction During Education (%)", 
                                          0, 100, 50, key="income_reduction")
                
                if st.button("Add Education Milestone"):
                    st.session_state.milestones.append(
                        EducationMilestone(milestone_year, edu_years, edu_cost, income_reduction/100)
                    )
                    st.success(f"Added Education milestone at year {milestone_year}")
                    
            elif milestone_type == MilestoneType.CUSTOM.value:
                custom_name = st.text_input("Milestone Name", "Custom Event", key="custom_name")
                income_change = st.number_input("Annual Income Change ($)", key="custom_income")
                expense_change = st.number_input("Annual Expense Change ($)", key="custom_expense")
                asset_change = st.number_input("Asset Value Change ($)", key="custom_asset")
                liability_change = st.number_input("Liability Change ($)", key="custom_liability")
                
                if st.button("Add Custom Milestone"):
                    st.session_state.milestones.append(
                        CustomMilestone(custom_name, milestone_year, income_change, 
                                      expense_change, asset_change, liability_change)
                    )
                    st.success(f"Added Custom milestone at year {milestone_year}")
                    
        # Display current milestones
        if st.session_state.milestones:
            st.sidebar.subheader("Current Milestones")
            for i, milestone in enumerate(st.session_state.milestones):
                st.sidebar.write(f"{milestone.year}: {milestone.name}")
                
            if st.sidebar.button("Clear All Milestones"):
                st.session_state.milestones = []
                st.sidebar.success("All milestones removed")
                
        # Show milestones visualization if we have milestones
        if 'milestones' in projections and projections['milestones']:
            st.subheader("Net Worth with Life Milestones")
            FinancialPlotter.plot_milestones(projections['years'], 
                                           projections['net_worth'],
                                           projections['milestones'])

                    "No matching locations found. Available locations: " +
                    ", ".join(locations[:3]))
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