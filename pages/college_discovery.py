"""College discovery page implementation"""
import streamlit as st
import pandas as pd
import numpy as np
from models.user_favorites import UserFavorites

def load_college_data():
    """Load and preprocess college scorecard data"""
    try:
        df = pd.read_csv('attached_assets/Updated_Most-Recent-Cohorts-Institution.csv')
        # Select relevant columns including the new rankings
        columns_of_interest = [
            'name', 'city', 'state', 
            'admission_rate.overall',
            'sat_scores.average.overall',
            'act_scores.midpoint.cumulative',
            'avg_net_price.public',
            'avg_net_price.private',
            'ownership',
            'US News Top 150',  # Updated column name
            'best liberal arts colleges'  # New column added
        ]
        return df[columns_of_interest]
    except Exception as e:
        st.error(f"Error loading college data: {str(e)}")
        return None

def load_college_discovery_page():
    st.title("College Discovery 🎓")

    # Initialize favorites
    UserFavorites.init_session_state()

    # Load data
    df = load_college_data()
    if df is None:
        return

    # Main ranking filter at the top of the page
    show_top_150 = st.checkbox(
        "Show Only Top 150 Schools",
        value=True,  # Default to showing Top 150
        help="Display only schools ranked in US News Top 150. This filter is applied by default."
    )

    # Create two columns for layout
    col1, col2 = st.columns(2)

    with col1:
        show_liberal_arts = st.checkbox(
            "Top Liberal Arts Colleges",
            value=False,
            help="Filter for top Liberal Arts Colleges"
        )

    with col2:
        st.checkbox(
            "Best Greek Life",
            value=False,
            disabled=True,
            help="Coming soon: Filter for schools with outstanding Greek life"
        )

    # Create two columns for main content and favorites
    main_col, favorites_col = st.columns([2, 1])

    with favorites_col:
        st.markdown("### Your Favorite Schools ⭐")
        favorite_schools = UserFavorites.get_favorite_schools()

        if favorite_schools:
            for school in favorite_schools:
                with st.expander(f"⭐ {school['name']}", expanded=False):
                    st.write(f"Location: {school['city']}, {school['state']}")
                    if 'US News Top 150' in school and pd.notna(school['US News Top 150']):
                        st.write(f"US News Ranking: #{int(school['US News Top 150'])}")
                    if 'best liberal arts colleges' in school and pd.notna(school['best liberal arts colleges']):
                        st.write(f"Liberal Arts Ranking: #{int(school['best liberal arts colleges'])}")
                    if st.button("❌ Remove from Favorites", key=f"remove_{school['name']}"):
                        UserFavorites.remove_favorite_school(school)
                        st.rerun()
        else:
            st.info("No favorite schools yet. Add some by clicking the star!")

    with main_col:
        # Sidebar filters
        st.sidebar.header("Filter Options")

        # State filter
        states = sorted(df['state'].unique())
        selected_states = st.sidebar.multiselect(
            "Select States",
            options=states,
            default=[]
        )

        # Admission rate filter
        admission_rate_range = st.sidebar.slider(
            "Admission Rate (%)",
            0.0, 100.0, (0.0, 100.0),
            step=5.0
        )

        # SAT Score Range
        sat_range = st.sidebar.slider(
            "SAT Score Range",
            min_value=400,
            max_value=1600,
            value=(400, 1600),
            step=10
        )

        # Institution type mapping
        institution_types = {
            1: "Public",
            2: "Private Non-Profit",
            3: "Private For-Profit"
        }
        selected_types = st.sidebar.multiselect(
            "Institution Type",
            options=list(institution_types.values()),
            default=list(institution_types.values())
        )

        # Apply filters
        filtered_df = df.copy()

        # Always apply Top 150 filter first if checkbox is selected
        if show_top_150:
            filtered_df = filtered_df[filtered_df['US News Top 150'].notna()].sort_values('US News Top 150')

        # Apply Liberal Arts filter if selected
        if show_liberal_arts:
            filtered_df = filtered_df[filtered_df['best liberal arts colleges'].notna()].sort_values('best liberal arts colleges')

        if selected_states:
            filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

        # Set null admission rates to 100% and then filter
        filtered_df['admission_rate.overall'] = filtered_df['admission_rate.overall'].fillna(1.0)
        filtered_df = filtered_df[
            (filtered_df['admission_rate.overall'] * 100 >= admission_rate_range[0]) &
            (filtered_df['admission_rate.overall'] * 100 <= admission_rate_range[1])
        ]

        # Handle SAT score filter with missing data
        sat_mask = pd.isna(filtered_df['sat_scores.average.overall']) | (
            (filtered_df['sat_scores.average.overall'] >= sat_range[0]) &
            (filtered_df['sat_scores.average.overall'] <= sat_range[1])
        )
        filtered_df = filtered_df[sat_mask]

        # Filter by institution type
        if selected_types:
            # Create a mapping from type name back to code
            type_to_code = {v: k for k, v in institution_types.items()}
            selected_codes = [type_to_code[type_name] for type_name in selected_types]
            filtered_df = filtered_df[filtered_df['ownership'].isin(selected_codes)]

        # Display results
        st.subheader(f"Found {len(filtered_df)} matching institutions")

        # Show results in an expandable format
        for _, college in filtered_df.iterrows():
            # Create title with appropriate ranking
            if show_liberal_arts and pd.notna(college['best liberal arts colleges']):
                title = f"Liberal Arts #{int(college['best liberal arts colleges'])} - {college['name']} - {college['city']}, {college['state']}"
            elif pd.notna(college['US News Top 150']):
                title = f"#{int(college['US News Top 150'])} - {college['name']} - {college['city']}, {college['state']}"
            else:
                title = f"{college['name']} - {college['city']}, {college['state']}"

            with st.expander(title):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write("**Institution Details**")
                    # Get institution type from mapping
                    institution_type = institution_types.get(college['ownership'], 'Unknown')
                    st.write(f"Type: {institution_type}")

                    # Show appropriate ranking information
                    if pd.notna(college['US News Top 150']):
                        st.write(f"US News Ranking: #{int(college['US News Top 150'])}")
                    else:
                        st.write("US News Ranking: Not ranked")

                    if pd.notna(college['best liberal arts colleges']):
                        st.write(f"Liberal Arts Ranking: #{int(college['best liberal arts colleges'])}")

                    # Show admission rate if available
                    if pd.notna(college['admission_rate.overall']):
                        st.write(f"Admission Rate: {college['admission_rate.overall']*100:.1f}%")
                    else:
                        st.write("Admission Rate: Not available")

                    # Show SAT score if available
                    if pd.notna(college['sat_scores.average.overall']):
                        st.write(f"Average SAT Score: {int(college['sat_scores.average.overall'])}")
                    else:
                        st.write("Average SAT Score: Not available")

                with col2:
                    st.write("**Cost Information**")
                    # Show appropriate cost based on institution type
                    if college['ownership'] == 1 and pd.notna(college['avg_net_price.public']):
                        st.write(f"Average Net Price: ${int(college['avg_net_price.public']):,}")
                    elif college['ownership'] in [2, 3] and pd.notna(college['avg_net_price.private']):
                        st.write(f"Average Net Price: ${int(college['avg_net_price.private']):,}")
                    else:
                        st.write("Average Net Price: Not available")

                    # Add favorite button
                    college_dict = college.to_dict()
                    if UserFavorites.is_favorite_school(college_dict):
                        if st.button("❌ Remove from Favorites", key=f"remove_{college['name']}"):
                            UserFavorites.remove_favorite_school(college_dict)
                            st.rerun()
                    else:
                        if st.button("⭐ Add to Favorites", key=f"add_{college['name']}"):
                            UserFavorites.add_favorite_school(college_dict)
                            st.rerun()

if __name__ == "__main__":
    load_college_discovery_page()