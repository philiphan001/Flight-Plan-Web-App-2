import streamlit as st
import pandas as pd
import numpy as np

def load_college_data():
    """Load and preprocess college scorecard data"""
    try:
        df = pd.read_csv('attached_assets/Updated_Most-Recent-Cohorts-Institution.csv')
        # Clean up column names and select relevant columns
        return df
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
    states = sorted(df['STABBR'].unique())
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
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_states:
        filtered_df = filtered_df[filtered_df['STABBR'].isin(selected_states)]
    
    filtered_df = filtered_df[
        (filtered_df['ADM_RATE'] * 100 >= admission_rate_range[0]) &
        (filtered_df['ADM_RATE'] * 100 <= admission_rate_range[1])
    ]
    
    # Display results
    st.subheader(f"Found {len(filtered_df)} matching institutions")
    
    # Show results in an expandable format
    for _, college in filtered_df.iterrows():
        with st.expander(f"{college['INSTNM']} - {college['CITY']}, {college['STABBR']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Institution Details**")
                st.write(f"Type: {college['CONTROL']}")
                st.write(f"Admission Rate: {college['ADM_RATE']*100:.1f}%")
                st.write(f"Average SAT Score: {college['SAT_AVG']}")
            
            with col2:
                st.write("**Cost Information**")
                st.write(f"In-State Tuition: ${college['TUITIONFEE_IN']:,.2f}")
                st.write(f"Out-of-State Tuition: ${college['TUITIONFEE_OUT']:,.2f}")
                st.write(f"Books and Supplies: ${college['BOOKSUPPLY']:,.2f}")

if __name__ == "__main__":
    load_college_discovery_page()
