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

try:
    if firebase_app:
        # Initialize Firestore client
        db = firestore.client(app=firebase_app)
        st.success("Connected to Firestore database")

        # Debug: Check if collection exists
        collection_ref = db.collection('institutions')
        st.info("Attempting to access institutions collection...")

        # Test query to check data
        test_docs = list(collection_ref.limit(1).stream())
        if not test_docs:
            st.warning("No data found in the institutions collection. The database appears to be empty.")
            st.info("Please add some data to the institutions collection in Firebase.")
        else:
            st.success(f"Successfully accessed institutions collection. Found data.")

            # Sidebar filters
            st.sidebar.header("Search & Filters")

            # Search box in sidebar
            search_term = st.sidebar.text_input("🔍 Search Institutions by Name")

            # Get unique states
            states = []
            states_query = collection_ref.select(['state']).stream()
            for doc in states_query:
                state = doc.to_dict().get('state')
                if state:
                    states.append(state)

            states = sorted(list(set(states)))
            if states:
                st.success(f"Found {len(states)} states in the database")

                # State filter
                selected_state = st.sidebar.selectbox("📍 Filter by State", ["All States"] + states)

                # Build query
                if selected_state != "All States":
                    docs = list(collection_ref.where('state', '==', selected_state).limit(100).stream())
                else:
                    docs = list(collection_ref.limit(100).stream())

                # Process results
                if docs:
                    institutions = [doc.to_dict() for doc in docs]
                    df = pd.DataFrame(institutions)

                    # Display results
                    st.write(f"Showing {len(df)} institutions")
                    st.dataframe(df)

                    # Gender distribution if data available
                    if 'men' in df.columns and 'women' in df.columns:
                        st.header("Gender Distribution")
                        st.bar_chart(df[['men', 'women']].mean())
                else:
                    st.info("No institutions found for the selected criteria")
            else:
                st.warning("No states data found in the database")
    else:
        st.error("Firebase is not initialized. Please check your credentials and try again.")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.exception(e)

# Columns we expect in our data
COLUMNS = ['id', 'name', 'city', 'state', 'men', 'women', 'roomboard_oncampus']