import streamlit as st
import json
from services.career_suggestion import CareerSuggestionService
from visualizations.plotter import FinancialPlotter

def load_career_game():
    """Interactive game-based career exploration"""
    st.subheader("🎮 Career Discovery Game")

    # Initialize game state if not already present
    if 'game_stage' not in st.session_state:
        st.session_state.game_stage = 0
        st.session_state.game_responses = {
            'interests': [],
            'skills': [],
            'work_style': None,
            'education_level': None
        }

    # Game stages definition
    stages = [
        {
            'name': 'Desert Island',
            'question': 'You\'re stranded on a desert island. Which three items would you choose to have with you?',
            'options': [
                ('Laptop and solar charger', {'interests': ['Technology'], 'skills': ['Problem Solving']}),
                ('Medical supplies kit', {'interests': ['Healthcare'], 'skills': ['Helping Others']}),
                ('Art supplies', {'interests': ['Arts'], 'skills': ['Creativity']}),
                ('Books on survival', {'interests': ['Research'], 'skills': ['Planning']}),
                ('Building tools', {'interests': ['Engineering'], 'skills': ['Hands-on Work']}),
                ('Communication device', {'interests': ['Communication'], 'skills': ['Leadership']}),
                ('Scientific equipment', {'interests': ['Science'], 'skills': ['Analysis']}),
                ('Musical instrument', {'interests': ['Arts'], 'skills': ['Entertainment']}),
                ('Teaching materials', {'interests': ['Education'], 'skills': ['Communication']}),
                ('Business planning notebook', {'interests': ['Business'], 'skills': ['Organization']})
            ]
        },
        {
            'name': 'Dream Project',
            'question': 'If you had unlimited resources, what kind of project would you start?',
            'options': [
                ('Tech startup', {'interests': ['Technology'], 'skills': ['Innovation', 'Business']}),
                ('Environmental conservation', {'interests': ['Environment'], 'skills': ['Social Impact']}),
                ('Community education center', {'interests': ['Education'], 'skills': ['Teaching']}),
                ('Healthcare innovation lab', {'interests': ['Healthcare'], 'skills': ['Research']}),
                ('Creative arts studio', {'interests': ['Arts'], 'skills': ['Design']}),
                ('Social enterprise', {'interests': ['Business'], 'skills': ['Leadership']}),
                ('Research institute', {'interests': ['Science'], 'skills': ['Analysis']}),
                ('Engineering workshop', {'interests': ['Engineering'], 'skills': ['Innovation']}),
                ('Financial advisory firm', {'interests': ['Finance'], 'skills': ['Analysis']}),
                ('Digital media company', {'interests': ['Technology', 'Arts'], 'skills': ['Creativity']})
            ]
        },
        {
            'name': 'Work Style',
            'question': 'How would you prefer to structure your workday?',
            'options': [
                ('Fixed schedule with clear tasks', {'work_style': 'Office-based'}),
                ('Flexible hours working remotely', {'work_style': 'Remote'}),
                ('Mix of office and remote work', {'work_style': 'Hybrid'}),
                ('Different locations each day', {'work_style': 'Field work'}),
                ('Project-based flexible schedule', {'work_style': 'Flexible'})
            ]
        },
        {
            'name': 'Learning Path',
            'question': 'What\'s your ideal way to learn something new?',
            'options': [
                ('Traditional academic courses', {'education_level': "Bachelor's Degree"}),
                ('Hands-on training programs', {'education_level': "Associate's Degree"}),
                ('Self-paced online learning', {'education_level': 'Some College'}),
                ('Advanced research projects', {'education_level': "Master's Degree"}),
                ('Intensive specialized study', {'education_level': 'Doctorate'})
            ]
        }
    ]

    # Check if game is complete
    if st.session_state.game_stage >= len(stages):
        st.success("🎉 Game Complete! Let's see your career matches!")

        # Clean up and deduplicate responses
        st.session_state.game_responses['interests'] = list(set(st.session_state.game_responses['interests']))
        st.session_state.game_responses['skills'] = list(set(st.session_state.game_responses['skills']))

        if st.button("View Career Suggestions"):
            st.session_state.show_suggestions = True
            st.session_state.hide_game = True
            st.rerun()
        return

    # Get current stage
    current_stage = stages[st.session_state.game_stage]

    # Display current stage
    st.markdown(f"### 🎯 {current_stage['name']}")
    st.write(current_stage['question'])

    # Handle multi-select stages (first two stages)
    if st.session_state.game_stage < 2:
        selected_options = st.multiselect(
            "Choose up to three options:",
            options=[opt[0] for opt in current_stage['options']],
            max_selections=3
        )

        if selected_options:
            if st.button("Next ➡️"):
                # Process selections
                for selection in selected_options:
                    traits = next(opt[1] for opt in current_stage['options'] if opt[0] == selection)
                    st.session_state.game_responses['interests'].extend(traits.get('interests', []))
                    st.session_state.game_responses['skills'].extend(traits.get('skills', []))
                st.session_state.game_stage += 1
                st.rerun()

    # Handle single-select stages (work style and education)
    else:
        for option, traits in current_stage['options']:
            if st.button(option, key=f"option_{option}"):
                if 'work_style' in traits:
                    st.session_state.game_responses['work_style'] = traits['work_style']
                if 'education_level' in traits:
                    st.session_state.game_responses['education_level'] = traits['education_level']
                st.session_state.game_stage += 1
                st.rerun()

    # Show progress
    progress = st.session_state.game_stage / len(stages)
    st.progress(progress)

