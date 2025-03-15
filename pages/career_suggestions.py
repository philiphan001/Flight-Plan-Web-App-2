import streamlit as st
import json
from services.career_suggestion import CareerSuggestionService
from visualizations.plotter import FinancialPlotter

def load_career_suggestions_page():
    st.title("AI Career Path Suggestions 🎯")
    
    # Initialize the career suggestion service
    career_service = CareerSuggestionService()
    
    # Create input form
    with st.form("career_input_form"):
        st.subheader("Tell us about yourself")
        
        # Multi-select for interests
        interests = st.multiselect(
            "What are your interests?",
            options=[
                "Technology", "Science", "Arts", "Business",
                "Healthcare", "Education", "Engineering",
                "Environment", "Social Impact", "Finance"
            ],
            max_selections=5
        )
        
        # Multi-select for skills
        skills = st.multiselect(
            "What are your current skills?",
            options=[
                "Programming", "Data Analysis", "Design",
                "Communication", "Leadership", "Problem Solving",
                "Project Management", "Research", "Writing",
                "Marketing", "Sales", "Customer Service"
            ],
            max_selections=5
        )
        
        # Education level
        education_level = st.selectbox(
            "What is your education level?",
            options=[
                "High School",
                "Some College",
                "Associate's Degree",
                "Bachelor's Degree",
                "Master's Degree",
                "Doctorate"
            ]
        )
        
        # Work style preference
        work_style = st.selectbox(
            "What is your preferred work style?",
            options=[
                "Remote",
                "Hybrid",
                "Office-based",
                "Field work",
                "Flexible"
            ]
        )
        
        # Optional inputs
        col1, col2 = st.columns(2)
        
        with col1:
            preferred_industry = st.text_input(
                "Preferred industry (optional)",
                placeholder="e.g., Technology, Healthcare"
            )
        
        with col2:
            salary_expectation = st.text_input(
                "Expected salary range (optional)",
                placeholder="e.g., $60,000 - $80,000"
            )
        
        # Submit button
        submitted = st.form_submit_button("Generate Career Suggestions")
    
    if submitted:
        if not interests or not skills:
            st.error("Please select at least one interest and one skill.")
            return
        
        with st.spinner("Generating career suggestions..."):
            # Generate suggestions
            suggestions = career_service.generate_career_suggestions(
                interests=interests,
                skills=skills,
                education_level=education_level,
                preferred_work_style=work_style,
                preferred_industry=preferred_industry if preferred_industry else None,
                salary_expectation=salary_expectation if salary_expectation else None
            )
            
            try:
                # Parse the JSON response
                career_data = json.loads(suggestions)
                
                if "error" in career_data:
                    st.error(career_data["error"])
                    return
                
                # Create visualization
                plotter = FinancialPlotter()
                plotter.plot_career_roadmap(career_data)
                
                # Get skill recommendations
                primary_path_title = career_data.get("primary_path", {}).get("title", "")
                if primary_path_title:
                    st.subheader("Recommended Skills Development")
                    skill_recommendations = career_service.get_skill_recommendations(primary_path_title)
                    st.write(skill_recommendations)
                
            except json.JSONDecodeError:
                st.error("Failed to process career suggestions. Please try again.")
                return
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return

if __name__ == "__main__":
    load_career_suggestions_page()
