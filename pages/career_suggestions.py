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
            try:
                # Generate suggestions
                suggestions = career_service.generate_career_suggestions(
                    interests=interests,
                    skills=skills,
                    education_level=education_level,
                    preferred_work_style=work_style,
                    preferred_industry=preferred_industry if preferred_industry else None,
                    salary_expectation=salary_expectation if salary_expectation else None
                )

                # Parse the JSON string response
                career_data = json.loads(suggestions)

                if "error" in career_data:
                    st.error(career_data["error"])
                    return

                # Display career path visualization
                st.subheader("Career Path Visualization")
                plotter = FinancialPlotter()
                plotter.plot_career_roadmap(career_data)

                # Get skill recommendations
                primary_path_title = career_data.get("primary_path", {}).get("title", "")
                if primary_path_title:
                    st.subheader("Recommended Skills Development")
                    skill_recommendations = career_service.get_skill_recommendations(primary_path_title)
                    skill_data = json.loads(skill_recommendations)

                    if "error" not in skill_data:
                        # Display technical skills
                        if "technical_skills" in skill_data:
                            st.write("**Technical Skills to Develop:**")
                            for skill in skill_data["technical_skills"]:
                                st.write(f"- {skill}")

                        # Display soft skills
                        if "soft_skills" in skill_data:
                            st.write("**Soft Skills to Enhance:**")
                            for skill in skill_data["soft_skills"]:
                                st.write(f"- {skill}")

                        # Display certifications
                        if "certifications" in skill_data:
                            st.write("**Recommended Certifications:**")
                            for cert in skill_data["certifications"]:
                                st.write(f"- {cert}")

                        # Display learning resources
                        if "learning_resources" in skill_data:
                            st.write("**Learning Resources:**")
                            for resource in skill_data["learning_resources"]:
                                with st.expander(f"📚 {resource['name']}"):
                                    st.write(f"Type: {resource['type']}")
                                    if 'url' in resource and resource['url']:
                                        st.write(f"Link: {resource['url']}")
                                    if 'estimated_duration' in resource:
                                        st.write(f"Duration: {resource['estimated_duration']}")

                        # Display skill development timeline
                        if "skill_development_timeline" in skill_data:
                            st.write("**Skill Development Timeline:**")
                            for phase in skill_data["skill_development_timeline"]:
                                with st.expander(f"🎯 {phase['timeframe']}"):
                                    st.write("Focus Areas:")
                                    for area in phase["focus_areas"]:
                                        st.write(f"- {area}")
                                    st.write("\nExpected Outcomes:")
                                    for outcome in phase["expected_outcomes"]:
                                        st.write(f"- {outcome}")
                    else:
                        st.error(skill_data["error"])

            except json.JSONDecodeError as e:
                st.error(f"Failed to process career suggestions: {str(e)}")
                return
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return

if __name__ == "__main__":
    load_career_suggestions_page()