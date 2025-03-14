import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
conn_params = {
    'dbname': 'educational_institutions',
    'user': 'postgres',
    'password': 'Bobbib00$',
    'host': 'localhost',
    'port': '5432'
}

# Create a connection function
def get_connection():
    conn = psycopg2.connect(**conn_params)
    return conn

# Example query function
def query_data(sql):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            data = cur.fetchall()
            return data
    finally:
        conn.close()

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
st.table(pd.DataFrame(state_data))

# Another example: Search for institutions
search_term = st.text_input("Search for an institution:")
if search_term:
    results = query_data(f"""
        SELECT i.unitid, i.name, i.city, i.state, 
               d.men, d.women
        FROM institutions i
        LEFT JOIN demographics d ON i.unitid = d.unitid
        WHERE i.name ILIKE '%{search_term}%'
        LIMIT 10
    """)
    st.table(pd.DataFrame(results))
    