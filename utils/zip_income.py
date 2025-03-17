"""Module for handling zip code based income data"""
import pandas as pd
from typing import Optional

def load_zip_income_data(file_path: str = "aggregated_irs_data.csv") -> pd.DataFrame:
    """Load income data by zip code from CSV file"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['zipcode', 'median_household_income', 'mean_household_income']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Income CSV file missing required columns")
        return df
    except Exception as e:
        print(f"Error loading zip code income data: {str(e)}")
        return pd.DataFrame()

def get_income_estimate(zip_code: str) -> Optional[dict]:
    """Get income estimates for a given zip code"""
    try:
        df = load_zip_income_data()
        if df.empty:
            return None

        # Convert zip code to string and pad with zeros if needed
        zip_code = str(zip_code).zfill(5)

        # Find matching zip code
        zip_data = df[df['zipcode'] == zip_code]
        if zip_data.empty:
            return None

        return {
            'median_income': int(zip_data['median_household_income'].iloc[0]),
            'mean_income': int(zip_data['mean_household_income'].iloc[0])
        }
    except Exception as e:
        print(f"Error getting income estimate: {str(e)}")
        return None