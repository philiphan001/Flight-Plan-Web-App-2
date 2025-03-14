import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text

# Initialize database connection
database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url)

# App title
st.title("Educational Institutions Explorer")

# Initialize database table if it doesn't exist
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS institutions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                city VARCHAR(255),
                state VARCHAR(255),
                men INTEGER,
                women INTEGER,
                roomboard_oncampus NUMERIC
            )
        """))
        conn.commit()

# Initialize database
init_db()

# Sidebar filters
st.sidebar.header("Filters")

try:
    # Get all states for filter
    with engine.connect() as conn:
        states_query = text("SELECT DISTINCT state FROM institutions WHERE state IS NOT NULL ORDER BY state")
        states = [row[0] for row in conn.execute(states_query)]

    # State filter
    selected_state = st.sidebar.selectbox("Select State", ["All States"] + states)

    # Get data based on filters
    with engine.connect() as conn:
        if selected_state == "All States":
            query = text("SELECT * FROM institutions LIMIT 100")  # Limit for performance
            institutions = conn.execute(query).fetchall()
        else:
            query = text("SELECT * FROM institutions WHERE state = :state")
            institutions = conn.execute(query, {"state": selected_state}).fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(institutions, columns=['id', 'name', 'city', 'state', 'men', 'women', 'roomboard_oncampus'])

        if not df.empty:
            # Display count
            st.write(f"Showing {len(df)} institutions")

            # Display data table
            st.dataframe(df[['name', 'city', 'state', 'men', 'women', 'roomboard_oncampus']])

            # Add visualizations
            if len(df) > 0 and 'men' in df.columns and 'women' in df.columns:
                st.header("Gender Distribution")
                st.bar_chart(df[['men', 'women']].mean())
        else:
            st.write("No data found for the selected filters.")

        # Search functionality
        st.header("Search Institutions")
        search_term = st.text_input("Enter institution name:")

        if search_term:
            search_query = text("""
                SELECT * FROM institutions 
                WHERE name ILIKE :search_term 
                LIMIT 10
            """)
            search_results = conn.execute(search_query, 
                {"search_term": f"%{search_term}%"}
            ).fetchall()

            search_df = pd.DataFrame(search_results, 
                columns=['id', 'name', 'city', 'state', 'men', 'women', 'roomboard_oncampus'])

            if not search_df.empty:
                st.dataframe(search_df[['name', 'city', 'state']])
            else:
                st.write("No matching institutions found.")

except Exception as e:
    st.error(f"Database error: {str(e)}")