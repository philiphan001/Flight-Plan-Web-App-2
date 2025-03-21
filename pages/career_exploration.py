"""Career exploration page implementation"""
import streamlit as st
import pandas as pd
import numpy as np
from models.user_favorites import UserFavorites

def load_career_data():
    """Load and preprocess BLS OEWS data"""
    try:
        df = pd.read_csv('attached_assets/BLS OEWS.csv')
        
        # Select relevant columns
        columns_of_interest = [
            'OCC_TITLE',  # Career title
            'Alias 1', 'Alias 2', 'Alias 3', 'Alias 4', 'Alias 5',  # Alternative titles
            'TOT_EMP',    # Total employment
            'A_MEAN',     # Annual mean wage
            'A_PCT10', 'A_PCT25', 'A_MEDIAN', 'A_PCT75', 'A_PCT90'  # Wage percentiles
        ]
        df = df[columns_of_interest]
        
        # Clean up employment data (remove commas and convert to numeric)
        df['TOT_EMP'] = df['TOT_EMP'].str.replace(',', '')
        df['TOT_EMP'] = pd.to_numeric(df['TOT_EMP'], errors='coerce')
        
        # Convert salary columns to numeric, handling special characters
        salary_columns = ['A_MEAN', 'A_PCT10', 'A_PCT25', 'A_MEDIAN', 'A_PCT75', 'A_PCT90']
        for col in salary_columns:
            # First convert any string numbers to proper format
            df[col] = df[col].astype(str).str.replace(',', '')
            # Then convert to numeric, replacing special characters with NaN
            df[col] = pd.to_numeric(df[col].replace(['#', '*', ''], np.nan), errors='coerce')
        
        # Clean up string columns
        string_columns = ['OCC_TITLE', 'Alias 1', 'Alias 2', 'Alias 3', 'Alias 4', 'Alias 5']
        for col in string_columns:
            df[col] = df[col].fillna('').astype(str).str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error loading career data: {str(e)}")
        return None

def format_salary(salary):
    """Format salary as currency"""
    if pd.isna(salary):
        return "Not available"
    return f"${salary:,.0f}"

def format_number(num):
    """Format large numbers with commas"""
    if pd.isna(num):
        return "Not available"
    return f"{num:,.0f}"

def load_career_exploration_page():
    st.title("Career Exploration 💼")

    # Initialize favorites
    UserFavorites.init_session_state()

    # Load data
    df = load_career_data()
    if df is None:
        return

    # Create two columns for main content and favorites
    main_col, favorites_col = st.columns([2, 1])

    with favorites_col:
        # Display favorites
        st.markdown("### Your Favorite Careers ⭐")
        favorite_careers = UserFavorites.get_favorite_careers()

        if favorite_careers:
            for career in favorite_careers:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"💼 {career['OCC_TITLE']}", key=f"view_{career['OCC_TITLE']}", use_container_width=True):
                        with st.expander(f"⭐ {career['OCC_TITLE']}", expanded=True):
                            st.write(f"Mean Annual Salary: {format_salary(career['A_MEAN'])}")
                            st.write(f"Total Employment: {format_number(career['TOT_EMP'])}")
                with col2:
                    if st.button("❌", key=f"remove_fav_{career['OCC_TITLE']}", help="Remove from favorites"):
                        UserFavorites.remove_favorite_career(career)
                        st.rerun()
        else:
            st.info("No favorite careers yet. Add some by clicking the star!")

    with main_col:
        # Simple filter options
        filter_type = st.radio(
            "View Careers By:",
            ["Top 50 by Employment", "Top 50 by Median Salary"],
            horizontal=True
        )

        # Filter and sort data based on selection
        if filter_type == "Top 50 by Employment":
            # Sort by total employment, handle NaN values
            filtered_df = df.dropna(subset=['TOT_EMP'])
            filtered_df = filtered_df.nlargest(50, 'TOT_EMP')
            st.subheader("Top 50 Careers by Total Employment")
        else:
            # Sort by median salary, handle NaN values
            filtered_df = df.dropna(subset=['A_MEDIAN'])
            filtered_df = filtered_df.sort_values('A_MEDIAN', ascending=False).head(50)
            st.subheader("Top 50 Careers by Median Salary")

        # Show results in an expandable format
        for _, career in filtered_df.iterrows():
            title = career['OCC_TITLE']
            
            # Format the title to include key information
            if filter_type == "Top 50 by Employment":
                display_title = f"{title} ({format_number(career['TOT_EMP'])} employed)"
            else:
                display_title = f"{title} (Median salary: {format_salary(career['A_MEDIAN'])})"
            
            with st.expander(display_title):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write("**Career Details**")
                    st.write(f"Median Annual Salary: {format_salary(career['A_MEDIAN'])}")
                    st.write(f"Mean Annual Salary: {format_salary(career['A_MEAN'])}")
                    st.write(f"Total Employment: {format_number(career['TOT_EMP'])}")
                    
                    # Display salary percentiles
                    st.write("\n**Salary Percentiles**")
                    st.write(f"10th Percentile: {format_salary(career['A_PCT10'])}")
                    st.write(f"25th Percentile: {format_salary(career['A_PCT25'])}")
                    st.write(f"75th Percentile: {format_salary(career['A_PCT75'])}")
                    st.write(f"90th Percentile: {format_salary(career['A_PCT90'])}")

                    # Display aliases if available
                    aliases = [
                        alias for alias in [
                            career['Alias 1'], career['Alias 2'],
                            career['Alias 3'], career['Alias 4'],
                            career['Alias 5']
                        ] if alias and alias.strip()
                    ]
                    if aliases:
                        st.write("\n**Also known as:**")
                        st.write(", ".join(aliases))

                with col2:
                    # Add to favorites button
                    if st.button("⭐", key=f"fav_{title}", help="Add to favorites"):
                        UserFavorites.add_favorite_career(career)
                        st.rerun()

if __name__ == "__main__":
    load_career_exploration_page() 