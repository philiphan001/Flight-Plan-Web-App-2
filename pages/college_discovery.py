import streamlit as st
import pandas as pd
import numpy as np

def load_college_data():
    """Load and preprocess college scorecard data"""
    try:
        df = pd.read_csv('attached_assets/Updated_Most-Recent-Cohorts-Institution.csv')
        # Select relevant columns
        columns_of_interest = [
            'name', 'city', 'state', 
            'admission_rate.overall',
            'sat_scores.average.overall',
            'act_scores.midpoint.cumulative',
            'avg_net_price.public',
            'avg_net_price.private',
            'ownership'
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

    # Institution type
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

    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

    filtered_df = filtered_df[
        (filtered_df['admission_rate.overall'] * 100 >= admission_rate_range[0]) &
        (filtered_df['admission_rate.overall'] * 100 <= admission_rate_range[1])
    ]

    filtered_df = filtered_df[
        (filtered_df['sat_scores.average.overall'] >= sat_range[0]) &
        (filtered_df['sat_scores.average.overall'] <= sat_range[1])
    ]

    # Display results
    st.subheader(f"Found {len(filtered_df)} matching institutions")

    # Show results in an expandable format
    for _, college in filtered_df.iterrows():
        with st.expander(f"{college['name']} - {college['city']}, {college['state']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Institution Details**")
                st.write(f"Type: {institution_types.get(college['ownership'], 'Other')}")
                st.write(f"Admission Rate: {college['admission_rate.overall']*100:.1f}%")
                st.write(f"Average SAT Score: {college['sat_scores.average.overall']}")

            with col2:
                st.write("**Cost Information**")
                if pd.notna(college['avg_net_price.public']):
                    st.write(f"Public Institution Cost: ${college['avg_net_price.public']:,.2f}")
                if pd.notna(college['avg_net_price.private']):
                    st.write(f"Private Institution Cost: ${college['avg_net_price.private']:,.2f}")

if __name__ == "__main__":
    load_college_discovery_page()