import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from services.calculator import FinancialCalculator
from visualizations.plotter import FinancialPlotter
from difflib import get_close_matches
from models.financial_models import (
    MilestoneFactory, Home, MortgageLoan, Vehicle, CarLoan,
    SpouseIncome as ModelSpouseIncome
)
from datetime import datetime
from services.bls_api import BLSApi # Added import


# Set page configuration with custom theme
st.set_page_config(
    page_title="Future Finance Explorer 🚀",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, engaging design
st.markdown("""
    <style>
        .main {
            background-color: #f0f8ff;
        }
        .big-button {
            background-color: #4CAF50;
            color: white;
            padding: 20px 40px;
            border-radius: 15px;
            border: none;
            font-size: 1.2rem;
            font-weight: bold;
            margin: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            text-align: center;
        }
        .big-button:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .choice-card {
            background-color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 20px 0;
            text-align: center;
        }
        h1 {
            color: #2E86C1;
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            margin-bottom: 2rem !important;
            text-align: center;
        }
        .subtitle {
            color: #666;
            font-size: 1.5rem;
            margin-bottom: 3rem;
            text-align: center;
        }
        .path-button {
            background-color: #3498db;
            color: white;
            padding: 15px 30px;
            border-radius: 12px;
            border: none;
            font-size: 1.1rem;
            margin: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        .path-button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 20px;
            padding: 10px 25px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2E86C1;
            font-size: 3rem !important;
            font-weight: 800 !important;
            margin-bottom: 2rem !important;
        }
        h2 {
            color: #1ABC9C;
            font-weight: 600 !important;
        }
        .stTextInput>div>div>input {
            border-radius: 15px;
            border: 2px solid #BCE6FF;
            padding: 10px 15px;
        }
        .stTextInput>div>div>input:focus {
            border-color: #2E86C1;
            box-shadow: 0 0 0 2px rgba(46,134,193,0.2);
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            color: #2E86C1 !important;
        }
        .card {
            padding: 20px;
            border-radius: 15px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Update the show_education_path function to use the College Scorecard API
def show_education_path():
    st.markdown("""
        <h1 style='font-size: 2.5rem !important;'>
            Let's Plan Your Education Journey 🎓
        </h1>
        <p class='subtitle'>
            Explore all your post-secondary education options
        </p>
    """, unsafe_allow_html=True)

    # Initialize College Scorecard API
    try:
        from services.college_scorecard import CollegeScorecardAPI
        college_api = CollegeScorecardAPI()
    except Exception as e:
        st.error(f"Error initializing College Scorecard API: {str(e)}")
        return

    # Initialize session state
    if 'selected_institution_type' not in st.session_state:
        st.session_state.selected_institution_type = None
    if 'selected_institution' not in st.session_state:
        st.session_state.selected_institution = None
    if 'selected_field' not in st.session_state:
        st.session_state.selected_field = None

    # Center the content
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown('<div class="choice-card">', unsafe_allow_html=True)

        # Institution type selection
        st.markdown("### Type of Institution 🏛️")
        institution_types = [
            "4-Year College/University",
            "Community College",
            "Vocational/Trade School",
            "Online Programs"
        ]

        institution_type = st.selectbox(
            "Select type of institution",
            options=institution_types,
            key="institution_type"
        )

        # Institution search
        st.markdown("### Search for Institution 🔍")
        institution_input = st.text_input(
            "Enter institution name",
            value=st.session_state.selected_institution['name'] if isinstance(st.session_state.selected_institution, dict) else "",
            key="institution_input"
        )

        # Clear selection if user starts typing something new
        if (st.session_state.selected_institution and 
            institution_input != (st.session_state.selected_institution['name'] if isinstance(st.session_state.selected_institution, dict) else "")):
            st.session_state.selected_institution = None

        if institution_input and not st.session_state.selected_institution:
            # Get school type parameter for API
            school_type = college_api.get_school_type_param(institution_type)

            # Search colleges using the API
            matching_institutions = college_api.search_colleges(
                query=institution_input,
                school_type=school_type,
                limit=5
            )

            if matching_institutions:
                st.markdown("#### Select your institution:")
                for inst in matching_institutions:
                    # Create a formatted button label with college details
                    label = (f"🏛️ {inst['name']}\n"
                            f"📍 {inst['city']}, {inst['state']}\n"
                            f"💰 In-State: ${inst['in_state_tuition']:,}" if inst['in_state_tuition'] != 'N/A' else 'N/A')

                    if st.button(label, key=f"inst_{inst['name']}"):
                        st.session_state.selected_institution = inst
                        st.rerun()
            else:
                st.info("No matching institutions found. Try a different search term.")

        # Show selected institution details
        if isinstance(st.session_state.selected_institution, dict):
            st.markdown("### Selected Institution Details")
            inst = st.session_state.selected_institution
            st.markdown(f"""
                **{inst['name']}**  
                Location: {inst['city']}, {inst['state']}  
                In-State Tuition: ${inst['in_state_tuition']:,}  
                Out-of-State Tuition: ${inst['out_state_tuition']:,}  
                Admission Rate: {inst['admission_rate']*100:.1f}%
            """)

            # Fields of study
            st.markdown("### Choose Your Field of Study 📚")
            fields_of_study = inst.get('programs', [])

            field_input = st.text_input(
                "Search for your field of study",
                value=st.session_state.selected_field if st.session_state.selected_field else "",
                key="field_input"
            )

            # Clear selection if user starts typing something new
            if (st.session_state.selected_field and 
                field_input != st.session_state.selected_field):
                st.session_state.selected_field = None

            if field_input and not st.session_state.selected_field:
                matching_fields = [
                    field for field in fields_of_study 
                    if field_input.lower() in field['title'].lower()
                ]

                if matching_fields:
                    st.markdown("#### Select your field:")
                    for field in matching_fields:
                        if st.button(f"📚 {field['title']}", key=f"field_{field['title']}"):
                            st.session_state.selected_field = field['title']
                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Progress indicator
        if st.session_state.selected_institution or st.session_state.selected_field:
            progress = 0
            if st.session_state.selected_institution:
                progress += 0.5
            if st.session_state.selected_field:
                progress += 0.5

            st.progress(progress)
            st.markdown(f"<p style='text-align: center; color: #666;'>Progress: {int(progress * 100)}%</p>", 
                        unsafe_allow_html=True)

        # Continue button
        if (st.session_state.selected_institution and 
            st.session_state.selected_field):
            if st.button("Continue to Financial Planning ➡️"):
                st.session_state.setup_complete = True
                st.rerun()

    # Back button
    if st.button("← Back to Previous Page"):
        st.session_state.page = 'known_path'
        st.session_state.selected_institution = None
        st.session_state.selected_field = None
        st.rerun()

def show_salary_heatmap():
    st.markdown("""
        <h1 style='font-size: 2.5rem !important;'>
            Salary Explorer 💰
        </h1>
        <p class='subtitle'>
            Compare salaries across different locations and occupations
        </p>
    """, unsafe_allow_html=True)

    try:
        bls_api = BLSApi()
    except Exception as e:
        st.error(f"Error initializing BLS API: {str(e)}")
        return

    # Create filters in the sidebar
    st.sidebar.markdown("### Salary Explorer Filters")

    # Location selection
    st.sidebar.markdown("#### Select Locations")
    available_locations = ["New York", "California", "Texas", "Florida", "Illinois"]  # Example locations
    selected_locations = st.sidebar.multiselect(
        "Choose locations to compare",
        options=available_locations,
        default=available_locations[:3]
    )

    # Occupation selection
    st.sidebar.markdown("#### Select Occupations")
    occupation_search = st.sidebar.text_input(
        "Search for occupations",
        placeholder="e.g., Software Developer"
    )

    if occupation_search:
        matching_occupations = bls_api.search_occupations(occupation_search)
        if matching_occupations:
            selected_occupations = st.sidebar.multiselect(
                "Choose occupations to compare",
                options=[occ['title'] for occ in matching_occupations],
                default=[matching_occupations[0]['title']] if matching_occupations else []
            )
        else:
            st.sidebar.info("No matching occupations found")
            return
    else:
        st.sidebar.info("Enter an occupation to search")
        return

    if selected_locations and selected_occupations:
        # Create a progress bar for data loading
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Fetch salary data for each combination
            salary_data = []
            total_combinations = len(selected_locations) * len(selected_occupations)
            current_progress = 0

            for occupation in selected_occupations:
                occupation_data = []
                for location in selected_locations:
                    status_text.text(f"Fetching data for {occupation} in {location}...")

                    # Get occupation code
                    occ_matches = bls_api.search_occupations(occupation, limit=1)
                    if occ_matches:
                        occ_code = occ_matches[0]['code']
                        # Get salary data
                        salary_info = bls_api.get_salary_by_location(occ_code, location)
                        # Extract median salary (example value for now)
                        median_salary = 75000  # Replace with actual data extraction
                        occupation_data.append(median_salary)

                    current_progress += 1
                    progress_bar.progress(current_progress / total_combinations)

                salary_data.append(occupation_data)

            # Create DataFrame for the heatmap
            df_salary = pd.DataFrame(
                salary_data,
                index=selected_occupations,
                columns=selected_locations
            )

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            # Display the heatmap
            st.markdown("### Salary Distribution Heatmap")
            FinancialPlotter.plot_salary_heatmap(
                df_salary,
                selected_locations,
                selected_occupations
            )

            # Add some analysis
            st.markdown("### Key Insights")

            # Highest paying location-occupation combination
            max_salary = df_salary.max().max()
            max_loc = df_salary.max().idxmax()
            max_occ = df_salary.max(axis=1).idxmax()

            st.markdown(f"""
            - Highest salary: ${max_salary:,.2f} ({max_occ} in {max_loc})
            - Average salary across all selected combinations: ${df_salary.mean().mean():,.2f}
            - Salary range: ${df_salary.min().min():,.2f} - ${max_salary:,.2f}
            """)

        except Exception as e:
            st.error(f"Error fetching salary data: {str(e)}")
            return

    # Add a back button
    if st.button("← Back to Main Menu"):
        st.session_state.page = 'initial'
        st.rerun()


def show_landing_page():
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'initial'
    if 'path_chosen' not in st.session_state:
        st.session_state.path_chosen = None

    if st.session_state.page == 'initial':
        # Animated welcome message
        st.markdown("""
            <h1 style='animation: fadeIn 1s ease-in;'>
                🎓 Your Future Journey Starts Here!
            </h1>
            <p class='subtitle'>
                Let's explore your path after high school together
            </p>
        """, unsafe_allow_html=True)

        # Center the content using columns
        col1, col2, col3 = st.columns([1,2,1])

        with col2:
            st.markdown('<div class="choice-card">', unsafe_allow_html=True)

            st.markdown("### Choose Your Path 🛣️")

            if st.button("I Know What I Want to Do ✨", key="known_path", 
                        help="Choose this if you have a clear idea of your next steps"):
                st.session_state.page = 'known_path'
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Help Me Develop Some Ideas 🤔", key="explore_path",
                        help="Choose this if you'd like to explore different possibilities"):
                st.session_state.page = 'explore_path'
                st.rerun()

            if st.button("Explore Careers 💼", key="career_discovery", 
                        help="Browse and learn about different careers"):
                st.session_state.page = 'career_discovery'
                st.rerun()

            if st.button("Explore Salary Data 💰", key="salary_explorer", 
                        help="Compare salaries across different locations and occupations"):
                st.session_state.page = 'salary_explorer'
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.page == 'known_path':
        st.markdown("""
            <h1 style='font-size: 2.5rem !important;'>
                Great Choice! What's Your Plan? 🎯
            </h1>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1,1])

        with col1:
            st.markdown('<div class="choice-card">', unsafe_allow_html=True)
            if st.button("Continue My Education 📚", key="education"):
                st.session_state.path_chosen = 'education'
                st.session_state.page = 'education_path'
                st.rerun()

            if st.button("Join the Military 🎖️", key="military"):
                st.session_state.path_chosen = 'military'
                st.session_state.page = 'military_path'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="choice-card">', unsafe_allow_html=True)
            if st.button("Get a Job 💼", key="job"):
                st.session_state.path_chosen = 'job'
                st.session_state.page = 'job_path'
                st.rerun()

            if st.button("Take a Gap Year 🌎", key="gap_year"):
                st.session_state.path_chosen = 'gap_year'
                st.session_state.page = 'gap_year_path'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Add a back button
        if st.button("← Back to Main Menu"):
            st.session_state.page = 'initial'
            st.rerun()

    elif st.session_state.page == 'explore_path':
        st.markdown("""
            <h1 style='font-size: 2.5rem !important;'>
                Let's Discover Your Interests! 🌟
            </h1>
            <p class='subtitle'>
                We'll help you explore different paths through fun activities
            </p>
        """, unsafe_allow_html=True)

        # Import and run the interest quiz
        from quiz.interest_quiz import run_quiz
        run_quiz()

        # Add a back button
        if st.button("← Back to Main Menu"):
            # Reset quiz state when going back
            if 'quiz' in st.session_state:
                del st.session_state['quiz']
            if 'current_question' in st.session_state:
                del st.session_state['current_question']
            if 'selected_traits' in st.session_state:
                del st.session_state['selected_traits']
            if 'quiz_completed' in st.session_state:
                del st.session_state['quiz_completed']

            st.session_state.page = 'initial'
            st.rerun()
    elif st.session_state.page == 'education_path':
        show_education_path()

    elif st.session_state.page == 'salary_explorer':
        show_salary_heatmap()
    elif st.session_state.page == 'career_discovery':
        from pages.career_discovery import show_career_discovery
        show_career_discovery()


