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

# Update the show_education_path function to use the new Firebase service
def show_education_path():
    st.markdown("""
        <h1 style='font-size: 2.5rem !important;'>
            Let's Plan Your Education Journey 🎓
        </h1>
        <p class='subtitle'>
            Explore all your post-secondary education options
        </p>
    """, unsafe_allow_html=True)

    # Initialize Firebase service
    try:
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
    except Exception as e:
        st.error(f"Error initializing Firebase service: {str(e)}")
        return

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

        search_button = st.button("Search Institution")

        if search_button and institution_input:
            with st.spinner("Searching..."):
                matching_institutions = firebase_service.search_institutions_by_name(institution_input)

                if matching_institutions:
                    st.success(f"Found {len(matching_institutions)} matching institutions")

                    for inst in matching_institutions:
                        # Create a formatted button label with college details
                        label = (f"🏛️ {inst['name']}\n"
                                f"📍 {inst['city']}, {inst['state']}\n"
                                f"💰 In-State: ${inst.get('in_state_tuition', 'N/A'):,}" 
                                if isinstance(inst.get('in_state_tuition'), (int, float)) 
                                else f"💰 In-State: N/A")

                        if st.button(label, key=f"inst_{inst['name']}"):
                            st.session_state.selected_institution = inst
                            st.rerun()
                else:
                    st.info("No matching institutions found. Try a different search term.")

        # Show selected institution details
        if isinstance(st.session_state.selected_institution, dict):
            st.markdown("### Selected Institution Details")
            inst = st.session_state.selected_institution

            # Display institution details
            st.markdown(f"""
                **{inst['name']}**  
                Location: {inst['city']}, {inst['state']}  
                In-State Tuition: ${inst.get('in_state_tuition', 'N/A'):,}  
                Out-of-State Tuition: ${inst.get('out_state_tuition', 'N/A'):,}  
                Admission Rate: {inst.get('admission_rate', 0)*100:.1f}%
            """)

            # Field of study selection
            st.markdown("### Choose Your Field of Study 📚")
            fields_of_study = inst.get('programs', [])

            if fields_of_study:
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
            else:
                st.info("No fields of study information available for this institution")

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