def load_career_suggestions_page():
    """Main career suggestions page"""
    st.title("AI Career Path Suggestions 🎯")

    # Initialize session state variables
    if 'show_suggestions' not in st.session_state:
        st.session_state.show_suggestions = False
    if 'exploration_mode' not in st.session_state:
        st.session_state.exploration_mode = 'traditional'
    if 'hide_game' not in st.session_state:
        st.session_state.hide_game = False
    if 'saved_career_suggestions' not in st.session_state:
        st.session_state.saved_career_suggestions = []

    # Initialize form variables
    interests = []
    skills = []
    education_level = None
    work_style = None
    preferred_industry = None
    salary_expectation = None
    submitted = False

    # Only show mode selection if not showing suggestions
    if not st.session_state.show_suggestions:
        st.write("Choose how you'd like to explore career paths:")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Traditional Form", 
                        use_container_width=True,
                        help="Fill out a form with your interests and preferences"):
                st.session_state.exploration_mode = 'traditional'
                st.session_state.show_suggestions = False
                st.session_state.hide_game = False
                st.rerun()

        with col2:
            if st.button("🎮 Let's Play a Game!", 
                        use_container_width=True,
                        help="Discover your career interests through interactive scenarios"):
                st.session_state.exploration_mode = 'game'
                st.session_state.game_stage = 0
                st.session_state.game_responses = {
                    'interests': [],
                    'skills': [],
                    'work_style': None,
                    'education_level': None
                }
                st.session_state.show_suggestions = False
                st.session_state.hide_game = False
                st.rerun()

        st.markdown("---")

    # Show appropriate interface based on mode and state
    if st.session_state.exploration_mode == 'traditional' and not st.session_state.show_suggestions:
        with st.form("career_input_form"):
            st.subheader("Tell us about yourself")

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

            if submitted:
                st.session_state.show_suggestions = True
                st.session_state.form_data = {
                    'interests': interests,
                    'skills': skills,
                    'education_level': education_level,
                    'work_style': work_style,
                    'preferred_industry': preferred_industry,
                    'salary_expectation': salary_expectation
                }

    elif st.session_state.exploration_mode == 'game' and not st.session_state.hide_game:
        load_career_game()

    # Generate career suggestions if needed
    if st.session_state.show_suggestions:
        if st.session_state.exploration_mode == 'game':
            # Get data from game responses
            interests = list(set(st.session_state.game_responses['interests']))
            skills = list(set(st.session_state.game_responses['skills']))
            education_level = st.session_state.game_responses['education_level']
            work_style = st.session_state.game_responses['work_style']
            preferred_industry = None
            salary_expectation = None
        else:
            # Get data from form
            form_data = st.session_state.form_data
            interests = form_data['interests']
            skills = form_data['skills']
            education_level = form_data['education_level']
            work_style = form_data['work_style']
            preferred_industry = form_data['preferred_industry']
            salary_expectation = form_data['salary_expectation']

        # Validate data
        if not interests or not skills:
            st.error("Please provide at least one interest and one skill.")
            return

        # Generate suggestions
        career_service = CareerSuggestionService()

        with st.spinner("Generating career suggestions..."):
            try:
                suggestions = career_service.generate_career_suggestions(
                    interests=interests,
                    skills=skills,
                    education_level=education_level,
                    preferred_work_style=work_style,
                    preferred_industry=preferred_industry,
                    salary_expectation=salary_expectation
                )

                # Parse and display suggestions
                career_data = json.loads(suggestions)

                if "error" in career_data:
                    st.error(career_data["error"])
                    return

                # Display visualizations and suggestions
                st.subheader("Career Path Visualization")
                plotter = FinancialPlotter()
                plotter.plot_career_roadmap(career_data)

                # Display primary career path
                st.subheader("🎯 Primary Career Path")
                with st.expander(f"📋 {career_data['primary_path']['title']}", expanded=True):
                    st.write(f"**Description:** {career_data['primary_path']['description']}")

                    st.write("**Career Timeline:**")
                    for milestone in career_data['primary_path']['timeline']:
                        st.write(f"Year {milestone['year']}: {milestone['milestone']}")
                        st.write(f"- Required Skills: {', '.join(milestone['skills_needed'])}")
                        st.write(f"- Estimated Salary: ${milestone['estimated_salary']:,}")

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

                # Display alternative paths
                st.subheader("🔄 Alternative Career Paths")
                for idx, alt_path in enumerate(career_data['alternative_paths']):
                    with st.expander(f"📋 {alt_path['title']}", expanded=False):
                        st.write(f"**Description:** {alt_path['description']}")

                        st.write("**Career Timeline:**")
                        for milestone in alt_path['timeline']:
                            st.write(f"Year {milestone['year']}: {milestone['milestone']}")
                            st.write(f"- Required Skills: {', '.join(milestone['skills_needed'])}")
                            st.write(f"- Estimated Salary: ${milestone['estimated_salary']:,}")

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

                # Get skill recommendations
                st.subheader("📚 Recommended Skills Development")
                primary_path_title = career_data['primary_path']['title']
                skill_recommendations = career_service.get_skill_recommendations(primary_path_title)
                skill_data = json.loads(skill_recommendations)

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

                # Add profile navigation
                st.markdown("---")
                if st.button("👤 View Your Profile"):
                    st.switch_page("pages/user_profile.py")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return

if __name__ == "__main__":
    load_career_suggestions_page()