"""Career discovery page implementation"""
import streamlit as st
import pandas as pd
from services.bls_api import BLSApi
from models.user_favorites import UserFavorites
from typing import Dict, List

def show_career_details(career: Dict, bls_api: BLSApi):
    """Display detailed information for a career"""
    st.markdown(f"### {career['title']} 💼")
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Salary and employment data
        salary_data = bls_api.get_salary_by_location(career['code'], "0000000")  # National data
        employment_proj = bls_api.get_employment_projection(career['code'])
        
        st.markdown("""
        #### Salary Information 💰
        """)
        if salary_data:
            st.metric("Median Annual Salary", f"${salary_data.get('annual_mean_wage', 'N/A'):,.2f}")
        
        st.markdown("""
        #### Employment Outlook 📈
        """)
        if employment_proj:
            st.write(employment_proj.get('outlook_summary', 'Data not available'))
            
    with col2:
        # Favorite button
        if UserFavorites.is_favorite_career(career):
            if st.button("❌ Remove from Favorites", key=f"remove_{career['code']}"):
                UserFavorites.remove_favorite_career(career)
                st.rerun()
        else:
            if st.button("⭐ Add to Favorites", key=f"add_{career['code']}"):
                UserFavorites.add_favorite_career(career)
                st.rerun()

def show_career_discovery():
    """Main career discovery page"""
    st.markdown("""
        <h1 style='font-size: 2.5rem !important;'>
            Career Discovery 🔍
        </h1>
        <p class='subtitle'>
            Explore careers and their potential
        </p>
    """, unsafe_allow_html=True)

    # Initialize favorites
    UserFavorites.init_session_state()

    try:
        bls_api = BLSApi()
    except Exception as e:
        st.error(f"Error initializing BLS API: {str(e)}")
        return

    # Create two columns for layout
    main_col, favorites_col = st.columns([2, 1])

    with main_col:
        # Career search
        st.markdown("### Search Careers")
        career_search = st.text_input(
            "Enter a career title or keyword",
            placeholder="e.g., Software Developer, Nurse, Teacher"
        )

        if career_search:
            matching_careers = bls_api.search_occupations(career_search)
            if matching_careers:
                st.markdown("### Matching Careers")
                for career in matching_careers:
                    with st.expander(f"🔍 {career['title']}", expanded=False):
                        show_career_details(career, bls_api)
            else:
                st.info("No matching careers found. Try different keywords.")

    with favorites_col:
        st.markdown("### Your Favorite Careers ⭐")
        favorite_careers = UserFavorites.get_favorite_careers()
        
        if favorite_careers:
            for career in favorite_careers:
                with st.expander(f"⭐ {career['title']}", expanded=False):
                    show_career_details(career, bls_api)
        else:
            st.info("No favorite careers yet. Add some by clicking the star!")

    # Add a back button
    if st.button("← Back to Main Menu"):
        st.session_state.page = 'initial'
        st.rerun()
