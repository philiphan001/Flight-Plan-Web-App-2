import os
import requests
from typing import List, Dict, Optional
import streamlit as st

class CollegeScorecardAPI:
    BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

    def __init__(self):
        self.api_key = os.environ.get("ED_GOV_API_KEY")
        if not self.api_key:
            raise ValueError("ED_GOV_API_KEY environment variable is not set")

    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def search_colleges(
        _self,  # Changed from self to _self to make it hashable
        query: str = None,
        school_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search colleges using the College Scorecard API

        Args:
            query: Search term (e.g., college name)
            school_type: Type of institution (e.g., '1,2' for 4-year, '3' for 2-year)
            limit: Maximum number of results to return
        """
        params = {
            'api_key': _self.api_key,
            'per_page': limit,
            'fields': ','.join([
                'school.name',
                'school.city',
                'school.state',
                'school.school_url',
                'latest.programs.cip_4_digit',
                'latest.cost.tuition.in_state',
                'latest.cost.tuition.out_of_state',
                'latest.admissions.admission_rate.overall'
            ])
        }

        # Add school type filter if specified
        if school_type:
            params['school.degrees_awarded.predominant'] = school_type

        # Add name search if query provided
        if query:
            params['school.name'] = query

        try:
            response = requests.get(_self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            return [
                {
                    'name': result['school.name'],
                    'city': result.get('school.city', 'N/A'),
                    'state': result.get('school.state', 'N/A'),
                    'website': result.get('school.school_url', ''),
                    'programs': result.get('latest.programs.cip_4_digit', []),
                    'in_state_tuition': result.get('latest.cost.tuition.in_state', 'N/A'),
                    'out_state_tuition': result.get('latest.cost.tuition.out_of_state', 'N/A'),
                    'admission_rate': result.get('latest.admissions.admission_rate.overall', 'N/A')
                }
                for result in data.get('results', [])
            ]
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching college data: {str(e)}")
            return []

    def get_fields_of_study(self, school_id: str) -> List[str]:
        """
        Get available fields of study for a specific school
        """
        params = {
            'api_key': self.api_key,
            'id': school_id,
            'fields': 'latest.programs.cip_4_digit'
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            programs = data.get('results', [{}])[0].get('latest.programs.cip_4_digit', [])
            return [program['title'] for program in programs]
        except requests.exceptions.RequestException:
            return []

    def get_school_type_param(self, type_name: str) -> Optional[str]:
        """
        Convert friendly school type names to API parameters
        """
        type_mapping = {
            "4-Year College/University": "1,2",  # Bachelor's and above
            "Community College": "3",            # Associate's degree
            "Vocational/Trade School": "4",      # Certificates
            "Online Programs": None              # No specific filter for online
        }
        return type_mapping.get(type_name)