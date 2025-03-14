import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from urllib.parse import urlparse

# Get database connection from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Create SQLAlchemy engine
@st.cache_resource
def get_db_engine():
    try:
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return None

# Query function with error handling and proper data conversion
def query_data(sql_query, params=None):
    engine = get_db_engine()
    if engine is None:
        return pd.DataFrame()  # Return empty DataFrame instead of empty list

    try:
        with engine.connect() as conn:
            # Use SQLAlchemy text() to safely handle parameters
            query = text(sql_query)
            result = conn.execute(query, params or {})

            # Convert results to DataFrame directly
            df = pd.DataFrame(result.fetchall())
            if not df.empty:
                df.columns = result.keys()
            return df
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return pd.DataFrame()

# Streamlit app
st.title("Educational Institutions Database Explorer")

# Example: Query and display institutions
st.header("Institutions by State")
state_data = query_data("""
    SELECT state, COUNT(*) as count 
    FROM institutions 
    GROUP BY state 
    ORDER BY count DESC
""")
if not state_data.empty:
    st.dataframe(state_data)
else:
    st.info("No state data available")

# Search functionality with SQL injection prevention
search_term = st.text_input("Search for an institution:")
if search_term:
    results = query_data(
        """
        SELECT i.unitid, i.name, i.city, i.state, 
               d.men, d.women
        FROM institutions i
        LEFT JOIN demographics d ON i.unitid = d.unitid
        WHERE i.name ILIKE :search
        LIMIT 10
        """,
        {"search": f"%{search_term}%"}
    )
    if not results.empty:
        st.dataframe(results)
    else:
        st.info("No results found")