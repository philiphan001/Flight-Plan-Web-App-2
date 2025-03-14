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

                # Sidebar filters
                st.sidebar.header("Search & Filters")

                # State filter
                selected_state = st.sidebar.selectbox("📍 Filter by State", ["All States"] + states)

                # Search box
                search_term = st.sidebar.text_input("🔍 Search Institutions by Name")

                # Gender ratio filter
                gender_filter = st.sidebar.selectbox(
                    "👥 Gender Ratio Filter",
                    ["No Filter", "Women > 50%", "Men > 50%"]
                )

                # Apply filters button
                apply_filters = st.sidebar.button("🔍 Apply Filters")

                if apply_filters:
                    try:
                        # Build query based on filters
                        query = collection_ref

                        # If both search and state filter are active, handle them separately
                        if search_term and selected_state != "All States":
                            # First filter by name
                            name_query = query.order_by('name')
                            name_query = name_query.start_at({'name': search_term}).end_at({'name': search_term + '\uf8ff'})
                            docs = list(name_query.limit(5).stream())  # Limit to top 5 matches

                            # Then filter results by state and gender ratio in memory
                            institutions = []
                            for doc in docs:
                                data = doc.to_dict()
                                if data.get('state') == selected_state:
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
                        else:
                            # Apply filters normally if only one is active
                            if selected_state != "All States":
                                query = query.where('state', '==', selected_state)

                            if search_term:
                                query = query.order_by('name')
                                query = query.start_at({'name': search_term}).end_at({'name': search_term + '\uf8ff'})

                            # Execute query and get results
                            docs = list(query.limit(5).stream())  # Limit to top 5 matches
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

                        # Display results
                        if institutions:
                            df = pd.DataFrame(institutions)
                            st.write(f"Showing {len(df)} institutions")

                            # Calculate and display gender ratios
                            if 'men' in df.columns and 'women' in df.columns:
                                df['women_ratio'] = df['women'] / (df['women'] + df['men'])
                                df['women_ratio'] = df['women_ratio'].apply(lambda x: f"{x:.1%}")

                            # Reorder columns to show important info first
                            display_columns = ['name', 'state', 'city']
                            if 'women_ratio' in df.columns:
                                display_columns.append('women_ratio')

                            # Add any additional columns that exist in the data
                            additional_columns = [col for col in df.columns if col not in display_columns and col not in ['women_ratio']]
                            display_columns.extend(additional_columns)

                            # Display the DataFrame with formatted columns
                            st.dataframe(
                                df[display_columns],
                                column_config={
                                    "name": "Institution Name",
                                    "state": "State",
                                    "city": "City",
                                    "women_ratio": "Women Ratio"
                                }
                            )

                            # Gender distribution if data available
                            if 'men' in df.columns and 'women' in df.columns:
                                st.header("Gender Distribution")
                                st.bar_chart(df[['men', 'women']].mean())

                        else:
                            st.info("No institutions found for the selected criteria")
                            st.sidebar.warning("Try adjusting your filters or search terms")

                    except Exception as query_error:
                        st.error(f"Error executing query: {str(query_error)}")
                        st.exception(query_error)
                else:
                    st.info("Click 'Apply Filters' to see results")
            else:
                st.warning("No states data found in the database")
    else:
        st.error("Firebase is not initialized. Please check your credentials and try again.")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.exception(e)