import streamlit as st
import pandas as pd
import numpy as np

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
            'us_news_ranking'  # New column for rankings
        ]
        return df[columns_of_interest]
    except Exception as e:
        st.error(f"Error loading college data: {str(e)}")
        return None

def load_college_discovery_page():
    st.title("College Discovery 🎓")

    # Load data
    df = load_college_data()
    if df is None:
        return

    # Sidebar filters
    st.sidebar.header("Filter Options")

    # Add US News Rankings filter
    ranking_range = st.sidebar.slider(
        "US News Top Rankings",
        1, 150, (1, 150),
        help="Filter by US News World Report Rankings"
    )

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

    # Cost filters
    tuition_range = st.sidebar.slider(
        "Annual Tuition Range ($)",
        0, 100000, (0, 100000),
        step=5000
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

    # Apply US News Rankings filter
    filtered_df = filtered_df[
        (filtered_df['us_news_ranking'].isnull()) |  # Include unranked schools
        (
            (filtered_df['us_news_ranking'] >= ranking_range[0]) &
            (filtered_df['us_news_ranking'] <= ranking_range[1])
        )
    ]

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
        with st.expander(f"{college['name']} - {college['city']}, {college['state']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Institution Details**")
                # Get institution type from mapping
                institution_type = institution_types.get(college['ownership'], 'Unknown')
                st.write(f"Type: {institution_type}")

                # Show US News Ranking if available
                if pd.notna(college['us_news_ranking']):
                    st.write(f"US News Ranking: #{int(college['us_news_ranking'])}")
                else:
                    st.write("US News Ranking: Not ranked")

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

if __name__ == "__main__":
    load_college_discovery_page()