"""User profile page implementation"""
import streamlit as st
import pandas as pd
from models.user_favorites import UserFavorites
from utils.zip_income import get_income_estimate
from services.financial_assessment import generate_financial_assessment

def load_user_profile_page():
    st.title("Your Profile 👤")

    # Initialize session state
    if 'user_zip_code' not in st.session_state:
        st.session_state.user_zip_code = ""

    # Initialize favorites
    UserFavorites.init_session_state()

    # Add zip code input at the top of the profile
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Location Information")
        zip_code = st.text_input(
            "Enter your ZIP code",
            value=st.session_state.user_zip_code,
            max_chars=5,
            help="Used to estimate household income in your area"
        )

        if zip_code:
            # Validate zip code format
            if len(zip_code) == 5 and zip_code.isdigit():
                st.session_state.user_zip_code = zip_code
                income_data = get_income_estimate(zip_code)
                if income_data:
                    st.write("**Estimated Household Income in Your Area:**")
                    st.write(f"Mean: ${income_data['mean_income']:,}")
                else:
                    st.warning("Income data not available for this ZIP code.")
            else:
                st.error("Please enter a valid 5-digit ZIP code.")

    # Create tabs for different sections of the profile
    tabs = st.tabs([
        "Favorite Colleges 🎓",
        "Career Interests 💼",
        "Skills & Experience 🛠️",
        "Saved Projections 📊"
    ])

    # Favorite Colleges Tab
    with tabs[0]:
        st.header("Your Favorite Colleges")
        favorite_schools = UserFavorites.get_favorite_schools()

        if favorite_schools:
            # Initialize selected colleges in session state if not present
            if 'selected_colleges_for_projection' not in st.session_state:
                st.session_state.selected_colleges_for_projection = []

            for school in favorite_schools:
                # Create three columns: school name/info, projection checkbox, remove button
                col1, col2, col3 = st.columns([4, 1, 1])

                with col1:
                    # Create expander for school details
                    with st.expander(f"🏫 {school['name']}", expanded=False):
                        st.write(f"Location: {school['city']}, {school['state']}")
                        if 'US News Top 150' in school and pd.notna(school['US News Top 150']):
                            st.write(f"US News Ranking: #{int(school['US News Top 150'])}")
                        if 'best liberal arts colleges' in school and pd.notna(school['best liberal arts colleges']):
                            st.write(f"Liberal Arts Ranking: #{int(school['best liberal arts colleges'])}")

                with col2:
                    # Add checkbox for financial projection
                    is_selected = school['name'] in st.session_state.selected_colleges_for_projection
                    if st.checkbox("📊", value=is_selected, 
                                key=f"include_in_projection_{school['name']}", 
                                help="Include in Financial Projection"):
                        if school['name'] not in st.session_state.selected_colleges_for_projection:
                            st.session_state.selected_colleges_for_projection.append(school['name'])
                    elif school['name'] in st.session_state.selected_colleges_for_projection:
                        st.session_state.selected_colleges_for_projection.remove(school['name'])

                with col3:
                    # Add remove button
                    if st.button("❌", key=f"remove_{school['name']}", help="Remove from favorites"):
                        UserFavorites.remove_favorite_school(school)
                        # Also remove from selected colleges if present
                        if school['name'] in st.session_state.selected_colleges_for_projection:
                            st.session_state.selected_colleges_for_projection.remove(school['name'])
                        st.rerun()

                st.markdown("---")  # Add separator between schools
        else:
            st.info("No favorite colleges yet. Visit the College Discovery page to add some!")
            if st.button("Go to College Discovery"):
                st.switch_page("pages/college_discovery.py")

    # Career Interests Tab
    with tabs[1]:
        st.header("Your Career Interests")

        # Display saved career suggestions
        if 'saved_career_suggestions' in st.session_state and st.session_state.saved_career_suggestions:
            for idx, career in enumerate(st.session_state.saved_career_suggestions):
                with st.expander(f"📋 {career['title']}", expanded=False):
                    st.write(f"**Path Type:** {career['type'].title()}")
                    st.write(f"**Description:** {career['description']}")

                    st.write("**Timeline:**")
                    for milestone in career['timeline']:
                        st.write(f"Year {milestone['year']}: {milestone['milestone']}")
                        st.write(f"- Required Skills: {', '.join(milestone['skills_needed'])}")
                        st.write(f"- Estimated Salary: ${milestone['estimated_salary']:,}")

                    st.write(f"**Education Level:** {career['education_level']}")
                    st.write(f"**Preferred Work Style:** {career['work_style']}")

                    if st.button("❌ Remove", key=f"remove_career_sugg_{idx}"):
                        st.session_state.saved_career_suggestions.pop(idx)
                        st.rerun()
        else:
            st.info("No saved career suggestions yet. Visit the Career Suggestions page to explore!")
            if st.button("Go to Career Suggestions"):
                st.switch_page("pages/career_suggestions.py")

    # Skills & Experience Tab
    with tabs[2]:
        st.header("Your Skills & Experience")

        # Display interests from career suggestions
        if 'user_interests' in st.session_state and st.session_state.user_interests:
            st.subheader("Interests")
            for interest in st.session_state.user_interests:
                st.write(f"• {interest}")

        # Display skills from career suggestions
        if 'user_skills' in st.session_state and st.session_state.user_skills:
            st.subheader("Skills")
            for skill in st.session_state.user_skills:
                st.write(f"• {skill}")

        # Additional skills input
        st.subheader("Add Additional Skills")
        new_skill = st.text_input("Add a new skill")
        if new_skill and st.button("Add Skill"):
            if 'user_skills' not in st.session_state:
                st.session_state.user_skills = []
            if new_skill not in st.session_state.user_skills:
                st.session_state.user_skills.append(new_skill)
                st.rerun()

        # Experience section
        st.subheader("Add Experience")
        exp_title = st.text_input("Title/Position")
        exp_description = st.text_area("Description")
        exp_duration = st.text_input("Duration (e.g., '2 years', 'Summer 2024')")

        if exp_title and exp_description and exp_duration and st.button("Add Experience"):
            if 'user_experience' not in st.session_state:
                st.session_state.user_experience = []
            new_exp = {
                "title": exp_title,
                "description": exp_description,
                "duration": exp_duration
            }
            st.session_state.user_experience.append(new_exp)
            st.rerun()

        # Display experiences
        if 'user_experience' in st.session_state and st.session_state.user_experience:
            st.subheader("Experience")
            for idx, exp in enumerate(st.session_state.user_experience):
                with st.expander(f"{exp['title']} - {exp['duration']}", expanded=False):
                    st.write(exp['description'])
                    if st.button("Remove", key=f"remove_exp_{idx}"):
                        st.session_state.user_experience.pop(idx)
                        st.rerun()

    # Saved Projections Tab
    with tabs[3]:
        st.header("Your Saved Financial Projections")
        if 'saved_projections' in st.session_state and st.session_state.saved_projections:
            for idx, proj in enumerate(st.session_state.saved_projections):
                with st.expander(f"Projection: {proj['name']} ({proj['date']})", expanded=False):
                    st.write(f"Location: {proj['location']}")
                    st.write(f"Occupation: {proj['occupation']}")
                    st.write(f"Investment Return Rate: {proj['investment_rate']}%")
                    st.write(f"Final Net Worth: ${proj['final_net_worth']:,}")

                    # Display milestones if present
                    if 'milestones' in proj and proj['milestones']:
                        st.subheader("Life Milestones:")
                        for milestone in proj['milestones']:
                            st.markdown(f"**{milestone['name']} (Year {milestone['year']})**")

                            # Display milestone-specific details
                            if milestone['type'] == 'Marriage':
                                st.write(f"Wedding Cost: ${milestone['wedding_cost']:,}")
                                st.write(f"Spouse Occupation: {milestone['spouse_occupation']}")
                                st.write(f"Lifestyle Adjustment: {milestone['lifestyle_adjustment']}%")
                                st.write(f"Spouse Initial Savings: ${milestone['spouse_savings']:,}")
                                st.write(f"Spouse Initial Debt: ${milestone['spouse_debt']:,}")

                            elif milestone['type'] == 'HomePurchase':
                                st.write(f"Home Price: ${milestone['home_price']:,}")
                                st.write(f"Down Payment: {milestone['down_payment']}%")
                                st.write(f"Monthly Utilities: ${milestone['monthly_utilities']:,}")
                                st.write(f"Monthly HOA: ${milestone['monthly_hoa']:,}")
                                st.write(f"Annual Renovation Budget: ${milestone['annual_renovation']:,}")

                            elif milestone['type'] == 'CarPurchase':
                                st.write(f"Car Price: ${milestone['car_price']:,}")
                                st.write(f"Down Payment: {milestone['down_payment']}%")
                                st.write(f"Vehicle Type: {milestone['vehicle_type']}")
                                st.write(f"Monthly Fuel Cost: ${milestone['monthly_fuel']:,}")
                                st.write(f"Monthly Parking: ${milestone['monthly_parking']:,}")

                            elif milestone['type'] == 'Child':
                                st.write(f"Monthly Education Savings: ${milestone['education_savings']/12:,.2f}")
                                st.write(f"Annual Healthcare Cost: ${milestone['healthcare_cost']:,}")
                                st.write(f"Annual Insurance Cost: ${milestone['insurance_cost']:,}")
                                st.write(f"Annual Tax Benefit: ${milestone['tax_benefit']:,}")

                            elif milestone['type'] == 'GraduateSchool':
                                st.write(f"Total Cost: ${milestone['total_cost']:,}")
                                st.write(f"Program Length: {milestone['program_years']} years")
                                st.write(f"Part-time Income: ${milestone['part_time_income']:,}/year")
                                st.write(f"Scholarship Amount: ${milestone['scholarship_amount']:,}")
                                st.write(f"Expected Salary Increase: {milestone['salary_increase']}%")

                            st.markdown("---")

                    # Add AI Assessment section
                    st.subheader("💡 AI Financial Assessment")
                    if st.button("Generate Assessment", key=f"gen_assessment_{idx}"):
                        with st.spinner("Generating financial assessment..."):
                            assessment = generate_financial_assessment(proj)
                            st.markdown(f"**Analysis:**\n{assessment}")

                    if st.button("Remove", key=f"remove_proj_{idx}"):
                        st.session_state.saved_projections.pop(idx)
                        st.rerun()
        else:
            st.info("No saved financial projections yet. Create some in the Financial Planning section!")
            if st.button("Go to Financial Planning"):
                st.switch_page("main.py")

if __name__ == "__main__":
    load_user_profile_page()