"""Module for handling zip code based income data"""
import pandas as pd
from typing import Optional

def load_zip_income_data(file_path: str = "aggregated_irs_data.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        required_columns = ['Cost of Living', 'Housing', 'Transportation', 'Food', 'Healthcare', 
                              'Personal Insurance', 'Apparel', 'Services', 'Entertainment', 'Other',
                              'Monthly Expense', 'Income Adjustment Factor', 'Average Price of Starter Home', 'zipcode', 'Mean Income'] #Added zipcode and Mean Income to required columns
        if not all(col in df.columns for col in required_columns):
            raise ValueError("COLI CSV file missing required columns")
        return df
    except Exception as e:
        raise Exception(f"Error loading COLI data: {str(e)}")

def get_income_estimate(zip_code: str) -> Optional[dict]:
    """Get income estimates for a given zip code"""
    try:
        df = load_zip_income_data()
        if df.empty:
            return None

        # Convert zip code to string and pad with zeros if needed
        zip_code = str(zip_code).zfill(5)

        # Find matching zip code
        zip_data = df[df['zipcode'] == int(zip_code)]
        if zip_data.empty:
            print(f"No data found for ZIP code: {zip_code}")
            return None

        # Only use Mean Income from CSV
        mean_income = float(zip_data['Mean Income'].iloc[0])

        return {
            'mean_income': int(mean_income)
        }
    except Exception as e:
        print(f"Error getting income estimate: {str(e)}")
        return None