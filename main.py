import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from difflib import get_close_matches
from models.financial_models import MilestoneFactory, Home, MortgageLoan, Vehicle, CarLoan

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

                    # Add edit button for home purchase milestone
                    if milestone.name == "Home Purchase":
                        if st.sidebar.button("Edit Home Purchase", key=f"edit_{idx}"):
                            st.session_state.editing_home_purchase = idx

                    # Show edit form if this milestone is being edited
                    if milestone.name == "Home Purchase" and getattr(st.session_state, 'editing_home_purchase', None) == idx:
                        st.sidebar.markdown("### Edit Home Purchase Details")

                        # Basic purchase details
                        new_year = st.sidebar.slider(
                            "Update Purchase Year",
                            min_value=1,
                            max_value=projection_years,
                            value=milestone.trigger_year,
                            key=f"edit_year_{idx}"
                        )
                        new_price = st.sidebar.number_input(
                            "Update Home Price",
                            value=float(next(asset.initial_value 
                                              for asset in milestone.assets 
                                              if isinstance(asset, Home))),
                            key=f"edit_price_{idx}"
                        )
                        new_down_payment_pct = st.sidebar.slider(
                            "Update Down Payment %",
                            5, 40, int(milestone.one_time_expense / new_price * 100),
                            key=f"edit_down_{idx}"
                        ) / 100

                        # Advanced settings
                        st.sidebar.markdown("#### Advanced Settings")

                        # Get current home for existing rates
                        current_home = next((asset for asset in milestone.assets if isinstance(asset, Home)), None)
                        current_mortgage = next((l for l in milestone.liabilities if isinstance(l, MortgageLoan)), None)

                        new_appreciation_rate = st.sidebar.slider(
                            "Home Appreciation Rate (%)",
                            0.0, 10.0, 
                            float(current_home.appreciation_rate * 100) if current_home else 3.0,
                            0.1,
                            key=f"edit_appreciation_{idx}"
                        ) / 100

                        new_mortgage_rate = st.sidebar.slider(
                            "Mortgage Interest Rate (%)",
                            2.0, 8.0, 
                            float(current_mortgage.interest_rate * 100) if current_mortgage else 3.5,
                            0.1,
                            key=f"edit_mortgage_{idx}"
                        ) / 100

                        # Get current expense rates from the recurring expenses
                        property_tax_exp = next((e for e in milestone.recurring_expenses if e.name == "Property Tax"), None)
                        insurance_exp = next((e for e in milestone.recurring_expenses if e.name == "Home Insurance"), None)
                        maintenance_exp = next((e for e in milestone.recurring_expenses if e.name == "Home Maintenance"), None)

                        new_property_tax_rate = st.sidebar.slider(
                            "Property Tax Rate (%)",
                            0.1, 5.0, 
                            float(property_tax_exp.annual_amount / new_price * 100) if property_tax_exp else 1.5,
                            0.1,
                            key=f"edit_tax_{idx}"
                        ) / 100

                        new_insurance_rate = st.sidebar.slider(
                            "Home Insurance Rate (%)",
                            0.1, 2.0, 
                            float(insurance_exp.annual_amount / new_price * 100) if insurance_exp else 0.5,
                            0.1,
                            key=f"edit_insurance_{idx}"
                        ) / 100

                        new_maintenance_rate = st.sidebar.slider(
                            "Annual Maintenance Rate (%)",
                            0.1, 5.0, 
                            float(maintenance_exp.annual_amount / new_price * 100) if maintenance_exp else 1.0,
                            0.1,
                            key=f"edit_maintenance_{idx}"
                        ) / 100

                        if st.sidebar.button("Save Changes", key=f"save_{idx}"):
                            # Create new milestone with updated values
                            new_milestone = MilestoneFactory.create_home_purchase(
                                new_year, new_price, new_down_payment_pct,
                                new_property_tax_rate, new_insurance_rate,
                                new_maintenance_rate, new_appreciation_rate,
                                new_mortgage_rate
                            )
                            st.session_state.milestones[idx] = new_milestone
                            # Clear editing state
                            st.session_state.editing_home_purchase = None
                            st.rerun()

                        if st.sidebar.button("Cancel", key=f"cancel_{idx}"):
                            st.session_state.editing_home_purchase = None
                            st.rerun()

                    # Add edit button for car purchase milestone
                    if milestone.name == "Car Purchase":
                        if st.sidebar.button("Edit Car Purchase", key=f"edit_car_{idx}"):
                            st.session_state.editing_car_purchase = idx

                    # Show edit form if this milestone is being edited
                    if milestone.name == "Car Purchase" and getattr(st.session_state, 'editing_car_purchase', None) == idx:
                        st.sidebar.markdown("### Edit Car Purchase Details")

                        # Basic purchase details
                        new_year = st.sidebar.slider(
                            "Update Purchase Year",
                            min_value=1,
                            max_value=projection_years,
                            value=milestone.trigger_year,
                            key=f"edit_car_year_{idx}"
                        )

                        # Get current car and loan details
                        current_car = next((asset for asset in milestone.assets if isinstance(asset, Vehicle)), None)
                        current_loan = next((l for l in milestone.liabilities if isinstance(l, CarLoan)), None)

                        new_price = st.sidebar.number_input(
                            "Update Car Price",
                            value=float(current_car.initial_value if current_car else 30000),
                            key=f"edit_car_price_{idx}"
                        )

                        new_down_payment_pct = st.sidebar.slider(
                            "Update Down Payment %",
                            5, 100, 
                            int(milestone.one_time_expense / new_price * 100) if milestone.one_time_expense else 20,
                            key=f"edit_car_down_{idx}"
                        ) / 100

                        # Advanced settings
                        st.sidebar.markdown("#### Advanced Settings")

                        new_loan_rate = st.sidebar.slider(
                            "Loan Interest Rate (%)",
                            2.0, 12.0, 
                            float(current_loan.interest_rate * 100) if current_loan else 4.5,
                            0.1,
                            key=f"edit_car_loan_rate_{idx}"
                        ) / 100

                        new_loan_term = st.sidebar.slider(
                            "Loan Term (Years)",
                            1, 7, 
                            int(current_loan.term_years) if current_loan else 5,
                            key=f"edit_car_loan_term_{idx}"
                        )

                        new_depreciation_rate = st.sidebar.slider(
                            "Annual Depreciation Rate (%)",
                            5.0, 30.0, 
                            float(current_car.depreciation_rate * 100) if current_car else 15.0,
                            0.5,
                            key=f"edit_car_depreciation_{idx}"
                        ) / 100

                        # Get current expense rates
                        insurance_exp = next((e for e in milestone.recurring_expenses if e.name == "Car Insurance"), None)
                        maintenance_exp = next((e for e in milestone.recurring_expenses if e.name == "Car Maintenance"), None)

                        new_insurance_rate = st.sidebar.slider(
                            "Annual Insurance Rate (% of car value)",
                            1.0, 10.0, 
                            float(insurance_exp.annual_amount / new_price * 100) if insurance_exp else 4.0,
                            0.1,
                            key=f"edit_car_insurance_{idx}"
                        ) / 100

                        new_maintenance_rate = st.sidebar.slider(
                            "Annual Maintenance Rate (% of car value)",
                            1.0, 10.0, 
                            float(maintenance_exp.annual_amount / new_price * 100) if maintenance_exp else 3.3,
                            0.1,
                            key=f"edit_car_maintenance_{idx}"
                        ) / 100

                        if st.sidebar.button("Save Changes", key=f"save_car_{idx}"):
                            # Create new milestone with updated values
                            new_milestone = MilestoneFactory.create_car_purchase(
                                new_year, new_price, new_down_payment_pct,
                                new_loan_rate, new_loan_term,
                                new_insurance_rate, new_maintenance_rate,
                                new_depreciation_rate
                            )
                            st.session_state.milestones[idx] = new_milestone
                            # Clear editing state
                            st.session_state.editing_car_purchase = None
                            st.rerun()

                        if st.sidebar.button("Cancel", key=f"cancel_car_{idx}"):
                            st.session_state.editing_car_purchase = None
                            st.rerun()

                    # Regular remove button
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
                st.session_state.milestones
            )

            # Calculate projections
            calculator = FinancialCalculator(assets, liabilities, income, expenses)
            projections = calculator.calculate_yearly_projection(projection_years)

            # Display summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Initial Net Worth",
                       f"${projections['net_worth'][0]:,}")
            with col2:
                st.metric("Final Net Worth",
                       f"${projections['net_worth'][-1]:,}")
            with col3:
                st.metric("Average Annual Cash Flow", 
                          f"${int(sum(projections['cash_flow'])/len(projections['cash_flow'])):,}")

            # Create tabs for different projections
            net_worth_tab, cash_flow_tab, assets_tab, home_tab = st.tabs([
                "Net Worth Projection", 
                "Income & Expenses", 
                "Assets & Liabilities",
                "Home Purchase Details"
            ])

            # Net Worth Tab
            with net_worth_tab:
                FinancialPlotter.plot_net_worth(projections['years'],
                                              projections['net_worth'],
                                              projections['asset_values'],
                                              projections['liability_values'],
                                              projections['investment_growth'])
                net_worth_df = pd.DataFrame({
                    'Year': projections['years'],
                    'Total Assets': [f"${x:,}" for x in projections['asset_values']],
                    'Total Liabilities': [f"${x:,}" for x in projections['liability_values']],
                    'Savings': [f"${x:,}" for x in projections['investment_growth']],
                    'Net Worth': [f"${x:,}" for x in projections['net_worth']]
                })
                st.dataframe(net_worth_df)

                # Add component breakdown
                st.subheader("Asset Components")
                assets_breakdown_df = pd.DataFrame({
                    'Year': projections['years'],
                    **{category: [f"${x:,}" for x in values] 
                       for category, values in projections['asset_breakdown'].items()}
                })
                st.dataframe(assets_breakdown_df)

                st.subheader("Liability Components")
                liabilities_breakdown_df = pd.DataFrame({
                    'Year': projections['years'],
                    **{category: [f"${x:,}" for x in values] 
                       for category, values in projections['liability_breakdown'].items()}
                })
                st.dataframe(liabilities_breakdown_df)

            # Cash Flow Tab
            with cash_flow_tab:
                FinancialPlotter.plot_cash_flow(
                    projections['years'],
                    projections['total_income'],
                    projections['expense_categories'],
                    projections['total_expenses'],
                    projections['cash_flow']
                )

                # Create detailed cash flow DataFrame
                cash_flow_data = {
                    'Year': projections['years'],
                    'Total Income': [f"${x:,}" for x in projections['total_income']],
                }

                # Add expense categories
                for category, values in projections['expense_categories'].items():
                    cash_flow_data[f"Expense: {category}"] = [f"${x:,}" for x in values]

                cash_flow_data.update({
                    'Total Expenses': [f"${x:,}" for x in projections['total_expenses']],
                    'Net Savings': [f"${x:,}" for x in projections['cash_flow']],
                    'Cumulative Investment Growth': [f"${x:,}" for x in projections['investment_growth']]
                })

                cash_flow_df = pd.DataFrame(cash_flow_data)
                st.dataframe(cash_flow_df)

            # Assets and Liabilities Tab
            with assets_tab:
                FinancialPlotter.plot_assets_liabilities(
                    projections['years'], projections['asset_values'],
                    projections['liability_values'],
                    projections['investment_growth'])

                # Create detailed breakdown DataFrames
                assets_data = {
                    'Year': projections['years'],
                }
                # Add individual asset values
                for category, values in projections['asset_breakdown'].items():
                    assets_data[category] = [f"${x:,}" for x in values]

                # Add individual liability values
                liabilities_data = {
                    'Year': projections['years'],
                }
                for category, values in projections['liability_breakdown'].items():
                    liabilities_data[category] = [f"${x:,}" for x in values]

                # Add totals
                assets_data['Total Assets'] = [f"${x:,}" for x in projections['asset_values']]
                liabilities_data['Total Liabilities'] = [f"${x:,}" for x in projections['liability_values']]

                # Display breakdowns
                st.subheader("Assets Breakdown")
                st.dataframe(pd.DataFrame(assets_data))

                st.subheader("Liabilities Breakdown")
                st.dataframe(pd.DataFrame(liabilities_data))

                st.subheader("Net Worth Summary")
                assets_liab_df = pd.DataFrame({
                    'Year': projections['years'],
                    'Total Assets': [f"${x:,}" for x in projections['asset_values']],
                    'Total Liabilities': [f"${x:,}" for x in projections['liability_values']],
                    'Net Worth': [f"${x:,}" for x in projections['net_worth']]
                })
                st.dataframe(assets_liab_df)

            # Home Purchase Details Tab
            with home_tab:
                # Find home purchase milestone if it exists
                home_milestone = next(
                    (m for m in st.session_state.milestones if m.name == "Home Purchase"),
                    None
                )

                if home_milestone:
                    st.header("Home Purchase Details")

                    # Get home and mortgage details
                    home = next((a for a in home_milestone.assets if isinstance(a, Home)), None)
                    mortgage = next((l for l in home_milestone.liabilities if isinstance(l, MortgageLoan)), None)

                    # Create columns for key metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Purchase Year", f"Year {home_milestone.trigger_year}")
                    with col2:
                        st.metric("Home Price", f"${home.initial_value:,}")
                    with col3:
                        st.metric("Down Payment", f"${home_milestone.one_time_expense:,}")

                    # Show mortgage details
                    if mortgage:
                        st.subheader("Mortgage Details")
                        st.write(f"Principal: ${mortgage.principal:,}")
                        st.write(f"Interest Rate: {mortgage.interest_rate*100:.1f}%")
                        st.write(f"Term: {mortgage.term_years} years")
                        st.write(f"Monthly Payment: ${mortgage.calculate_payment():,}")

                    # Show projected home value
                    st.subheader("Home Value Projection")
                    home_values = []
                    mortgage_balance = []
                    equity = []
                    years = list(range(projection_years))

                    for year in years:
                        if year >= home_milestone.trigger_year:
                            adj_year = year - home_milestone.trigger_year
                            home_value = home.calculate_value(adj_year)
                            mort_bal = mortgage.get_balance(adj_year) if mortgage else 0
                        else:
                            home_value = 0
                            mort_bal = 0

                        home_values.append(home_value)
                        mortgage_balance.append(mort_bal)
                        equity.append(home_value - mort_bal)

                    home_data = pd.DataFrame({
                        'Year': years,
                        'Home Value': [f"${x:,}" for x in home_values],
                        'Mortgage Balance': [f"${x:,}" for x in mortgage_balance],
                        'Home Equity': [f"${x:,}" for x in equity]
                    })
                    st.dataframe(home_data)

                else:
                    st.info("No home purchase milestone has been added yet. Add a home purchase milestone using the sidebar to see detailed projections.")

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()