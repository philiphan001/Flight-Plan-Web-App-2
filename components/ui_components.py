"""UI components for the financial planning application"""
import streamlit as st
from typing import List, Dict, Optional
import pandas as pd
from difflib import get_close_matches
from utils.validation import validate_input_with_error, validate_financial_input, validate_percentage
from utils.cache_utils import process_location_data
from models.milestone_factory import MilestoneFactory, Milestone

def render_location_selection(locations: List[str]) -> Optional[str]:
    """
    Render the location selection component.
    
    Args:
        locations: List of available locations
        
    Returns:
        Selected location if one is chosen, None otherwise
    """
    st.markdown("### Select Your Location 📍")
    
    if st.session_state.selected_location and st.session_state.selected_location != "":
        st.markdown(f"**Selected Location:** {st.session_state.selected_location}")
        return st.session_state.selected_location
        
    location_input = st.text_input("Enter Location")
    if location_input:
        matches = get_close_matches(location_input.lower(),
                                   [loc.lower() for loc in locations],
                                   n=3, cutoff=0.1)
        matching_locations = [loc for loc in locations if loc.lower() in matches]
        if matching_locations:
            cols = st.columns(3)
            for idx, loc in enumerate(matching_locations):
                with cols[idx]:
                    if st.button(f"📍 {loc}", key=f"loc_{loc}"):
                        return loc
    return None

def render_occupation_selection(occupations: List[str]) -> Optional[str]:
    """
    Render the occupation selection component.
    
    Args:
        occupations: List of available occupations
        
    Returns:
        Selected occupation if one is chosen, None otherwise
    """
    st.markdown("### Select Your Occupation 💼")
    
    if st.session_state.selected_occupation and st.session_state.selected_occupation != "":
        st.markdown(f"**Selected Occupation:** {st.session_state.selected_occupation}")
        return st.session_state.selected_occupation
        
    occupation_input = st.text_input("Enter Occupation")
    if occupation_input:
        matches = get_close_matches(occupation_input.lower(),
                                   [occ.lower() for occ in occupations],
                                   n=3, cutoff=0.1)
        matching_occupations = [occ for occ in occupations if occ.lower() in matches]
        if matching_occupations:
            cols = st.columns(3)
            for idx, occ in enumerate(matching_occupations):
                with cols[idx]:
                    if st.button(f"💼 {occ}", key=f"occ_{occ}"):
                        return occ
    return None

def render_milestone_form(milestone_type: str) -> Optional[Dict]:
    """
    Render a form for adding a new milestone.
    
    Args:
        milestone_type: Type of milestone to add
        
    Returns:
        Dictionary of milestone data if form is submitted, None otherwise
    """
    with st.form(f"milestone_form_{milestone_type}"):
        st.subheader(f"Add {milestone_type} Milestone")
        
        # Common fields
        year = validate_input_with_error(
            "Year", 
            f"year_{milestone_type}", 
            validate_year_input,
            min_year=0,
            max_year=30
        )
        
        # Milestone-specific fields
        data = {"type": milestone_type, "year": year}
        
        if milestone_type == "Marriage":
            data["wedding_cost"] = validate_input_with_error(
                "Wedding Cost ($)", 
                "wedding_cost", 
                validate_financial_input,
                min_value=0,
                max_value=1000000
            )
            data["joint_lifestyle_adjustment"] = validate_input_with_error(
                "Joint Lifestyle Adjustment (%)", 
                "lifestyle_adj", 
                validate_percentage
            )
            
        elif milestone_type == "Home":
            data["home_cost"] = validate_input_with_error(
                "Home Cost ($)", 
                "home_cost", 
                validate_financial_input,
                min_value=0,
                max_value=10000000
            )
            data["down_payment"] = validate_input_with_error(
                "Down Payment (%)", 
                "down_payment", 
                validate_percentage
            )
            
        elif milestone_type == "Education":
            data["total_cost"] = validate_input_with_error(
                "Total Cost ($)", 
                "education_cost", 
                validate_financial_input,
                min_value=0,
                max_value=500000
            )
            data["program_years"] = validate_input_with_error(
                "Program Length (years)", 
                "program_years", 
                validate_year_input,
                min_year=1,
                max_year=10
            )
            
        submitted = st.form_submit_button("Add Milestone")
        
        if submitted and all(v is not None for v in data.values()):
            return data
            
    return None

def render_financial_controls() -> Dict:
    """
    Render financial control inputs.
    
    Returns:
        Dictionary containing financial control values
    """
    col1, col2 = st.columns(2)
    
    with col1:
        investment_return_rate = st.slider(
            "Investment Return Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=7.0,
            step=0.5,
            key="investment_rate"
        ) / 100.0
        
    with col2:
        projection_years = st.slider(
            "Projection Years",
            1, 30, 10,
            key="projection_years"
        )
        
    return {
        "investment_return_rate": investment_return_rate,
        "projection_years": projection_years
    }

def render_milestone_list(milestones: List[Dict]) -> None:
    """
    Render the list of current milestones.
    
    Args:
        milestones: List of milestone dictionaries
    """
    if not milestones:
        st.info("No milestones added yet.")
        return
        
    for idx, milestone in enumerate(milestones):
        with st.expander(f"{milestone['type']} - Year {milestone['year']}"):
            for key, value in milestone.items():
                if key not in ['type', 'year']:
                    st.write(f"{key.replace('_', ' ').title()}: {value}")
            if st.button("Remove", key=f"remove_milestone_{idx}"):
                milestones.pop(idx)
                st.session_state.needs_recalculation = True
                st.rerun() 