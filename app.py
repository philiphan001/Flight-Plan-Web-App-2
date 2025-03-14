import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from difflib import SequenceMatcher

def string_similarity(a, b):
    """Calculate string similarity ratio"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

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

                # Create two columns for search and filters
                search_col, filter_col = st.columns(2)

                with search_col:
                    st.header("🔍 Search Institutions")
                    search_term = st.text_input("Enter institution name:")
                    search_button = st.button("Search")

                    if search_button and search_term:
                        # Get all institutions first (limited to a reasonable number)
                        all_docs = list(collection_ref.limit(100).stream())
                        search_results = []

                        # Score each institution based on name similarity
                        for doc in all_docs:
                            data = doc.to_dict()
                            name = data.get('name', '')
                            if name:
                                similarity = string_similarity(search_term, name)
                                if similarity > 0.3:  # Minimum similarity threshold
                                    search_results.append((similarity, data))

                        # Sort by similarity score and take top 5
                        search_results.sort(reverse=True, key=lambda x: x[0])
                        top_results = [data for score, data in search_results[:5]]

                        if top_results:
                            st.success(f"Found {len(top_results)} matching institutions")
                            df = pd.DataFrame(top_results)
                            st.dataframe(
                                df[['name', 'state', 'city']],
                                column_config={
                                    "name": "Institution Name",
                                    "state": "State",
                                    "city": "City"
                                }
                            )
                        else:
                            st.info("No matching institutions found")

                with filter_col:
                    st.header("🎯 Filter Institutions")
                    # State filter
                    selected_state = st.selectbox("Filter by State", ["All States"] + states)

                    # Gender ratio filter
                    gender_filter = st.selectbox(
                        "Gender Ratio Filter",
                        ["No Filter", "Women > 50%", "Men > 50%"]
                    )

                    apply_filters = st.button("Apply Filters")

                    if apply_filters:
                        # Build query based on filters
                        query = collection_ref

                        if selected_state != "All States":
                            query = query.where('state', '==', selected_state)

                        # Execute query
                        docs = list(query.limit(100).stream())

                        if docs:
                            institutions = []
                            for doc in docs:
                                data = doc.to_dict()
                                # Apply gender ratio filter
                                men = float(data.get('men', 0))
                                women = float(data.get('women', 0))
                                total = men + women
                                if total > 0:  # Avoid division by zero
                                    women_ratio = women / total
                                    if (gender_filter == "Women > 50%" and women_ratio > 0.5) or \
                                       (gender_filter == "Men > 50%" and women_ratio < 0.5) or \
                                       (gender_filter == "No Filter"):
                                        institutions.append(data)

                            if institutions:
                                df = pd.DataFrame(institutions)

                                # Calculate women ratio
                                if 'men' in df.columns and 'women' in df.columns:
                                    df['women_ratio'] = df['women'] / (df['women'] + df['men'])
                                    df['women_ratio'] = df['women_ratio'].apply(lambda x: f"{x:.1%}")

                                st.success(f"Found {len(df)} institutions matching your criteria")

                                # Display results
                                display_columns = ['name', 'state', 'city', 'women_ratio'] if 'women_ratio' in df.columns else ['name', 'state', 'city']
                                st.dataframe(
                                    df[display_columns],
                                    column_config={
                                        "name": "Institution Name",
                                        "state": "State",
                                        "city": "City",
                                        "women_ratio": "Women Ratio"
                                    }
                                )

                                # Gender distribution visualization
                                if 'men' in df.columns and 'women' in df.columns:
                                    st.header("Gender Distribution")
                                    st.bar_chart(df[['men', 'women']].mean())
                            else:
                                st.info("No institutions found matching your criteria")
                        else:
                            st.info("No institutions found matching your criteria")

            else:
                st.warning("No states data found in the database")
    else:
        st.error("Firebase is not initialized. Please check your credentials and try again.")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.exception(e)