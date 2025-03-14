import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from difflib import SequenceMatcher

def string_similarity(search_term, institution_name):
    """Enhanced string similarity matching with sophisticated scoring"""
    search_term = search_term.lower()
    institution_name = institution_name.lower()

    # Direct match gets highest score
    if search_term == institution_name:
        return 1.0

    # Split institution name into words
    name_words = institution_name.split()
    search_words = search_term.split()

    # Check for exact word matches at the start of name
    if any(name_words[0].startswith(search_word) for search_word in search_words):
        return 0.98  # Extremely high score for matches at start

    # Check for exact word matches anywhere
    if any(search_word in name_words for search_word in search_words):
        return 0.95  # Very high score for exact word match

    # Check common institution name patterns
    patterns = [
        f"{search_term} university",
        f"university of {search_term}",
        f"{search_term} college",
        f"college of {search_term}"
    ]
    if any(pattern in institution_name for pattern in patterns):
        return 0.9

    # Use sequence matcher for fuzzy matching of each word
    max_word_ratio = max(
        SequenceMatcher(None, search_word, name_word).ratio()
        for search_word in search_words
        for name_word in name_words
    )

    # Boost score if any word starts with search term
    if any(word.startswith(search_term) for word in name_words):
        max_word_ratio += 0.2

    return max_word_ratio

def init_firebase():
    try:
        # Clean up existing default app if it exists
        try:
            default_app = firebase_admin.get_app()
            firebase_admin.delete_app(default_app)
        except ValueError:
            pass

        # Get credentials from environment
        cred_json = os.environ.get('FIREBASE_CREDENTIALS')
        if not cred_json:
            st.error("Firebase credentials not found in environment variables")
            return None

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
                        # Get all documents for searching
                        all_docs = list(collection_ref.stream())
                        search_results = []

                        # Score each institution based on enhanced name similarity
                        for doc in all_docs:
                            data = doc.to_dict()
                            name = data.get('name', '')
                            if name:
                                similarity = string_similarity(search_term, name)
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