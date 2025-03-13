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
        if career_data not in st.session_state.favorite_careers:
            st.session_state.favorite_careers.append(career_data)

    @staticmethod
    def remove_favorite_career(career_data: Dict):
        """Remove a career from favorites"""
        if career_data in st.session_state.favorite_careers:
            st.session_state.favorite_careers.remove(career_data)

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
        return career_data in st.session_state.favorite_careers

    @staticmethod
    def is_favorite_school(school_data: Dict) -> bool:
        """Check if a school is in favorites"""
        return school_data in st.session_state.favorite_schools
