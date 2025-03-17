import streamlit as st
import json
from services.career_suggestion import CareerSuggestionService
from visualizations.plotter import FinancialPlotter

def load_career_game():
    """Interactive game-based career exploration"""
    st.subheader("🎮 Career Discovery Game")

    # Initialize game state
    if 'game_stage' not in st.session_state:
        st.session_state.game_stage = 0
    if 'game_responses' not in st.session_state:
        st.session_state.game_responses = {
            'interests': [],
            'skills': [],
            'values': [],
            'work_style': None,
            'education_level': None
        }

    # Game stages remain unchanged
    stages = [
        {
            'name': 'Desert Island',
            'question': 'You\'re stranded on a desert island. Which three items would you choose to have with you?',
            'options': [
                ('Laptop and solar charger', ['Technology', 'Problem Solving']),
                ('Medical supplies kit', ['Healthcare', 'Helping Others']),
                ('Art supplies', ['Arts', 'Creativity']),
                ('Books on survival', ['Research', 'Planning']),
                ('Building tools', ['Engineering', 'Hands-on Work']),
                ('Communication device', ['Communication', 'Leadership']),
                ('Scientific equipment', ['Science', 'Analysis']),
                ('Musical instrument', ['Arts', 'Entertainment']),
                ('Teaching materials', ['Education', 'Communication']),
                ('Business planning notebook', ['Business', 'Organization'])
            ]
        },
        {
            'name': 'Dream Project',
            'question': 'If you had unlimited resources, what kind of project would you start?',
            'options': [
                ('Tech startup', ['Technology', 'Innovation', 'Business']),
                ('Environmental conservation', ['Environment', 'Social Impact']),
                ('Community education center', ['Education', 'Social Impact']),
                ('Healthcare innovation lab', ['Healthcare', 'Science']),
                ('Creative arts studio', ['Arts', 'Design']),
                ('Social enterprise', ['Business', 'Social Impact']),
                ('Research institute', ['Science', 'Research']),
                ('Engineering workshop', ['Engineering', 'Innovation']),
                ('Financial advisory firm', ['Finance', 'Business']),
                ('Digital media company', ['Technology', 'Arts'])
            ]
        },
        {
            'name': 'Time Management',
            'question': 'How would you prefer to structure your workday?',
            'options': [
                ('Fixed schedule, clear tasks', 'Office-based'),
                ('Flexible hours, remote work', 'Remote'),
                ('Mix of office and remote', 'Hybrid'),
                ('Different locations daily', 'Field work'),
                ('Project-based scheduling', 'Flexible')
            ]
        },
        {
            'name': 'Learning Style',
            'question': 'What\'s your ideal way to learn something new?',
            'options': [
                ('Traditional academic courses', "Bachelor's Degree"),
                ('Hands-on training programs', "Associate's Degree"),
                ('Self-paced online learning', 'Some College'),
                ('Advanced research projects', "Master's Degree"),
                ('Intensive specialized study', 'Doctorate')
            ]
        }
    ]

    # Check if game is complete
    if st.session_state.game_stage >= len(stages):
        st.success("🎉 Game Complete! Let's find your career matches!")

        # Clean up and deduplicate responses
        st.session_state.game_responses['interests'] = list(set(st.session_state.game_responses['interests']))
        st.session_state.game_responses['skills'] = list(set(st.session_state.game_responses['skills']))

        # Transfer game responses to career suggestion inputs
        st.session_state.user_interests = st.session_state.game_responses['interests']
        st.session_state.user_skills = st.session_state.game_responses['skills']

        if st.button("View Career Suggestions"):
            st.session_state.game_complete = True
            st.session_state.show_suggestions = True
            # Reset game stage for next time
            st.session_state.game_stage = 0
            st.rerun()
        return

    # Get current stage
    current_stage = stages[st.session_state.game_stage]

    # Display current game stage
    st.markdown(f"### 🎯 {current_stage['name']}")
    st.write(current_stage['question'])

    if st.session_state.game_stage < 2:  # Multi-select stages
        selected_options = st.multiselect(
            "Choose up to three options:",
            [opt[0] for opt in current_stage['options']],
            max_selections=3
        )

        if selected_options:
            # Map selections to interests/skills
            for selection in selected_options:
                traits = next(opt[1] for opt in current_stage['options'] if opt[0] == selection)
                st.session_state.game_responses['interests'].extend(traits)

            if st.button("Next ➡️"):
                st.session_state.game_stage += 1
                st.rerun()

    else:  # Single-select stages
        for option, value in current_stage['options']:
            if st.button(option, key=f"option_{value}"):
                if st.session_state.game_stage == 2:  # Work style
                    st.session_state.game_responses['work_style'] = value
                else:  # Education level
                    st.session_state.game_responses['education_level'] = value
                st.session_state.game_stage += 1
                st.rerun()

    # Fixed progress calculation - now returns value between 0 and 1
    progress = st.session_state.game_stage / len(stages)
    st.progress(progress)

