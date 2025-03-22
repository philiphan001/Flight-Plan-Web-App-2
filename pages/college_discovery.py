"""College discovery page implementation"""
import streamlit as st
import pandas as pd
import numpy as np
from models.user_favorites import UserFavorites
from difflib import get_close_matches
from fuzzywuzzy import fuzz

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

def get_best_matches(search_query: str, df: pd.DataFrame, num_matches: int = 3) -> pd.DataFrame:
    """Find the best matching colleges using fuzzy string matching"""
    if not search_query:
        return pd.DataFrame()
    
    # Calculate similarity scores for each college name
    scores = [(name, fuzz.ratio(search_query.lower(), name.lower()))
             for name in df['name']]
    
    # Sort by score in descending order and get top matches
    best_matches = sorted(scores, key=lambda x: x[1], reverse=True)[:num_matches]
    best_match_names = [match[0] for match in best_matches]
    
    # Create a new DataFrame with the matching rows
    matched_colleges = df[df['name'].isin(best_match_names)].copy()
    
    # Create a mapping for sorting
    name_to_order = {name: idx for idx, name in enumerate(best_match_names)}
    
    # Add sort order and sort
    matched_colleges.loc[:, 'sort_order'] = matched_colleges['name'].map(name_to_order)
    matched_colleges = matched_colleges.sort_values('sort_order')
    matched_colleges = matched_colleges.drop('sort_order', axis=1)
    
    return matched_colleges

def display_college_card(college: pd.Series, show_favorite_button: bool = True, source: str = "filter"):
    """Display a college card with consistent styling"""
    # Create a title that includes ranking if available
    if pd.notna(college['US News Top 150']):
        title = f"🏫 #{int(college['US News Top 150'])} - {college['name']}"
    elif pd.notna(college['best liberal arts colleges']):
        title = f"🏫 Liberal Arts #{int(college['best liberal arts colleges'])} - {college['name']}"
    else:
        title = f"🏫 {college['name']}"
    
    # Add location to title
    title += f" ({college['city']}, {college['state']})"

    with st.expander(title):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Institution Details**")
            if pd.notna(college['admission_rate.overall']):
                st.write(f"• Admission Rate: {college['admission_rate.overall']*100:.1f}%")
            if pd.notna(college['sat_scores.average.overall']):
                st.write(f"• Average SAT: {int(college['sat_scores.average.overall'])}")
            if pd.notna(college['US News Top 150']):
                st.write(f"• US News: #{int(college['US News Top 150'])}")
            if pd.notna(college['best liberal arts colleges']):
                st.write(f"• Liberal Arts: #{int(college['best liberal arts colleges'])}")
        
        with col2:
            st.write("**Cost Information**")
            if college['ownership'] == 1:  # Public institution
                if pd.notna(college['avg_net_price.public']):
                    st.write(f"• In-State: ${int(college['avg_net_price.public']):,}")
                if pd.notna(college['avg_net_price.private']):
                    st.write(f"• Out-of-State: ${int(college['avg_net_price.private']):,}")
            else:  # Private institution
                if pd.notna(college['avg_net_price.private']):
                    st.write(f"• Tuition: ${int(college['avg_net_price.private']):,}")
            
            if show_favorite_button:
                college_dict = college.to_dict()
                # Create a unique key using name, city, state, and source
                unique_key = f"{college['name']}_{college['city']}_{college['state']}_{source}"
                if UserFavorites.is_favorite_school(college_dict):
                    if st.button("❌ Remove", key=f"remove_{unique_key}", use_container_width=True):
                        UserFavorites.remove_favorite_school(college_dict)
                        st.rerun()
                else:
                    if st.button("⭐ Add", key=f"add_{unique_key}", use_container_width=True):
                        UserFavorites.add_favorite_school(college_dict)
                        st.rerun()

