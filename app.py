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

        # Get all states for filter
        states_query = db.collection('institutions').select(['state']).stream()
        states = sorted(list(set(doc.to_dict().get('state') for doc in states_query if doc.to_dict().get('state'))))

        # State filter
        selected_state = st.sidebar.selectbox("📍 Filter by State", ["All States"] + states)

        # Initialize query based on filters
        query = db.collection('institutions')

        # Apply state filter if selected
        if selected_state != "All States":
            query = query.where('state', '==', selected_state)
            st.sidebar.info(f"Showing institutions in {selected_state}")

        # Apply search if entered
        if search_term:
            query = query.order_by('name').start_at({
                'name': search_term
            }).end_at({
                'name': search_term + '\uf8ff'
            })
            st.sidebar.info(f"Searching for: {search_term}")

        # Limit results for performance
        query = query.limit(100)

        # Execute query
        docs = list(query.stream())
        institutions = [doc.to_dict() for doc in docs]

        if institutions:
            # Convert to DataFrame
            df = pd.DataFrame(institutions)

            # Ensure we only use columns we expect
            df = df[df.columns.intersection(COLUMNS)]

            # Display count
            st.write(f"Showing {len(df)} institutions")

            # Display data table
            st.dataframe(df[['name', 'city', 'state', 'men', 'women', 'roomboard_oncampus']])

            # Add visualizations
            if len(df) > 0 and 'men' in df.columns and 'women' in df.columns:
                st.header("Gender Distribution")
                st.bar_chart(df[['men', 'women']].mean())
        else:
            st.info("No institutions found matching your search criteria")
            st.sidebar.warning("Try adjusting your filters or search terms")

    else:
        st.error("Firebase is not initialized. Please check your credentials and try again.")

except Exception as e:
    st.error(f"Error: {str(e)}")