def load_career_suggestions_page():
    st.title("AI Career Path Suggestions 🎯")

    # Initialize session state
    if 'saved_career_suggestions' not in st.session_state:
        st.session_state.saved_career_suggestions = []
    if 'user_interests' not in st.session_state:
        st.session_state.user_interests = []
    if 'user_skills' not in st.session_state:
        st.session_state.user_skills = []
    if 'show_suggestions' not in st.session_state:
        st.session_state.show_suggestions = False
    if 'exploration_mode' not in st.session_state:
        st.session_state.exploration_mode = 'traditional'

    # Mode selection
    st.write("Choose how you'd like to explore career paths:")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 Traditional Form", 
                    use_container_width=True,
                    help="Fill out a form with your interests and preferences"):
            st.session_state.exploration_mode = 'traditional'
            st.session_state.show_suggestions = False
            st.rerun()

    with col2:
        if st.button("🎮 Let's Play a Game!", 
                    use_container_width=True,
                    help="Discover your career interests through interactive scenarios"):
            st.session_state.exploration_mode = 'game'
            st.session_state.game_stage = 0
            st.session_state.show_suggestions = False
            st.rerun()

    st.markdown("---")

    if st.session_state.exploration_mode == 'traditional':
        # Create input form
        with st.form("career_input_form"):
            st.subheader("Tell us about yourself")

            # Original form inputs remain unchanged
            interests = st.multiselect(
                "What are your interests?",
                options=[
                    "Technology", "Science", "Arts", "Business",
                    "Healthcare", "Education", "Engineering",
                    "Environment", "Social Impact", "Finance"
                ],
                max_selections=5
            )

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

            submitted = st.form_submit_button("Generate Career Suggestions")

    else:
        # Load the game interface
        load_career_game()
        submitted = st.session_state.show_suggestions
        interests = st.session_state.user_interests
        skills = st.session_state.user_skills
        education_level = st.session_state.game_responses.get('education_level')
        work_style = st.session_state.game_responses.get('work_style')
        preferred_industry = None
        salary_expectation = None

    if submitted:
        if not interests or not skills:
            st.error("Please select at least one interest and one skill.")
            return

        # Initialize the career suggestion service
        career_service = CareerSuggestionService()

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

                # Display primary career path with save option
                st.subheader("🎯 Primary Career Path")
                with st.expander(f"📋 {career_data['primary_path']['title']}", expanded=True):
                    st.write(career_data['primary_path']['description'])
                    st.write("**Career Timeline:**")
                    for milestone in career_data['primary_path']['timeline']:
                        st.write(f"Year {milestone['year']}: {milestone['milestone']}")
                        st.write(f"- Required Skills: {', '.join(milestone['skills_needed'])}")
                        st.write(f"- Estimated Salary: ${milestone['estimated_salary']:,}")

                    # Save button for primary path
                    if st.button("💾 Save to Profile", key="save_primary"):
                        saved_career = {
                            'type': 'primary',
                            'title': career_data['primary_path']['title'],
                            'description': career_data['primary_path']['description'],
                            'timeline': career_data['primary_path']['timeline'],
                            'interests': interests,
                            'skills': skills,
                            'education_level': education_level,
                            'work_style': work_style
                        }
                        st.session_state.saved_career_suggestions.append(saved_career)
                        st.success(f"Saved {career_data['primary_path']['title']} to your profile!")

                # Display alternative paths with save options
                st.subheader("🔄 Alternative Career Paths")
                for idx, alt_path in enumerate(career_data['alternative_paths']):
                    with st.expander(f"📋 {alt_path['title']}", expanded=False):
                        st.write(alt_path['description'])
                        st.write("**Career Timeline:**")
                        for milestone in alt_path['timeline']:
                            st.write(f"Year {milestone['year']}: {milestone['milestone']}")
                            st.write(f"- Required Skills: {', '.join(milestone['skills_needed'])}")
                            st.write(f"- Estimated Salary: ${milestone['estimated_salary']:,}")

                        # Save button for alternative path
                        if st.button("💾 Save to Profile", key=f"save_alt_{idx}"):
                            saved_career = {
                                'type': 'alternative',
                                'title': alt_path['title'],
                                'description': alt_path['description'],
                                'timeline': alt_path['timeline'],
                                'interests': interests,
                                'skills': skills,
                                'education_level': education_level,
                                'work_style': work_style
                            }
                            st.session_state.saved_career_suggestions.append(saved_career)
                            st.success(f"Saved {alt_path['title']} to your profile!")

                # Get skill recommendations for primary path
                primary_path_title = career_data['primary_path']['title']
                skill_recommendations = career_service.get_skill_recommendations(primary_path_title)
                skill_data = json.loads(skill_recommendations)

                if "error" not in skill_data:
                    st.subheader("📚 Recommended Skills Development")
                    if "technical_skills" in skill_data:
                        st.write("**Technical Skills to Develop:**")
                        for skill in skill_data["technical_skills"]:
                            st.write(f"- {skill}")

                    if "soft_skills" in skill_data:
                        st.write("**Soft Skills to Enhance:**")
                        for skill in skill_data["soft_skills"]:
                            st.write(f"- {skill}")

                    if "certifications" in skill_data:
                        st.write("**Recommended Certifications:**")
                        for cert in skill_data["certifications"]:
                            st.write(f"- {cert}")

                    if "learning_resources" in skill_data:
                        st.write("**Learning Resources:**")
                        for resource in skill_data["learning_resources"]:
                            with st.expander(f"📚 {resource['name']}"):
                                st.write(f"Type: {resource['type']}")
                                if 'url' in resource and resource['url']:
                                    st.write(f"Link: {resource['url']}")
                                if 'estimated_duration' in resource:
                                    st.write(f"Duration: {resource['estimated_duration']}")

                # Add view profile button
                st.markdown("---")
                if st.button("👤 View Your Profile"):
                    st.switch_page("pages/user_profile.py")

            except json.JSONDecodeError as e:
                st.error(f"Failed to process career suggestions: {str(e)}")
                return
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return

if __name__ == "__main__":
    load_career_suggestions_page()