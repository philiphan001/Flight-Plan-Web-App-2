import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Initialize Firebase with proper error handling
def init_firebase():
    try:
        # Try to get existing app first
        try:
            return firebase_admin.get_app('educational-institutions')
        except ValueError:
            # App doesn't exist, create new one
            cred_json = os.environ.get('FIREBASE_CREDENTIALS')
            if not cred_json:
                st.error("Firebase credentials not found in environment variables")
                return None

            try:
                cred_dict = json.loads(cred_json)

                # Validate required fields in credentials
                required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
                missing_fields = [field for field in required_fields if field not in cred_dict]

                if missing_fields:
                    st.error(f"Firebase credentials missing required fields: {', '.join(missing_fields)}")
                    return None

                # Fix private key formatting
                if 'private_key' in cred_dict:
                    cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')

                # Log non-sensitive credential info for debugging
                st.info(f"Firebase credentials loaded with keys: {', '.join(cred_dict.keys())}")
                st.info(f"Project ID: {cred_dict.get('project_id')}")
                st.info(f"Client Email: {cred_dict.get('client_email')}")

                # Extra validation for OAuth2 fields
                oauth2_fields = ['client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url']
                missing_oauth2 = [field for field in oauth2_fields if field not in cred_dict]
                if missing_oauth2:
                    st.warning(f"Some optional OAuth2 fields are missing: {', '.join(missing_oauth2)}")

                # Verify credential type
                if cred_dict.get('type') != 'service_account':
                    st.error("Invalid credential type. Must be 'service_account'")
                    return None

                cred = credentials.Certificate(cred_dict)
                return firebase_admin.initialize_app(cred, name='educational-institutions')
            except json.JSONDecodeError as je:
                st.error(f"Invalid Firebase credentials format: {str(je)}")
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

# Initialize Firebase first
firebase_app = init_firebase()

# Only proceed with Firestore operations if Firebase is initialized
if firebase_app:
    # Initialize Firestore client with the specific app instance
    db = firestore.client(app=firebase_app)

    # App title
    st.title("Educational Institutions Explorer")

    # Sidebar filters
    st.sidebar.header("Filters")

    try:
        # Get all states for filter
        states_query = db.collection('institutions').select(['state']).stream()
        states = sorted(list(set(doc.to_dict().get('state') for doc in states_query if doc.to_dict().get('state'))))

        # State filter
        selected_state = st.sidebar.selectbox("Select State", ["All States"] + states)

        # Get data based on filters
        if selected_state == "All States":
            query = db.collection('institutions').limit(100)  # Limit for performance
        else:
            query = db.collection('institutions').where('state', '==', selected_state)

        # Execute query and convert to DataFrame
        docs = list(query.stream())
        institutions = [doc.to_dict() for doc in docs]
        df = pd.DataFrame(institutions)

        if not df.empty:
            # Display count
            st.write(f"Showing {len(df)} institutions")

            # Display data table
            st.dataframe(df[['name', 'city', 'state', 'men', 'women', 'roomboard_oncampus']])

            # Add more visualizations as needed
            if len(df) > 0 and 'men' in df.columns and 'women' in df.columns:
                st.header("Gender Distribution")
                st.bar_chart(df[['men', 'women']].mean())
        else:
            st.write("No data found for the selected filters.")

        # Search functionality
        st.header("Search Institutions")
        search_term = st.text_input("Enter institution name:")

        if search_term:
            # Firestore doesn't support LIKE queries natively, so we use a workaround
            results = db.collection('institutions').order_by('name').start_at({
                'name': search_term
            }).end_at({
                'name': search_term + '\uf8ff'  # High Unicode character
            }).stream()

            search_data = [doc.to_dict() for doc in results]
            search_df = pd.DataFrame(search_data)

            if not search_df.empty:
                st.dataframe(search_df[['name', 'city', 'state']])
            else:
                st.write("No matching institutions found.")

    except Exception as e:
        st.error(f"Error accessing Firestore: {str(e)}")
else:
    st.error("Failed to initialize Firebase. Please check your credentials and try again.")