"""User profile page implementation"""
import streamlit as st
import pandas as pd
from models.user_favorites import UserFavorites

def load_user_profile_page():
    st.title("Your Profile 👤")
    
    # Initialize favorites
    UserFavorites.init_session_state()
    
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
        favorite_careers = UserFavorites.get_favorite_careers()
        
        if favorite_careers:
            for career in favorite_careers:
                with st.expander(f"⭐ {career['title']}", expanded=False):
                    if 'description' in career:
                        st.write(career['description'])
                    if 'salary' in career:
                        st.write(f"Average Salary: ${career['salary']:,}")
                    if st.button("❌ Remove", key=f"remove_career_{career['title']}"):
                        UserFavorites.remove_favorite_career(career)
                        st.rerun()
        else:
            st.info("No saved career interests yet. Visit the Career Discovery page to explore!")
            if st.button("Go to Career Discovery"):
                st.switch_page("pages/career_discovery.py")
    
    # Skills & Experience Tab
    with tabs[2]:
        st.header("Your Skills & Experience")
        if 'user_skills' not in st.session_state:
            st.session_state.user_skills = []
        if 'user_experience' not in st.session_state:
            st.session_state.user_experience = []
            
        # Add new skill
        new_skill = st.text_input("Add a new skill")
        if new_skill and st.button("Add Skill"):
            if new_skill not in st.session_state.user_skills:
                st.session_state.user_skills.append(new_skill)
                st.rerun()
        
        # Display skills
        if st.session_state.user_skills:
            st.subheader("Skills")
            for skill in st.session_state.user_skills:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {skill}")
                with col2:
                    if st.button("Remove", key=f"remove_skill_{skill}"):
                        st.session_state.user_skills.remove(skill)
                        st.rerun()
        
        # Add new experience
        st.subheader("Add Experience")
        exp_title = st.text_input("Title/Position")
        exp_description = st.text_area("Description")
        exp_duration = st.text_input("Duration (e.g., '2 years', 'Summer 2024')")
        
        if exp_title and exp_description and exp_duration and st.button("Add Experience"):
            new_exp = {
                "title": exp_title,
                "description": exp_description,
                "duration": exp_duration
            }
            st.session_state.user_experience.append(new_exp)
            st.rerun()
        
        # Display experiences
        if st.session_state.user_experience:
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
        if 'saved_projections' not in st.session_state:
            st.session_state.saved_projections = []
            
        if st.session_state.saved_projections:
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
