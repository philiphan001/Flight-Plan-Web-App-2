import streamlit as st
import pandas as pd
import os

def main():
    st.title("CSV File Diagnostic")

    # Test file existence first
    st.subheader("Checking CSV Files")

    files_to_check = ["COLI by Location.csv", "Occupational Data.csv"]

    for file_name in files_to_check:
        if os.path.exists(file_name):
            st.success(f"✅ {file_name} exists")
            try:
                df = pd.read_csv(file_name)
                st.write(f"Columns in {file_name}:", df.columns.tolist())
                st.write(f"First few rows of {file_name}:")
                st.dataframe(df.head())
            except Exception as e:
                st.error(f"❌ Error reading {file_name}: {str(e)}")
        else:
            st.error(f"❌ {file_name} not found")
            st.write(f"Current directory contents:", os.listdir())

if __name__ == "__main__":
    main()