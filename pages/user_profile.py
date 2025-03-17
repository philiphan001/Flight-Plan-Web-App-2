"""User profile page implementation"""
import streamlit as st
import pandas as pd
from models.user_favorites import UserFavorites
from utils.zip_income import get_income_estimate

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
                    st.write(f"Median: ${income_data['median_income']:,}")
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
            for school in favorite_schools:
                with st.expander(f"⭐ {school['name']}", expanded=False):
                    st.write(f"Location: {school['city']}, {school['state']}")
                    if 'US News Top 150' in school and pd.notna(school['US News Top 150']):
                        st.write(f"US News Ranking: #{int(school['US News Top 150'])}")
                    if 'best liberal arts colleges' in school and pd.notna(school['best liberal arts colleges']):
                        st.write(f"Liberal Arts Ranking: #{int(school['best liberal arts colleges'])}")
                    if st.button("❌ Remove", key=f"remove_school_{school['name']}"):
                        UserFavorites.remove_favorite_school(school)
                        st.rerun()
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
                with st.expander(f"Projection {idx + 1}: {proj['date']}", expanded=False):
                    st.write(f"Location: {proj['location']}")
                    st.write(f"Occupation: {proj['occupation']}")
                    st.write(f"Investment Return Rate: {proj['investment_rate']}%")
                    st.write(f"Final Net Worth: ${proj['final_net_worth']:,}")
                    if st.button("Remove", key=f"remove_proj_{idx}"):
                        st.session_state.saved_projections.pop(idx)
                        st.rerun()
        else:
            st.info("No saved financial projections yet. Create some in the Financial Planning section!")
            if st.button("Go to Financial Planning"):
                st.switch_page("main.py")

if __name__ == "__main__":
    load_user_profile_page()