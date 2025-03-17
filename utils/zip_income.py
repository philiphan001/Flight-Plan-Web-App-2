"""Module for handling zip code based income data"""
import pandas as pd
from typing import Optional

def load_zip_income_data(file_path: str = "aggregated_irs_data.csv") -> pd.DataFrame:
    """Load income data by zip code from CSV file"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['zipcode', 'Number of returns', 'Total income amount', 'Mean Income']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Income CSV file missing required columns")

        # Clean up the 'Mean Income' column by removing commas and dollar signs
        df['Mean Income'] = df['Mean Income'].str.replace('$', '').str.replace(',', '').str.replace(' ', '').astype(float)

        # Clean up the 'Total income amount' column
        df['Total income amount'] = df['Total income amount'].str.replace('$', '').str.replace(',', '').str.replace(' ', '').astype(float)

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
        zip_data = df[df['zipcode'] == int(zip_code)]
        if zip_data.empty:
            print(f"No data found for ZIP code: {zip_code}")
            return None

        # Calculate average household income from total income and number of returns
        mean_income = float(zip_data['Mean Income'].iloc[0])
        total_income = float(zip_data['Total income amount'].iloc[0])
        num_returns = float(zip_data['Number of returns'].iloc[0])
        calculated_mean = total_income / num_returns if num_returns > 0 else 0

        return {
            'median_income': int(mean_income),  # Using mean as proxy since median isn't available
            'mean_income': int(calculated_mean)
        }
    except Exception as e:
        print(f"Error getting income estimate: {str(e)}")
        return None