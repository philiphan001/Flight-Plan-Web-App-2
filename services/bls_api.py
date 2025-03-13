import os
import requests
from typing import Dict, List, Optional
import streamlit as st
from datetime import datetime

class BLSApi:
    BASE_URL = "https://api.bls.gov/publicAPI/v2"

    def __init__(self):
        self.api_key = os.environ.get("BLS_API_KEY")
        if not self.api_key:
            raise ValueError("BLS_API_KEY environment variable is not set")

    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def get_occupation_data(
        _self,  # Using _self to make it hashable for caching
        occupation_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict:
        """
        Fetch occupation data from BLS API
        
        Args:
            occupation_code: SOC code for the occupation
            start_year: Start year for data (defaults to current year - 1)
            end_year: End year for data (defaults to current year)
        """
        # Set default years if not provided
        current_year = datetime.now().year
        if not end_year:
            end_year = current_year
        if not start_year:
            start_year = end_year - 1

        headers = {'Content-type': 'application/json'}
        data = {
            "seriesid": [f"OEUN{occupation_code}00000000"],
            "startyear": str(start_year),
            "endyear": str(end_year),
            "registrationkey": _self.api_key
        }

        try:
            response = requests.post(f"{_self.BASE_URL}/timeseries/data/", 
                                  json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching BLS data: {str(e)}")
            return {}

    @st.cache_data(ttl=3600)
    def get_salary_by_location(
        _self,
        occupation_code: str,
        area_code: str
    ) -> Dict:
        """
        Get salary data for an occupation in a specific area
        
        Args:
            occupation_code: SOC code for the occupation
            area_code: BLS area code
        """
        headers = {'Content-type': 'application/json'}
        data = {
            "seriesid": [f"OEUM{area_code}{occupation_code}"],
            "registrationkey": _self.api_key
        }

        try:
            response = requests.post(f"{_self.BASE_URL}/timeseries/data/", 
                                  json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching salary data: {str(e)}")
            return {}

    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def search_occupations(
        _self,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search for occupations by keyword
        
        Args:
            query: Search term
            limit: Maximum number of results to return
        """
        # This would typically use the BLS API's occupation search endpoint
        # For now, we'll implement a basic search against common occupations
        common_occupations = {
            "15-1252": "Software Developers",
            "29-1141": "Registered Nurses",
            "13-2011": "Accountants and Auditors",
            "11-1021": "General and Operations Managers",
            "25-2021": "Elementary School Teachers",
            # Add more occupations as needed
        }

        # Simple search implementation
        results = []
        query = query.lower()
        for code, title in common_occupations.items():
            if query in title.lower():
                results.append({
                    "code": code,
                    "title": title
                })
            if len(results) >= limit:
                break

        return results

    def get_employment_projection(
        self,
        occupation_code: str
    ) -> Dict:
        """
        Get employment projections for an occupation
        
        Args:
            occupation_code: SOC code for the occupation
        """
        headers = {'Content-type': 'application/json'}
        data = {
            "seriesid": [f"EP{occupation_code}"],
            "registrationkey": self.api_key
        }

        try:
            response = requests.post(f"{self.BASE_URL}/timeseries/data/", 
                                  json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching employment projections: {str(e)}")
            return {}
