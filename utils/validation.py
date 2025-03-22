"""Validation utilities for user inputs"""
from typing import Optional, Tuple, Union
import streamlit as st

def validate_financial_input(value: Union[str, float], 
                           min_value: float = 0, 
                           max_value: float = float('inf')) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validate financial input values.
    
    Args:
        value: Input value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, validated_value, error_message)
    """
    try:
        if isinstance(value, str):
            # Remove currency symbols and commas
            value = value.replace('$', '').replace(',', '')
        
        validated = float(value)
        
        if validated < min_value:
            return False, None, f"Value must be at least {min_value:,.2f}"
        if validated > max_value:
            return False, None, f"Value must be less than {max_value:,.2f}"
            
        return True, validated, None
        
    except ValueError:
        return False, None, "Please enter a valid number"

def validate_percentage(value: Union[str, float], 
                       min_value: float = 0, 
                       max_value: float = 100) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validate percentage inputs.
    
    Args:
        value: Input value to validate
        min_value: Minimum allowed percentage
        max_value: Maximum allowed percentage
        
    Returns:
        Tuple of (is_valid, validated_value, error_message)
    """
    try:
        if isinstance(value, str):
            # Remove percentage symbol
            value = value.replace('%', '')
            
        validated = float(value)
        
        if validated < min_value:
            return False, None, f"Percentage must be at least {min_value}%"
        if validated > max_value:
            return False, None, f"Percentage must be less than {max_value}%"
            
        return True, validated, None
        
    except ValueError:
        return False, None, "Please enter a valid percentage"

def validate_year_input(value: Union[str, int], 
                       min_year: int = 0, 
                       max_year: int = 50) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate year inputs.
    
    Args:
        value: Input value to validate
        min_year: Minimum allowed year
        max_year: Maximum allowed year
        
    Returns:
        Tuple of (is_valid, validated_value, error_message)
    """
    try:
        validated = int(float(value))
        
        if validated < min_year:
            return False, None, f"Year must be at least {min_year}"
        if validated > max_year:
            return False, None, f"Year must be less than {max_year}"
            
        return True, validated, None
        
    except ValueError:
        return False, None, "Please enter a valid year"

def validate_input_with_error(label: str, 
                            key: str, 
                            validation_func, 
                            default_value: Union[str, float, int] = "",
                            **validation_args) -> Optional[Union[float, int]]:
    """
    Streamlit input widget with validation and error display.
    
    Args:
        label: Label for the input widget
        key: Unique key for the input widget
        validation_func: Validation function to use
        default_value: Default value for the input
        **validation_args: Additional arguments for validation function
        
    Returns:
        Validated value if valid, None otherwise
    """
    value = st.text_input(label, value=default_value, key=key)
    
    if value:
        is_valid, validated_value, error_message = validation_func(value, **validation_args)
        if not is_valid:
            st.error(error_message)
            return None
        return validated_value
    return None 