import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

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

# Initialize Firebase
firebase_app = init_firebase()

# App title
st.title("Educational Institutions Explorer")

# Columns we expect in our data
COLUMNS = ['id', 'name', 'city', 'state', 'men', 'women', 'roomboard_oncampus']

try:
    if firebase_app:
        # Initialize Firestore client
        db = firestore.client(app=firebase_app)

        # Sidebar filters
        st.sidebar.header("Search & Filters")

        # Search box in sidebar
        search_term = st.sidebar.text_input("🔍 Search Institutions by Name")

        try:
            # Get all states for filter
            st.info("Loading states data...")
            states_query = db.collection('institutions').select(['state']).stream()
            states = sorted(list(set(doc.to_dict().get('state') for doc in states_query if doc.to_dict().get('state'))))

            if not states:
                st.warning("No states data found in the database. Please check if there are any institutions in the database.")
                states = []
        except Exception as e:
            st.error(f"Error loading states: {str(e)}")
            states = []

        # State filter
        selected_state = st.sidebar.selectbox("📍 Filter by State", ["All States"] + states)

        # Show loading message
        st.info("Loading institutions data...")

        try:
            # Initialize query based on filters
            query = db.collection('institutions')

            # Apply state filter if selected
            if selected_state != "All States":
                query = query.where('state', '==', selected_state)
                st.sidebar.info(f"Filtering by state: {selected_state}")

            # Apply search if entered
            if search_term:
                query = query.order_by('name').start_at({
                    'name': search_term
                }).end_at({
                    'name': search_term + '\uf8ff'
                })
                st.sidebar.info(f"Searching for: {search_term}")

            # Execute query with limit
            docs = list(query.limit(100).stream())

            if docs:
                st.success(f"Found {len(docs)} institutions")
                institutions = [doc.to_dict() for doc in docs]

                # Convert to DataFrame
                df = pd.DataFrame(institutions)

                # Ensure we only use columns we expect
                available_columns = df.columns.intersection(COLUMNS)
                if len(available_columns) < len(COLUMNS):
                    missing_columns = set(COLUMNS) - set(available_columns)
                    st.warning(f"Some expected columns are missing: {', '.join(missing_columns)}")

                df = df[available_columns]

                # Display data table
                st.dataframe(df)

                # Add visualizations if we have gender data
                if 'men' in df.columns and 'women' in df.columns:
                    st.header("Gender Distribution")
                    st.bar_chart(df[['men', 'women']].mean())
            else:
                st.warning("No institutions found matching your criteria")
                st.sidebar.info("Try adjusting your filters or search terms")

        except Exception as e:
            st.error(f"Error querying institutions: {str(e)}")
            st.exception(e)  # This will show the full error trace

    else:
        st.error("Firebase is not initialized. Please check your credentials and try again.")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.exception(e)  # This will show the full error trace