import streamlit as st
from services.bls_api import BLSApi

def test_bls_api():
    """
    Simple test function to verify BLS API functionality
    """
    try:
        # Initialize API
        bls_api = BLSApi()
        
        # Test occupation search
        results = bls_api.search_occupations("software")
        st.write("### Sample Occupation Search Results")
        st.write(results)
        
        if results:
            # Test getting occupation data
            occupation_code = results[0]['code']
            occupation_data = bls_api.get_occupation_data(occupation_code)
            st.write("### Sample Occupation Data")
            st.write(occupation_data)
            
            # Test salary data
            salary_data = bls_api.get_salary_by_location(occupation_code, "0000000")
            st.write("### Sample Salary Data")
            st.write(salary_data)
            
        st.success("✅ BLS API integration test completed successfully")
        return True
        
    except Exception as e:
        st.error(f"❌ Error testing BLS API: {str(e)}")
        return False

if __name__ == "__main__":
    test_bls_api()
