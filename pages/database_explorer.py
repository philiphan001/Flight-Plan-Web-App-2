import streamlit as st
import pandas as pd
from utils.database import query_data, init_database

def show_database_explorer():
    st.title("Educational Institutions Database Explorer")
    
    # Initialize database tables
    init_database()
    
    # Create two columns for different queries
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Institutions by State")
        state_data = query_data("""
            SELECT state, COUNT(*) as count 
            FROM institutions 
            GROUP BY state 
            ORDER BY count DESC
        """)
        if state_data:
            st.table(pd.DataFrame(state_data))
        else:
            st.info("No data available. Please add some institutions first.")
    
    with col2:
        st.header("Search Institutions")
        search_term = st.text_input("Search for an institution:")
        if search_term:
            results = query_data("""
                SELECT i.unitid, i.name, i.city, i.state, 
                       d.men, d.women, d.total_enrollment
                FROM institutions i
                LEFT JOIN demographics d ON i.unitid = d.unitid
                WHERE i.name ILIKE %s
                LIMIT 10
            """, (f"%{search_term}%",))
            
            if results:
                st.table(pd.DataFrame(results))
            else:
                st.info("No matching institutions found.")
    
    # Add institution form
    st.header("Add New Institution")
    with st.form("add_institution"):
        name = st.text_input("Institution Name")
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City")
            state = st.text_input("State (2-letter code)", max_chars=2)
        with col2:
            zipcode = st.text_input("Zipcode")
            inst_type = st.selectbox(
                "Institution Type",
                ["Public", "Private", "Community College", "Technical School"]
            )
        
        submit = st.form_submit_button("Add Institution")
        
        if submit and name and city and state:
            conn = get_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO institutions (name, city, state, zipcode, institution_type)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING unitid
                        """, (name, city, state, zipcode, inst_type))
                        conn.commit()
                        st.success("Institution added successfully!")
                except Exception as e:
                    st.error(f"Error adding institution: {str(e)}")
                finally:
                    conn.close()
