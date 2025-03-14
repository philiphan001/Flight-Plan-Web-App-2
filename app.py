import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json

# Initialize Firebase (if not already initialized)
if not firebase_admin._apps:
    # Get credentials from Replit secrets
    cred_dict = json.loads(os.environ['FIREBASE_CREDENTIALS'])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# App title
st.title("Educational Institutions Explorer")

# Sidebar filters
st.sidebar.header("Filters")

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
    # This gets documents where the name field starts with the search term
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