def main():
    # Show landing page if setup is not complete
    if not st.session_state.get('setup_complete', False):
        show_landing_page()
        return

    st.title("Financial Projection Application")

    # Add back button at the top
    if st.button("← Back to Education Selection"):
        st.session_state.setup_complete = False
        st.session_state.page = 'education_path'
        st.rerun()

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
        if 'selected_spouse_occupation' not in st.session_state:
            st.session_state.selected_spouse_occupation = None
        if 'milestones' not in st.session_state:
            st.session_state.milestones = []
        if 'editing_marriage' not in st.session_state:
            st.session_state.editing_marriage = None
        if 'temp_spouse_occupation' not in st.session_state:
            st.session_state.temp_spouse_occupation = None

        # Location input with suggestions
        location_input = st.sidebar.text_input(
            "Enter Location",
            value=st.session_state.selected_location if st.session_state.selected_location else "",
            key="location_input"
        )

        # Clear selection if user starts typing something new
        if (st.session_state.selected_location and 
            location_input != st.session_state.selected_location):
            st.session_state.selected_location = None
            st.rerun()

        if location_input and not st.session_state.selected_location:
            # Find best matches using string similarity
            matches = get_close_matches(location_input.lower(), 
                                        [loc.lower() for loc in locations], 
                                        n=3, cutoff=0.1)

            # Get original case matches
            matching_locations = [
                loc for loc in locations 
                if loc.lower() in matches
            ]

            # Show matches only if typing
            if matching_locations:
                st.sidebar.markdown("### Select a location:")
                for loc in matching_locations:
                    if st.sidebar.button(
                        loc,
                        key=f"loc_{loc}",
                        help=f"Select {loc} as your location",
                        type="secondary"
                    ):
                        st.session_state.selected_location = loc
                        st.rerun()

        # Occupation input with suggestions
        occupation_input = st.sidebar.text_input(
            "Enter Occupation",
            value=st.session_state.selected_occupation if st.session_state.selected_occupation else "",
            key="occupation_input"
        )

        # Clear selection if user starts typing something new
        if (st.session_state.selected_occupation and 
            occupation_input != st.session_state.selected_occupation):
            st.session_state.selected_occupation = None
            st.rerun()

        if occupation_input and not st.session_state.selected_occupation:
            # Find best matches using string similarity
            matches = get_close_matches(occupation_input.lower(), 
                                        [occ.lower() for occ in occupations], 
                                        n=3, cutoff=0.1)

            # Get original case matches
            matching_occupations = [
                occ for occ in occupations 
                if occ.lower() in matches
            ]

            # Show matches only if typing
            if matching_occupations:
                st.sidebar.markdown("### Select an occupation:")
                for occ in matching_occupations:
                    if st.sidebar.button(
                        occ,
                        key=f"occ_{occ}",
                        help=f"Select {occ} as your occupation",
                        type="secondary"
                    ):
                        st.session_state.selected_occupation = occ
                        st.rerun()

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
                # Spouse occupation input with suggestions
                st.sidebar.markdown("### Spouse Information")
                spouse_occupation_input = st.sidebar.text_input(
                    "Enter Spouse's Occupation",
                    value=st.session_state.selected_spouse_occupation if st.session_state.selected_spouse_occupation else "",
                    key="spouse_occupation_input"
                )

                # Clear selection if user starts typing something new
                if (st.session_state.selected_spouse_occupation and 
                    spouse_occupation_input != st.session_state.selected_spouse_occupation):
                    st.session_state.selected_spouse_occupation = None
                    st.rerun()

                if spouse_occupation_input and not st.session_state.selected_spouse_occupation:
                    # Find best matches for spouse occupation
                    spouse_matches = get_close_matches(spouse_occupation_input.lower(), 
                                                        [occ.lower() for occ in occupations], 
                                                        n=3, cutoff=0.1)

                    # Get original case matches
                    matching_spouse_occupations = [
                        occ for occ in occupations 
                        if occ.lower() in spouse_matches
                    ]

                    # Show matches only if typing
                    if matching_spouse_occupations:
                        st.sidebar.markdown("### Select Spouse's Occupation:")
                        for occ in matching_spouse_occupations:
                            if st.sidebar.button(
                                occ,
                                key=f"spouse_occ_{occ}",
                                help=f"Select {occ} as spouse's occupation",
                                type="secondary"
                            ):
                                st.session_state.selected_spouse_occupation = occ
                                st.rerun()

                # Always show the Add Marriage Milestone button and wedding cost input
                st.sidebar.markdown("### Marriage Details")
                wedding_cost = st.sidebar.number_input("Wedding Cost", value=30000)

                # Show add milestone button if spouse occupation is selected
                if st.session_state.selected_spouse_occupation:
                    if st.sidebar.button("Add Marriage Milestone"):
                        # Process spouse's income data
                        spouse_data = DataProcessor.process_location_data(
                            coli_df, occupation_df,
                            st.session_state.selected_location,
                            st.session_state.selected_spouse_occupation,
                            investment_return_rate
                        )
                        # Create spouse income object using the model class
                        spouse_income = ModelSpouseIncome(
                            spouse_data['base_income'],
                            spouse_data['location_adjustment']
                        )
                        # Create marriage milestone with spouse income
                        milestone = MilestoneFactory.create_marriage(
                            milestone_year, wedding_cost, spouse_income)
                        st.session_state.milestones.append(milestone)
                        # Clear spouse occupation selection
                        st.session_state.selected_spouse_occupation = None
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

                    # Add edit button for marriage milestone
                    if milestone.name == "Marriage":
                        if st.sidebar.button("Edit Marriage", key=f"edit_marriage_{idx}"):
                            st.session_state.editing_marriage = idx
                            # Store current spouse occupation temporarily
                            current_spouse_income = next((inc for inc in milestone.income_adjustments 
                                                        if inc.name == "Spouse Income"), None)
                            if current_spouse_income:
                                st.session_state.temp_spouse_occupation = current_spouse_income

                    # Show edit form if this milestone is being edited
                    if getattr(st.session_state, 'editing_marriage', None) == idx:
                        st.sidebar.markdown("### Edit Marriage Details")

                        # Basic details
                        new_year = st.sidebar.slider(
                            "Update Marriage Year",
                            min_value=1,
                            max_value=projection_years,
                            value=milestone.trigger_year,
                            key=f"edit_marriage_year_{idx}"
                        )
                        new_wedding_cost = st.sidebar.number_input(
                            "Update Wedding Cost",
                            value=milestone.one_time_expense,
                            key=f"edit_wedding_cost_{idx}"
                        )

                        # Spouse occupation update
                        st.sidebar.markdown("#### Update Spouse's Occupation")
                        new_spouse_occupation_input = st.sidebar.text_input(
                            "Enter New Spouse's Occupation",
                            key=f"edit_spouse_occupation_{idx}"
                        )

                        if new_spouse_occupation_input:
                            # Find best matches for spouse occupation
                            spouse_matches = get_close_matches(new_spouse_occupation_input.lower(), 
                                                                [occ.lower() for occ in occupations], 
                                                                n=3, cutoff=0.1)

                            # Get original case matches
                            matching_spouse_occupations = [
                                occ for occ in occupations 
                                if occ.lower() in spouse_matches
                            ]

                            if matching_spouse_occupations:
                                for occ in matchingspouse_occupations:
                                    is_selected = st.session_state.selected_spouse_occupation == occ
                                    if st.sidebar.button(
                                        occ,
                                        key=f"edit_spouse_occ_{idx}_{occ}",
                                        help=f"Select {occ} as new spouse's occupation",
                                        type="secondary"
                                    ):
                                        st.session_state.selected_spouse_occupation = occ
                                        st.rerun()

                                if st.session_state.selected_spouse_occupation:
                                    # Process new spouse's income data
                                    new_spouse_data = DataProcessor.process_location_data(
                                        coli_df, occupation_df,
                                        st.session_state.selected_location,
                                        st.session_state.selected_spouse_occupation,
                                        investment_return_rate
                                    )

                                    # Create new spouse income object with marriage year as start year
                                    new_spouse_income = ModelSpouseIncome(
                                        new_spouse_data['base_income'],
                                        new_spouse_data['location_adjustment'],
                                        start_year=new_year  # Set start year to marriage year
                                    )

                                    if st.sidebar.button("Save Changes", key=f"save_marriage_{idx}"):
                                        # Create new milestone with updated values
                                        new_milestone = MilestoneFactory.create_marriage(
                                            new_year, new_wedding_cost, new_spouse_income
                                        )
                                        st.session_state.milestones[idx] = new_milestone
                                        # Clear editing state
                                        st.session_state.editing_marriage = None
                                        st.session_state.selected_spouse_occupation = None
                                        st.rerun()

                        if st.sidebar.button("Cancel", key=f"cancel_marriage_{idx}"):
                            st.session_state.editing_marriage = None
                            st.session_state.selected_spouse_occupation = None
                            st.rerun()

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
                        property_tax_exp = next((e for e in milestone.recurring_expenses if e.name == "PropertyTax"), None)
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

            # Display summary metrics with emojis and styling
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Initial Net Worth 💰",
                       f"${projections['net_worth'][0]:,}")
            with col2:
                st.metric("Final Net Worth 🚀",
                       f"${projections['net_worth'][-1]:,}")
            with col3:
                st.metric("Average Annual Cash Flow 💵", 
                          f"${int(sum(projections['cash_flow'])/len(projections['cash_flow'])):,}")

            # Create tabs for different projections with emojis
            net_worth_tab, cash_flow_tab, assets_tab, home_tab = st.tabs([
                "Net Worth Projection 📈", 
                "Income & Expenses 📊", 
                "Assets & Liabilities ⚖️",
                "Home Purchase Details 🏠"
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
                    projections['cash_flow'],
                    projections['income_streams']  # Add income streams to the plot
                )

                # Create detailed cash flow DataFrame
                cash_flow_data = {
                    'Year': projections['years'],
                }

                # Add income streams
                for stream, values in projections['income_streams'].items():
                    cash_flow_data[stream] = [f"${x:,}" for x in values]

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
                # Check if there's a home purchase milestone
                home_milestone = next((m for m in st.session_state.milestones 
                                        if m.name == "Home Purchase"), None)
                if home_milestone:
                    # Get the home asset and mortgage
                    home = next((asset for asset in home_milestone.assets 
                               if isinstance(asset, Home)), None)
                    mortgage = next((liability for liability in home_milestone.liabilities 
                                      if isinstance(liability, MortgageLoan)), None)

                    if home and mortgage:
                        # Calculate home values over time
                        home_values = []
                        mortgage_balances = []
                        for year in range(projection_years):
                            if year < home_milestone.trigger_year:
                                # Before purchase, all values are 0
                                home_values.append(0)
                                mortgage_balances.append(0)
                            else:
                                # Calculate values relative to purchase year
                                years_since_purchase = year - home_milestone.trigger_year
                                home_values.append(home.calculate_value(years_since_purchase))
                                mortgage_balances.append(mortgage.get_balance(years_since_purchase))

                        # Plot home value breakdown
                        FinancialPlotter.plot_home_value_breakdown(
                            projections['years'],
                            home_values,
                            mortgage_balances
                        )

                        # Show detailed data table
                        home_data = pd.DataFrame({
                            'Year': projections['years'],
                            'Home Value': [f"${x:,}" for x in home_values],
                            'Mortgage Balance': [f"${x:,}" for x in mortgage_balances],
                            'Home Equity': [f"${x - y:,}" for x, y in zip(home_values, mortgage_balances)]
                        })
                        st.dataframe(home_data)
                else:
                    st.info("No home purchase milestone has been added yet. Add a home purchase milestone using the sidebar to see detailed projections.")

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()