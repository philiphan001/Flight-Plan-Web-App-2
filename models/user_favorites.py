"""User favorites management module"""
import streamlit as st
from typing import Dict, List, Optional

class UserFavorites:
    @staticmethod
    def init_session_state():
        """Initialize session state for favorites"""
        if 'favorite_careers' not in st.session_state:
            st.session_state.favorite_careers = []
        if 'favorite_schools' not in st.session_state:
            st.session_state.favorite_schools = []

    @staticmethod
    def add_favorite_career(career_data: Dict):
        """Add a career to favorites"""
        # Convert Pandas Series to dict if needed
        if hasattr(career_data, 'to_dict'):
            career_dict = career_data.to_dict()
        else:
            career_dict = career_data
            
        # Only add if not already in favorites
        if not UserFavorites.is_favorite_career(career_data):
            st.session_state.favorite_careers.append(career_dict)

    @staticmethod
    def remove_favorite_career(career_data: Dict):
        """Remove a career from favorites"""
        career_title = career_data['OCC_TITLE']
        # Find and remove the career with matching title
        st.session_state.favorite_careers = [
            fav for fav in st.session_state.favorite_careers 
            if fav['OCC_TITLE'] != career_title
        ]

    @staticmethod
    def add_favorite_school(school_data: Dict):
        """Add a school to favorites"""
        if school_data not in st.session_state.favorite_schools:
            st.session_state.favorite_schools.append(school_data)

    @staticmethod
    def remove_favorite_school(school_data: Dict):
        """Remove a school from favorites"""
        if school_data in st.session_state.favorite_schools:
            st.session_state.favorite_schools.remove(school_data)

    @staticmethod
    def get_favorite_careers() -> List[Dict]:
        """Get all favorite careers"""
        return st.session_state.favorite_careers

    @staticmethod
    def get_favorite_schools() -> List[Dict]:
        """Get all favorite schools"""
        return st.session_state.favorite_schools

    @staticmethod
    def is_favorite_career(career_data: Dict) -> bool:
        """Check if a career is in favorites"""
        # Compare by occupation title since we're dealing with Pandas Series objects
        career_title = career_data['OCC_TITLE']
        return any(fav['OCC_TITLE'] == career_title for fav in st.session_state.favorite_careers)

    @staticmethod
    def is_favorite_school(school_data: Dict) -> bool:
        """Check if a school is in favorites"""
        return school_data in st.session_state.favorite_schools