def load_college_discovery_page():
    st.title("College Discovery 🎓")

    # Initialize favorites
    UserFavorites.init_session_state()

    # Load data
    df = load_college_data()
    if df is None:
        return

    # Create a search section at the top
    st.markdown("## 🔍 Quick Search")
    search_query = st.text_input(
        "Search for a college by name",
        placeholder="Enter college name (e.g., Harvard, Stanford, MIT)",
        help="This will show the top 3 closest matches to your search"
    )

    # Display search results if there's a query
    if search_query:
        matched_colleges = get_best_matches(search_query, df)
        if not matched_colleges.empty:
            st.markdown("### Top Matches")
            with st.container():
                for _, college in matched_colleges.iterrows():
                    # Create a unique key using both the school name and location
                    unique_key = f"{college['name']}_{college['city']}_{college['state']}"
                    if st.button(f"View {college['name']}", key=f"search_view_{unique_key}", use_container_width=True):
                        display_college_card(college, source="search")
        else:
            st.info("No matching colleges found. Try a different search term.")
        
        st.markdown("---")

    st.markdown("## 📊 Advanced Filters")

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
        # Display favorites in sidebar
        st.markdown("### Your Favorite Schools ⭐")
        favorite_schools = UserFavorites.get_favorite_schools()

        if favorite_schools:
            for school in favorite_schools:
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Create a unique key using both the school name and location
                    unique_key = f"{school['name']}_{school['city']}_{school['state']}"
                    if st.button(f"📚 {school['name']}", key=f"fav_view_{unique_key}", use_container_width=True):
                        with st.expander(f"⭐ {school['name']}", expanded=True):
                            st.write(f"Location: {school['city']}, {school['state']}")
                            if 'US News Top 150' in school and pd.notna(school['US News Top 150']):
                                st.write(f"US News Ranking: #{int(school['US News Top 150'])}")
                            if 'best liberal arts colleges' in school and pd.notna(school['best liberal arts colleges']):
                                st.write(f"Liberal Arts Ranking: #{int(school['best liberal arts colleges'])}")
                with col2:
                    if st.button("❌", key=f"remove_fav_{school['name']}", help="Remove from favorites"):
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
            default=[],
            help="Filter colleges by state(s). Select multiple states by clicking."
        )

        # Tuition filters
        st.sidebar.subheader("Tuition Filters")

        # In-state tuition range for public schools
        in_state_tuition_range = st.sidebar.slider(
            "In-State Tuition Range ($)",
            0, 50000, (0, 50000),
            step=1000,
            help="Filter public schools by in-state tuition"
        )

        # Out-of-state/private tuition range
        out_state_tuition_range = st.sidebar.slider(
            "Out-of-State/Private Tuition Range ($)",
            0, 75000, (0, 75000),
            step=1000,
            help="Filter schools by out-of-state (public) or private tuition"
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

        # Apply state filter if states are selected
        if selected_states:
            filtered_df = filtered_df[filtered_df['state'].isin(selected_states)].copy()

        # Apply tuition filters
        # For public schools (ownership == 1), check in-state tuition
        public_mask = (
            (filtered_df['ownership'] == 1) & 
            (
                pd.isna(filtered_df['avg_net_price.public']) |
                (
                    (filtered_df['avg_net_price.public'] >= in_state_tuition_range[0]) &
                    (filtered_df['avg_net_price.public'] <= in_state_tuition_range[1])
                )
            )
        )

        # For private schools and out-of-state public tuition
        private_mask = (
            (filtered_df['ownership'].isin([2, 3])) & 
            (
                pd.isna(filtered_df['avg_net_price.private']) |
                (
                    (filtered_df['avg_net_price.private'] >= out_state_tuition_range[0]) &
                    (filtered_df['avg_net_price.private'] <= out_state_tuition_range[1])
                )
            )
        )

        # Combine masks
        filtered_df = filtered_df[public_mask | private_mask]

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

        # Display results in a scrollable container
        st.subheader(f"Found {len(filtered_df)} matching institutions")
        with st.container():
            max_height = 600  # Maximum height in pixels
            st.markdown(f"""
                <style>
                    .college-results {{
                        max-height: {max_height}px;
                        overflow-y: auto;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        background-color: #f8f9fa;
                    }}
                </style>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="college-results">', unsafe_allow_html=True)
                for _, college in filtered_df.iterrows():
                    display_college_card(college, source="filter")
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    load_college_discovery_page()