import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from sqlalchemy import create_engine, text

# Initialize database connection
database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url)

# Database schema for reference
COLUMNS = ['id', 'name', 'city', 'state', 'men', 'women', 'roomboard_oncampus']

# Initialize Firebase with proper error handling
def init_firebase():
    try:
        # Clean up any existing app first
        try:
            existing_app = firebase_admin.get_app('educational-institutions')
            firebase_admin.delete_app(existing_app)
        except ValueError:
            pass  # App doesn't exist, which is fine

        # Now create new app
        cred_json = os.environ.get('FIREBASE_CREDENTIALS')
        if not cred_json:
            st.error("Firebase credentials not found in environment variables")
            return None

        try:
            cred_dict = json.loads(cred_json)

            # Fix private key formatting
            if 'private_key' in cred_dict:
                cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')

            cred = credentials.Certificate(cred_dict)
            firebase_app = firebase_admin.initialize_app(cred, name='educational-institutions')
            st.success(f"Firebase initialized successfully for project: {cred_dict['project_id']}")
            return firebase_app

        except json.JSONDecodeError as je:
            st.error(f"Invalid Firebase credentials JSON format: {str(je)}")
            return None
        except ValueError as ve:
            st.error(f"Invalid Firebase credential values: {str(ve)}")
            return None
        except Exception as e:
            st.error(f"Failed to initialize Firebase: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error accessing Firebase: {str(e)}")
        return None

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

# Initialize PostgreSQL database
init_db()

# Initialize Firebase
firebase_app = init_firebase()

# App title
st.title("Educational Institutions Explorer")

# Sidebar filters
st.sidebar.header("Filters")

try:
    # Get states data from both sources
    states = []

    # Get states from PostgreSQL
    with engine.connect() as conn:
        states_query = text("""
            SELECT DISTINCT state 
            FROM institutions 
            WHERE state IS NOT NULL 
            ORDER BY state
        """)
        pg_states = [row[0] for row in conn.execute(states_query)]
        states.extend(pg_states)

    # Get states from Firebase if available
    if firebase_app:
        db = firestore.client(app=firebase_app)
        fb_states_query = db.collection('institutions').select(['state']).stream()
        fb_states = [doc.to_dict().get('state') for doc in fb_states_query if doc.to_dict().get('state')]
        states.extend(fb_states)

    # Remove duplicates and sort
    states = sorted(list(set(filter(None, states))))

    # State filter
    selected_state = st.sidebar.selectbox("Select State", ["All States"] + states)

    # Initialize empty DataFrame
    df = pd.DataFrame(columns=COLUMNS)

    # Get data based on filters
    if selected_state == "All States":
        # Get PostgreSQL data
        with engine.connect() as conn:
            query = text(f"""
                SELECT {', '.join(COLUMNS)}
                FROM institutions 
                LIMIT 100
            """)
            pg_institutions = conn.execute(query).fetchall()
            pg_df = pd.DataFrame(pg_institutions, columns=COLUMNS)
            df = pd.concat([df, pg_df], ignore_index=True)

        # Get Firebase data if available
        if firebase_app:
            fb_query = db.collection('institutions').limit(100)
            docs = list(fb_query.stream())
            fb_institutions = [doc.to_dict() for doc in docs]
            if fb_institutions:
                fb_df = pd.DataFrame(fb_institutions)
                # Ensure Firebase data matches our schema
                fb_df = fb_df[fb_df.columns.intersection(COLUMNS)]
                df = pd.concat([df, fb_df], ignore_index=True)
    else:
        # Get PostgreSQL data
        with engine.connect() as conn:
            query = text(f"""
                SELECT {', '.join(COLUMNS)}
                FROM institutions 
                WHERE state = :state
            """)
            pg_institutions = conn.execute(query, {"state": selected_state}).fetchall()
            pg_df = pd.DataFrame(pg_institutions, columns=COLUMNS)
            df = pd.concat([df, pg_df], ignore_index=True)

        # Get Firebase data if available
        if firebase_app:
            fb_query = db.collection('institutions').where('state', '==', selected_state)
            docs = list(fb_query.stream())
            fb_institutions = [doc.to_dict() for doc in docs]
            if fb_institutions:
                fb_df = pd.DataFrame(fb_institutions)
                # Ensure Firebase data matches our schema
                fb_df = fb_df[fb_df.columns.intersection(COLUMNS)]
                df = pd.concat([df, fb_df], ignore_index=True)

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
        search_results = []

        # Search in PostgreSQL
        with engine.connect() as conn:
            search_query = text(f"""
                SELECT {', '.join(COLUMNS)}
                FROM institutions 
                WHERE name ILIKE :search_term 
                LIMIT 10
            """)
            pg_results = conn.execute(search_query, {"search_term": f"%{search_term}%"}).fetchall()
            if pg_results:
                search_results.extend([dict(zip(COLUMNS, row)) for row in pg_results])

        # Search in Firebase if available
        if firebase_app:
            results = db.collection('institutions').order_by('name').start_at({
                'name': search_term
            }).end_at({
                'name': search_term + '\uf8ff'
            }).stream()
            fb_results = [doc.to_dict() for doc in results]
            if fb_results:
                # Ensure Firebase search results match our schema
                fb_results = [{k: v for k, v in result.items() if k in COLUMNS} for result in fb_results]
                search_results.extend(fb_results)

        if search_results:
            search_df = pd.DataFrame(search_results)
            st.dataframe(search_df[['name', 'city', 'state']])
        else:
            st.write("No matching institutions found.")

except Exception as e:
    st.error(f"Database error: {str(e)}")