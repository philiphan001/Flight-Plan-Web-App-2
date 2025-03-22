"""Caching utilities for expensive operations"""
import streamlit as st
from typing import Dict, List, Optional, Any
import pandas as pd

@st.cache_data
def process_location_data(_data_processor, coli_df: pd.DataFrame, occupation_df: pd.DataFrame, 
                         location: str, occupation: str, investment_rate: float) -> Dict:
    """
    Cache wrapper for processing location data.
    
    Args:
        _data_processor: DataProcessor instance (underscore prefix to prevent hashing)
        coli_df: Cost of living dataframe
        occupation_df: Occupation data dataframe
        location: Selected location
        occupation: Selected occupation
        investment_rate: Investment return rate
        
    Returns:
        Dict containing processed location data
    """
    return _data_processor.process_location_data(
        coli_df, occupation_df, location, occupation, investment_rate
    )

@st.cache_data
def calculate_yearly_projection(_calculator, years: int) -> Dict:
    """
    Cache wrapper for calculating financial projections.
    
    Args:
        _calculator: FinancialCalculator instance
        years: Number of years to project
        
    Returns:
        Dict containing yearly projections
    """
    return _calculator.calculate_yearly_projection(years)

@st.cache_data
def get_best_matches(query: str, df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """
    Cache wrapper for finding best matches in a dataframe.
    
    Args:
        query: Search query
        df: DataFrame to search in
        n: Number of matches to return
        
    Returns:
        DataFrame containing best matches
    """
    matches = get_close_matches(query.lower(), df.index.str.lower(), n=n, cutoff=0.1)
    return df[df.index.str.lower().isin(matches)] 