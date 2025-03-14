"""Firebase service module for institution data"""
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
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

def search_institutions(search_term, docs):
    """Search institutions with enhanced matching and known institution handling"""
    search_results = []
    search_term_lower = search_term.lower()

    # Create a list of well-known institutions for exact matching
    well_known_prefixes = [
        "harvard", "yale", "stanford", "princeton", "mit", 
        "caltech", "berkeley", "columbia", "brown", "dartmouth"
    ]

    for doc in docs:
        data = doc.to_dict()
        name = data.get('name', '')
        if name:
            name_lower = name.lower()
            similarity = 0.0

            # Check for well-known institution matches first
            if any(prefix in name_lower for prefix in well_known_prefixes):
                if search_term_lower in name_lower:
                    similarity = 1.0
                elif any(prefix.startswith(search_term_lower) for prefix in well_known_prefixes):
                    similarity = 0.95

            # If no well-known match, use general similarity
            if similarity == 0.0:
                similarity = string_similarity(search_term, name)

            if similarity > 0.2:  # Only include reasonably good matches
                search_results.append((similarity, data))

    # Sort by similarity score and take top 5
    search_results.sort(reverse=True, key=lambda x: x[0])
    return [data for score, data in search_results[:5]]

class FirebaseService:
    def __init__(self):
        self.db = None
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase with proper error handling"""
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
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            return True

        except Exception as e:
            st.error(f"Error in Firebase initialization: {str(e)}")
            return False

    def search_institutions_by_name(self, search_term):
        """Search for institutions by name"""
        if not self.db:
            st.error("Firebase database not initialized")
            return []
            
        try:
            collection_ref = self.db.collection('institutions')
            all_docs = list(collection_ref.stream())
            return search_institutions(search_term, all_docs)
        except Exception as e:
            st.error(f"Error searching institutions: {str(e)}")
            return []

    def get_institution_states(self):
        """Get list of unique states"""
        if not self.db:
            return []
            
        try:
            collection_ref = self.db.collection('institutions')
            states_query = collection_ref.select(['state']).stream()
            states = []
            for doc in states_query:
                state = doc.to_dict().get('state')
                if state:
                    states.append(state)
            return sorted(list(set(states)))
        except Exception as e:
            st.error(f"Error getting states: {str(e)}")
            return []

    def get_institutions_by_state(self, state):
        """Get institutions filtered by state"""
        if not self.db:
            return []
            
        try:
            collection_ref = self.db.collection('institutions')
            query = collection_ref.where('state', '==', state)
            docs = list(query.stream())
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            st.error(f"Error getting institutions by state: {str(e)}")
            return []
