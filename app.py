import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def init_firebase():
    try:
        # Clean up existing default app if it exists
        try:
            default_app = firebase_admin.get_app()
            firebase_admin.delete_app(default_app)
        except ValueError:
            # No default app exists
            pass

        # Get credentials from environment
        cred_json = os.environ.get('FIREBASE_CREDENTIALS')
        if not cred_json:
            st.error("Firebase credentials not found in environment variables")
            return None

        # Initialize Firebase with default app
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_app = firebase_admin.initialize_app(cred)
        st.success(f"Firebase initialized successfully for project: {cred_dict['project_id']}")
        return firebase_app

    except Exception as e:
        st.error(f"Error in Firebase initialization: {str(e)}")
        return None

# App title
st.title("Educational Institutions Explorer")

try:
    # Initialize Firebase
    firebase_app = init_firebase()

    if firebase_app:
        # Initialize Firestore client
        db = firestore.client()
        st.success("Connected to Firestore database")

        # Sidebar filters
        st.sidebar.header("Search & Filters")

        # Search box in sidebar
        search_term = st.sidebar.text_input("🔍 Search Institutions by Name")

        # Check if collection exists and has data
        collection_ref = db.collection('institutions')
        test_docs = list(collection_ref.limit(1).stream())

        if not test_docs:
            st.warning("No data found in the institutions collection. Please add some data to Firebase first.")
        else:
            # Get unique states
            states_query = collection_ref.select(['state']).stream()
            states = []
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
                query = collection_ref
                if selected_state != "All States":
                    query = query.where('state', '==', selected_state)

                # Apply search if entered
                if search_term:
                    query = query.order_by('name').start_at({
                        'name': search_term
                    }).end_at({
                        'name': search_term + '\uf8ff'
                    })

                # Execute query
                docs = list(query.limit(100).stream())

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

# COLUMNS = ['id', 'name', 'city', 'state', 'men', 'women', 'roomboard_oncampus'] #This line is not needed here.