def show_financial_planning():
    st.markdown("""
        <h1 style='font-size: 2.5rem !important;'>
            Financial Planning Details 💰
        </h1>
    """, unsafe_allow_html=True)

    try:
        # Load data files
        coli_df = DataProcessor.load_coli_data("COLI by Location.csv")
        occupation_df = DataProcessor.load_occupation_data("Occupational Data.csv")

        # Get available options and remove any NaN values
        locations = sorted([loc for loc in coli_df['Cost of Living'].astype(str).unique().tolist() 
                   if loc.lower() != 'nan'])
        occupations = sorted([occ for occ in occupation_df['Occupation'].astype(str).unique().tolist() 
                     if occ.lower() != 'nan'])

        # Location input with suggestions
        st.markdown("### Choose Your Location 📍")
        location_input = st.text_input(
            "Enter Location",
            value=st.session_state.get('selected_location', ''),
            key="location_input"
        )

        # Show location matches
        if location_input:
            matches = get_close_matches(location_input.lower(), 
                                    [loc.lower() for loc in locations], 
                                    n=3, cutoff=0.1)

            matching_locations = [loc for loc in locations if loc.lower() in matches]

            if matching_locations:
                st.markdown("#### Select a location:")
                for loc in matching_locations:
                    if st.button(loc, key=f"loc_{loc}"):
                        st.session_state['selected_location'] = loc
                        st.rerun()

        # Rest of the financial planning UI...

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("Debug info:", locations if 'locations' in locals() else "locations not defined")
        return

def main():
    # Show landing page if setup is not complete
    if not st.session_state.get('setup_complete', False):
        show_landing_page()
        return

    # Initialize session state for financial planning
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    if 'selected_occupation' not in st.session_state:
        st.session_state.selected_occupation = None

    show_financial_planning()

if __name__ == "__main__":
    main()