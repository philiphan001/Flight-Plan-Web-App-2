"""Career and Education Pathways Page"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
import plotly.graph_objects as go
from models.milestone_factory import Milestone, MilestoneFactory
from components.timeline_component import timeline_component
from fuzzywuzzy import fuzz
import graphviz

# Page configuration
st.set_page_config(
    page_title="Career & Education Pathways",
    page_icon="🛣️",
    layout="wide"
)

def load_colleges():
    # This would ideally come from a database - for now using a sample list
    return [
        "University of Washington",
        "Stanford University",
        "Harvard University",
        "Massachusetts Institute of Technology",
        "University of California, Berkeley",
        "Georgia Institute of Technology",
        "United States Air Force Academy",
        "United States Naval Academy",
        "Community College",
        "Technical College",
    ]

def load_careers():
    # This would ideally come from a database - for now using a sample list
    return [
        "Software Engineer",
        "Pilot",
        "Aircraft Mechanic",
        "Air Traffic Controller",
        "Flight Attendant",
        "Aerospace Engineer",
        "Aviation Manager",
        "Aircraft Designer",
        "Drone Operator",
        "Aviation Safety Inspector",
    ]

def load_military_branches():
    return [
        "Air Force",
        "Navy",
        "Army",
        "Marine Corps",
        "Coast Guard",
        "Space Force",
    ]

def load_gap_year_options():
    return [
        "Travel and Exploration",
        "Volunteer Work",
        "Internship",
        "Work and Save",
        "Learn a New Skill",
        "Language Study Abroad",
    ]

def load_programs():
    """Load available programs/majors"""
    return {
        "Computer Science & Engineering": {
            "careers": ["Software Engineer", "AI/ML Engineer", "Cybersecurity Specialist"],
            "description": "Study the theory and practice of computing, including programming, algorithms, and system design."
        },
        "Aerospace Engineering": {
            "careers": ["Aerospace Engineer", "Aircraft Designer", "Systems Engineer"],
            "description": "Focus on aircraft and spacecraft design, aerodynamics, and propulsion systems."
        },
        "Aviation Management": {
            "careers": ["Aviation Manager", "Air Traffic Controller", "Airport Operations Manager"],
            "description": "Learn about aviation operations, safety, and management principles."
        },
        "Business Administration": {
            "careers": ["Business Analyst", "Project Manager", "Operations Manager"],
            "description": "Study business principles, management, finance, and organizational behavior."
        },
        "Data Science": {
            "careers": ["Data Scientist", "Data Analyst", "Machine Learning Engineer"],
            "description": "Learn to analyze and interpret complex data using statistical and computational methods."
        }
    }

def display_military_flowchart(selected_branch: str, selected_node: str = None):
    """Display an interactive military pathway flowchart"""
    # Create a new directed graph
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB')
    
    # Style configurations
    graph.attr('node', shape='rectangle', style='rounded,filled', fillcolor='white')
    
    # Add nodes with conditional styling
    nodes = {
        'enlist': 'Enlistment\nAfter High School',
        'boot': 'Basic Training\n(Boot Camp)\n8-13 weeks',
        'ait': f'Advanced Training\n(AIT/Technical School)\nSpecialized Skills',
        'edu_options': 'Education Options\nWhile Serving',
        'ta': 'Tuition\nAssistance',
        'online': 'Online/Evening\nClasses',
        'clep': 'CLEP/DANTES\nExams',
        'outcomes': 'Career\nOutcomes',
        'military_career': 'Military Career\nAdvancement',
        'civilian': 'Civilian\nTransition',
        'gi_bill': 'GI Bill\nEducation'
    }
    
    # Add Air Force specific node
    if selected_branch == "Air Force":
        nodes['ccaf'] = 'Community College\nof the Air Force'
    
    # Add nodes with conditional styling
    for node_id, label in nodes.items():
        if node_id == selected_node:
            graph.node(node_id, label, fillcolor='lightblue', style='rounded,filled,bold')
        else:
            graph.node(node_id, label)
    
    # Add edges
    graph.edge('enlist', 'boot')
    graph.edge('boot', 'ait')
    graph.edge('ait', 'edu_options')
    graph.edge('ait', 'outcomes')
    
    # Education path edges
    graph.edge('edu_options', 'ta')
    graph.edge('edu_options', 'online')
    graph.edge('edu_options', 'clep')
    if selected_branch == "Air Force":
        graph.edge('edu_options', 'ccaf')
    
    # Career outcome edges
    graph.edge('outcomes', 'military_career')
    graph.edge('outcomes', 'civilian')
    graph.edge('outcomes', 'gi_bill')
    
    # Render the graph
    st.graphviz_chart(graph)

def show_military_path_details(node_type: str, selected_branch: str):
    """Show detailed information for selected military path nodes"""
    if node_type == "enlist":
        st.write("### Enlistment Process")
        st.write("• Meet with a recruiter")
        st.write("• Take the ASVAB test")
        st.write("• Pass physical examination")
        st.write("• Select your Military Occupational Specialty (MOS)")
        st.write("• Sign enlistment contract")
        
    elif node_type == "boot":
        st.write("### Basic Training")
        st.write("• Physical fitness and conditioning")
        st.write("• Military customs and courtesies")
        st.write("• Weapons training")
        st.write("• Basic tactical skills")
        st.write(f"• {selected_branch}-specific training requirements")
        
    elif node_type == "ait":
        st.write("### Advanced Individual Training")
        st.write("• Specialized skills for your chosen career field")
        st.write("• Hands-on technical training")
        st.write("• Classroom instruction")
        st.write("• Field exercises")
        
    elif node_type == "edu_options":
        st.write("### Education While Serving")
        st.write("• Multiple paths to earn your degree")
        st.write("• Compatible with military service")
        st.write("• Financial assistance available")
        
    elif node_type == "ta":
        st.write("### Tuition Assistance")
        st.write("• Up to 100% of tuition costs covered")
        st.write("• Annual and lifetime caps apply")
        st.write("• Available for degree programs")
        st.write("• Can be used for certifications")
        
    elif node_type == "online":
        st.write("### Online/Evening Classes")
        st.write("• Flexible scheduling")
        st.write("• Military-friendly universities")
        st.write("• Study during off-duty hours")
        
    elif node_type == "clep":
        st.write("### CLEP/DANTES Exams")
        st.write("• Test out of college courses")
        st.write("• Save time and money")
        st.write("• Free for service members")
        
    elif node_type == "ccaf" and selected_branch == "Air Force":
        st.write("### Community College of the Air Force")
        st.write("• Associate degrees in Air Force specialties")
        st.write("• Credits for military training")
        st.write("• Transferable to other institutions")
        
    elif node_type == "outcomes":
        st.write("### Career Outcomes")
        st.write("• Multiple career paths available")
        st.write("• Leadership opportunities")
        st.write("• Valuable experience")
        
    elif node_type == "military_career":
        st.write("### Military Career Advancement")
        st.write("• Promotion opportunities")
        st.write("• Leadership roles")
        st.write("• Advanced training")
        st.write("• Retirement benefits")
        
    elif node_type == "civilian":
        st.write("### Civilian Career Transition")
        st.write("• Skills transfer to civilian jobs")
        st.write("• Veterans' preference in federal jobs")
        st.write("• Career counseling available")
        st.write("• Networking opportunities")
        
    elif node_type == "gi_bill":
        st.write("### GI Bill Education Benefits")
        st.write("• Tuition and fees covered")
        st.write("• Monthly housing allowance")
        st.write("• Book stipend")
        st.write("• Up to 36 months of benefits")

def show_known_path():
    st.write("## After high school, I plan on...")
    
    # Create columns for the choices
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Continuing my Education", use_container_width=True):
            st.session_state.chosen_path = "college"
    
        if st.button("Joining the Military 🪖", use_container_width=True):
            st.session_state.chosen_path = "military"
            
    with col2:
        if st.button("Starting Work 💼", use_container_width=True):
            st.session_state.chosen_path = "work"
            
        if st.button("Taking a Gap Year 🌎", use_container_width=True):
            st.session_state.chosen_path = "gap_year"
    
    # Show the appropriate options based on the chosen path
    if "chosen_path" in st.session_state:
        st.write("---")
        if st.session_state.chosen_path == "college":
            # Initialize session states if not exists
            if 'selected_college_name' not in st.session_state:
                st.session_state.selected_college_name = ""
            if 'selected_program' not in st.session_state:
                st.session_state.selected_program = ""
            if 'selected_career_goal' not in st.session_state:
                st.session_state.selected_career_goal = ""
            
            # Step 1: College Selection
            if not st.session_state.selected_college_name:
                st.write("### I'd like to go to...")
                
                # Add a search box for colleges
                search_query = st.text_input(
                    "Search for a college by name",
                    value=st.session_state.selected_college_name,
                    placeholder="Enter college name (e.g., Harvard, Stanford, MIT)",
                    help="Type to search for colleges",
                    key="college_search"
                )
                
                if search_query:
                    # Load college data
                    df = pd.read_csv('attached_assets/Updated_Most-Recent-Cohorts-Institution.csv')
                    
                    # Calculate similarity scores for each college name
                    scores = [(name, fuzz.ratio(search_query.lower(), name.lower()))
                             for name in df['name']]
                    
                    # Sort by score in descending order and get top matches
                    best_matches = sorted(scores, key=lambda x: x[1], reverse=True)[:5]
                    best_match_names = [match[0] for match in best_matches]
                    
                    # Create a new DataFrame with the matching rows
                    matched_colleges = df[df['name'].isin(best_match_names)].copy()
                    
                    if not matched_colleges.empty:
                        st.write("#### Top Matches:")
                        for _, college in matched_colleges.iterrows():
                            # Create a unique identifier for the college
                            college_id = f"{college['name']}_{college['city']}_{college['state']}"
                            
                            with st.expander(f"🏫 {college['name']} ({college['city']}, {college['state']})", expanded=False):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.write("**Institution Details**")
                                    if pd.notna(college['admission_rate.overall']):
                                        st.write(f"• Admission Rate: {college['admission_rate.overall']*100:.1f}%")
                                    if pd.notna(college['sat_scores.average.overall']):
                                        st.write(f"• Average SAT: {int(college['sat_scores.average.overall'])}")
                                    if pd.notna(college['US News Top 150']):
                                        st.write(f"• US News: #{int(college['US News Top 150'])}")
                                    
                                with col2:
                                    st.write("**Cost Information**")
                                    if college['ownership'] == 1:  # Public institution
                                        if pd.notna(college['avg_net_price.public']):
                                            st.write(f"• In-State: ${int(college['avg_net_price.public']):,}")
                                        if pd.notna(college['avg_net_price.private']):
                                            st.write(f"• Out-of-State: ${int(college['avg_net_price.private']):,}")
                                    else:  # Private institution
                                        if pd.notna(college['avg_net_price.private']):
                                            st.write(f"• Tuition: ${int(college['avg_net_price.private']):,}")
                                
                                if st.button("Select this college", key=f"select_{college_id}"):
                                    st.session_state.selected_college = college.to_dict()
                                    st.session_state.selected_college_name = college['name']
                                    st.rerun()
                    else:
                        st.info("No matching colleges found. Try a different search term.")
                
                # Add a link to the full college discovery page
                st.write("---")
                if st.button("🔍 Explore More Colleges"):
                    st.switch_page("pages/college_discovery.py")
            
            # Step 2: Program Selection (only show if college is selected)
            elif not st.session_state.selected_program:
                st.write(f"### At {st.session_state.selected_college_name}, I'd like to study...")
                
                # Get available programs
                programs = load_programs()
                
                # Create program selection
                for program_name, program_info in programs.items():
                    with st.expander(f"📚 {program_name}", expanded=False):
                        st.write(program_info["description"])
                        st.write("\n**Potential Careers:**")
                        for career in program_info["careers"]:
                            st.write(f"• {career}")
                        if st.button("Select this program", key=f"select_program_{program_name}"):
                            st.session_state.selected_program = program_name
                            st.session_state.available_careers = program_info["careers"]
                            st.rerun()
                
                # Add option to change college
                st.write("---")
                if st.button("← Change College Selection"):
                    st.session_state.selected_college_name = ""
                    st.session_state.selected_college = None
                    st.rerun()
            
            # Step 3: Career Goal Selection (only show if program is selected)
            elif not st.session_state.selected_career_goal:
                st.write(f"### With my {st.session_state.selected_program} degree, I'd like to become...")
                
                # Show careers related to the selected program
                for career in st.session_state.available_careers:
                    if st.button(f"🎯 {career}", key=f"select_career_{career}", use_container_width=True):
                        st.session_state.selected_career_goal = career
                        st.rerun()
                
                # Add options to change previous selections
                st.write("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("← Change College"):
                        st.session_state.selected_college_name = ""
                        st.session_state.selected_college = None
                        st.session_state.selected_program = ""
                        st.rerun()
                with col2:
                    if st.button("← Change Program"):
                        st.session_state.selected_program = ""
                        st.rerun()
            
            # Show final pathway summary
            else:
                st.success("🎉 Your pathway is set!")
                st.write("### Your Educational & Career Path:")
                st.write(f"1. 🏫 Attend **{st.session_state.selected_college_name}**")
                st.write(f"2. 📚 Study **{st.session_state.selected_program}**")
                st.write(f"3. 🎯 Become a **{st.session_state.selected_career_goal}**")
                
                # Add options to change selections
                st.write("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Change College"):
                        st.session_state.selected_college_name = ""
                        st.session_state.selected_college = None
                        st.session_state.selected_program = ""
                        st.session_state.selected_career_goal = ""
                        st.rerun()
                with col2:
                    if st.button("Change Program"):
                        st.session_state.selected_program = ""
                        st.session_state.selected_career_goal = ""
                        st.rerun()
                with col3:
                    if st.button("Change Career Goal"):
                        st.session_state.selected_career_goal = ""
                        st.rerun()
                
                # Add button to view detailed plan
                st.write("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📋 View Detailed Plan", use_container_width=True):
                        # TODO: Implement detailed plan view
                        pass
                
                with col2:
                    if st.button("⭐ Save to My Profile", use_container_width=True):
                        # Save the pathway to user's profile
                        if 'saved_pathways' not in st.session_state:
                            st.session_state.saved_pathways = []
                        
                        # Create a pathway object
                        pathway = {
                            'type': 'college',
                            'college': st.session_state.selected_college,
                            'program': st.session_state.selected_program,
                            'career_goal': st.session_state.selected_career_goal,
                            'timestamp': pd.Timestamp.now()
                        }
                        
                        st.session_state.saved_pathways.append(pathway)
                        st.success("✅ Pathway saved to your profile!")
                        
                        # Option to view profile
                        if st.button("👤 View My Profile"):
                            st.switch_page("pages/user_profile.py")
                
        elif st.session_state.chosen_path == "military":
            if 'military_step' not in st.session_state:
                st.session_state.military_step = 'branch'
                st.session_state.selected_node = None

            # Step 1: Branch Selection
            if st.session_state.military_step == 'branch':
                st.write("### Which branch of service interests you?")
                selected_branch = st.selectbox("Select a branch:", load_military_branches())
                if selected_branch:
                    st.session_state.selected_branch = selected_branch
                    if st.button("Continue"):
                        st.session_state.military_step = 'path'
                        st.rerun()

            # Step 2: Interactive Flowchart
            elif st.session_state.military_step == 'path':
                st.write(f"### Your Path in the {st.session_state.selected_branch}")
                
                # Display the flowchart
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Node selection
                    nodes = ['enlist', 'boot', 'ait', 'edu_options', 'ta', 'online', 'clep', 
                            'outcomes', 'military_career', 'civilian', 'gi_bill']
                    if st.session_state.selected_branch == "Air Force":
                        nodes.append('ccaf')
                    
                    selected_node = st.selectbox(
                        "Select a node to learn more:",
                        nodes,
                        format_func=lambda x: {
                            'enlist': 'Enlistment Process',
                            'boot': 'Basic Training',
                            'ait': 'Advanced Training',
                            'edu_options': 'Education Options',
                            'ta': 'Tuition Assistance',
                            'online': 'Online/Evening Classes',
                            'clep': 'CLEP/DANTES Exams',
                            'ccaf': 'Community College of the Air Force',
                            'outcomes': 'Career Outcomes',
                            'military_career': 'Military Career',
                            'civilian': 'Civilian Transition',
                            'gi_bill': 'GI Bill Education'
                        }[x]
                    )
                    
                    # Display flowchart with selected node
                    display_military_flowchart(st.session_state.selected_branch, selected_node)
                
                with col2:
                    # Display details for selected node
                    if selected_node:
                        show_military_path_details(selected_node, st.session_state.selected_branch)
                
                # Add back button
                if st.button("← Change Branch"):
                    st.session_state.military_step = 'branch'
                    st.rerun()

        elif st.session_state.chosen_path == "work":
            st.write("### What career interests you?")
            selected_career = st.selectbox("Select a career:", load_careers())
            if selected_career:
                st.write(f"Excellent choice! Let's plan your path to becoming a {selected_career}")
                
        elif st.session_state.chosen_path == "gap_year":
            st.write("### What would you like to do during your gap year?")
            selected_option = st.selectbox("Select an option:", load_gap_year_options())
            if selected_option:
                st.write(f"Great plan! Let's make the most of your gap year with {selected_option}")

def show_explore_path():
    st.write("## Let's explore your options!")
    st.write("We'll help you discover different paths based on your interests and skills.")
    
    # Interest assessment
    st.write("### What interests you the most?")
    interests = {
        "Technology": "💻",
        "Science": "🔬",
        "Arts": "🎨",
        "Business": "📈",
        "Healthcare": "⚕️",
        "Aviation": "✈️",
        "Military": "🪖",
        "Education": "📚",
        "Sports": "⚽",
        "Nature": "🌲"
    }
    
    selected_interests = st.multiselect(
        "Select your interests (choose up to 3):",
        list(interests.keys()),
        format_func=lambda x: f"{x} {interests[x]}"
    )
    
    if len(selected_interests) > 0:
        st.write("### Based on your interests, you might want to explore:")
        
        for interest in selected_interests:
            st.write(f"#### {interest} {interests[interest]}")
            if interest == "Aviation":
                st.write("- ✈️ Commercial Pilot")
                st.write("- 🛩️ Aircraft Mechanic")
                st.write("- 🗼 Air Traffic Controller")
            elif interest == "Military":
                st.write("- 🪖 Military Officer")
                st.write("- 🛡️ Military Aviation")
                st.write("- 🏥 Military Medical Corps")
            elif interest == "Technology":
                st.write("- 💻 Software Engineer")
                st.write("- 🤖 AI/ML Engineer")
                st.write("- 🔒 Cybersecurity Specialist")
            elif interest == "Healthcare":
                st.write("- 👨‍⚕️ Doctor")
                st.write("- 👩‍⚕️ Nurse")
                st.write("- 🧬 Medical Researcher")
            # Add more career suggestions for other interests
            
        st.write("### Want to learn more about any of these paths?")
        st.write("Select a path above to see detailed information about:")
        st.write("- 📚 Required Education")
        st.write("- 💰 Expected Salary")
        st.write("- ⏳ Timeline to Achievement")
        st.write("- 🎯 Next Steps")

def load_pathways_page():
    """Main function to load the pathways page"""
    st.title("Career & Education Pathways")
    
    # Create two main paths with descriptions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### I Know What I Want to Do
        Already have a clear direction? Let's create a detailed plan to help you achieve your goals!
        """)
        if st.button("Yes, let's do this! 🎯", key="known_path", use_container_width=True):
            st.session_state.pathway_choice = "known"
            
    with col2:
        st.markdown("""
        ### Help Me Explore My Options
        Not sure yet? Let's discover different paths based on your interests and skills!
        """)
        if st.button("Show me possibilities! 🔍", key="explore_path", use_container_width=True):
            st.session_state.pathway_choice = "explore"
    
    # Show the appropriate content based on the user's choice
    if "pathway_choice" in st.session_state:
        st.write("---")
        if st.session_state.pathway_choice == "known":
            show_known_path()
        else:
            show_explore_path()

# Execute the main function when the page is loaded
if __name__ == "__main__":
    load_pathways_page() 