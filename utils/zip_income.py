"""Module for handling zip code based income data"""
import pandas as pd
from typing import Optional

def load_zip_income_data(file_path: str = "aggregated_irs_data.csv") -> pd.DataFrame:
    """Load income data by zip code from CSV file"""
    try:
        df = pd.read_csv(file_path)

        # Clean up column names by stripping whitespace
        df.columns = df.columns.str.strip()

        required_columns = ['zipcode', 'Mean Income']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Income CSV file missing required columns")

        # Clean up the 'Mean Income' column by removing formatting
        df['Mean Income'] = df['Mean Income'].str.replace('$', '').str.replace(',', '').str.replace(' ', '').astype(float)

        return df
    except Exception as e:
        print(f"Error loading income data: {str(e)}")
        return None

def get_income_estimate(zip_code: str) -> Optional[dict]:
    """Get income estimates for a given zip code"""
    try:
        df = load_zip_income_data()
        if df is None or df.empty:
            return None

        # Convert zip code to integer for comparison
        zip_code = int(zip_code)

        # Find matching zip code
        zip_data = df[df['zipcode'] == zip_code]
        if zip_data.empty:
            print(f"No data found for ZIP code: {zip_code}")
            return None

        # Get mean income 
        mean_income = float(zip_data['Mean Income'].iloc[0])

        return {
            'mean_income': int(mean_income)
        }
    except Exception as e:
        print(f"Error getting income estimate: {str(e)}")
        return None