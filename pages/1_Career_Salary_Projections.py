import streamlit as st
import pandas as pd
from services.bls_api import BLSApi
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter

st.set_page_config(page_title="Career Salary Projections", page_icon="💰")

def main():
    st.title("Career Salary Projections 📈")
    st.markdown("""
    Explore potential career earnings and make informed decisions about your future.
    Compare different career paths and see how your earnings could grow over time.
    """)

    try:
        bls_api = BLSApi()
    except Exception as e:
        st.error(f"Error initializing BLS API: {str(e)}")
        return

    # Career selection
    st.subheader("Select Career Path")
    occupation_search = st.text_input(
        "Search for occupations",
        placeholder="e.g., Software Developer"
    )

    if occupation_search:
        # Search for matching occupations
        matching_occupations = bls_api.search_occupations(occupation_search)
        if matching_occupations:
            selected_occupation = st.selectbox(
                "Select an occupation",
                options=[occ['title'] for occ in matching_occupations],
                index=0
            )

            # Location selection
            st.subheader("Select Location")
            available_locations = ["New York", "California", "Texas", "Florida", "Illinois"]
            selected_location = st.selectbox(
                "Choose location",
                options=available_locations
            )

            # Years of projection
            projection_years = st.slider("Projection Years", 5, 30, 10)

            # Calculate button
            if st.button("Calculate Projections"):
                st.spinner("Calculating salary projections...")

                try:
                    # Get occupation code
                    occ_code = next(
                        occ['code'] for occ in matching_occupations 
                        if occ['title'] == selected_occupation
                    )

                    # Get salary data
                    salary_data = bls_api.get_salary_by_location(occ_code, selected_location)

                    # Create salary projections
                    years = list(range(projection_years + 1))
                    base_salary = salary_data.get('median_salary', 75000)  # Example default
                    growth_rate = 0.03  # 3% annual growth
                    
                    projections = {
                        'Year': years,
                        'Salary': [base_salary * (1 + growth_rate) ** year for year in years]
                    }
                    
                    df_projections = pd.DataFrame(projections)

                    # Display results
                    st.subheader("Salary Projections")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Starting Salary", f"${base_salary:,.0f}")
                    with col2:
                        final_salary = projections['Salary'][-1]
                        st.metric("Projected Final Salary", f"${final_salary:,.0f}")
                    with col3:
                        total_growth = ((final_salary - base_salary) / base_salary) * 100
                        st.metric("Total Growth", f"{total_growth:.1f}%")

                    # Projection chart
                    st.line_chart(df_projections.set_index('Year')['Salary'])

                    # Detailed breakdown
                    st.subheader("Year-by-Year Breakdown")
                    df_projections['Salary'] = df_projections['Salary'].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(df_projections)

                except Exception as e:
                    st.error(f"Error calculating projections: {str(e)}")
        else:
            st.info("No matching occupations found. Try a different search term.")
    else:
        st.info("Enter an occupation to begin exploring salary projections.")

if __name__ == "__main__":
    main()
