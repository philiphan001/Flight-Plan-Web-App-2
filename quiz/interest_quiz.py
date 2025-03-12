import streamlit as st
import time
import random
from typing import List, Dict, Tuple

class InterestQuiz:
    def __init__(self):
        self.questions = [
            {
                "id": 1,
                "text": "Would you rather...",
                "option_a": "Solve a complex puzzle 🧩",
                "option_b": "Create artwork 🎨",
                "traits_a": ["analytical", "logical"],
                "traits_b": ["creative", "artistic"]
            },
            {
                "id": 2,
                "text": "Which sounds more fun?",
                "option_a": "Leading a team project 👥",
                "option_b": "Working independently on a challenge 🎯",
                "traits_a": ["leadership", "social"],
                "traits_b": ["independent", "focused"]
            },
            {
                "id": 3,
                "text": "What interests you more?",
                "option_a": "Understanding how things work 🔧",
                "option_b": "Helping others learn and grow 🌱",
                "traits_a": ["technical", "analytical"],
                "traits_b": ["nurturing", "social"]
            },
            {
                "id": 4,
                "text": "Which activity appeals to you?",
                "option_a": "Building something with your hands 🛠️",
                "option_b": "Writing stories or articles ✍️",
                "traits_a": ["practical", "technical"],
                "traits_b": ["creative", "communicative"]
            },
            {
                "id": 5,
                "text": "What would you prefer?",
                "option_a": "Analyzing data and trends 📊",
                "option_b": "Performing or presenting 🎭",
                "traits_a": ["analytical", "detail-oriented"],
                "traits_b": ["expressive", "social"]
            }
        ]

        self.career_mappings = {
            "analytical": ["Data Scientist", "Financial Analyst", "Research Scientist"],
            "logical": ["Software Engineer", "Mathematician", "Systems Analyst"],
            "creative": ["Graphic Designer", "Art Director", "Product Designer"],
            "artistic": ["Multimedia Artist", "Fashion Designer", "Interior Designer"],
            "leadership": ["Project Manager", "Business Executive", "Entrepreneur"],
            "social": ["Teacher", "Human Resources Manager", "Social Worker"],
            "independent": ["Freelance Consultant", "Writer", "Software Developer"],
            "focused": ["Surgeon", "Air Traffic Controller", "Research Scientist"],
            "technical": ["Engineer", "IT Specialist", "Architect"],
            "nurturing": ["Nurse", "Counselor", "Veterinarian"],
            "practical": ["Construction Manager", "Mechanic", "Chef"],
            "communicative": ["Journalist", "Public Relations Specialist", "Marketing Manager"],
            "detail-oriented": ["Accountant", "Quality Assurance Specialist", "Editor"],
            "expressive": ["Actor", "Music Teacher", "Public Speaker"]
        }

    def show_animated_question(self, question: Dict) -> Tuple[str, List[str]]:
        st.markdown(f"""
        <div class='quiz-question' style='text-align: center; padding: 20px;'>
            <h2>{question['text']}</h2>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        selected_traits = []
        with col1:
            if st.button(question['option_a'], key=f"q{question['id']}_a", 
                        help="Click to choose this option"):
                selected_traits = question['traits_a']
                return "a", selected_traits

        with col2:
            if st.button(question['option_b'], key=f"q{question['id']}_b",
                        help="Click to choose this option"):
                selected_traits = question['traits_b']
                return "b", selected_traits

        return None, []

    def show_progress(self, current: int, total: int):
        progress = current / total
        st.progress(progress)
        st.markdown(f"Question {current} of {total}")

    def calculate_results(self, traits: List[str]) -> Dict[str, int]:
        trait_counts = {}
        for trait in traits:
            if trait in trait_counts:
                trait_counts[trait] += 1
            else:
                trait_counts[trait] = 1
        return trait_counts

    def get_career_suggestions(self, traits: List[str], num_suggestions: int = 3) -> List[str]:
        suggestions = set()
        for trait in traits:
            if trait in self.career_mappings:
                suggestions.update(self.career_mappings[trait])
        return list(suggestions)[:num_suggestions]

    def show_results_animation(self, traits: List[str], career_suggestions: List[str]):
        st.markdown("""
        <div style='text-align: center;'>
            <h2>🎉 Your Results Are In! 🎉</h2>
        </div>
        """, unsafe_allow_html=True)

        # Animate traits appearing
        st.markdown("### Your Top Traits:")
        for trait in set(traits):
            st.markdown(f"✨ {trait.title()}")
            time.sleep(0.5)

        # Show career suggestions with animation
        st.markdown("### Suggested Career Paths:")
        for career in career_suggestions:
            st.markdown(f"""
            <div class='career-suggestion' style='
                padding: 10px;
                margin: 5px;
                background-color: #f0f8ff;
                border-radius: 10px;
                text-align: center;
                animation: slideIn 0.5s ease-out;
            '>
                🚀 {career}
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.5)

def run_quiz():
    st.markdown("""
    <style>
        @keyframes slideIn {
            from {
                transform: translateX(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        .quiz-question {
            animation: fadeIn 1s ease-in;
        }
        .career-suggestion {
            transition: all 0.3s ease;
        }
        .career-suggestion:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize quiz state
    if 'quiz' not in st.session_state:
        st.session_state.quiz = InterestQuiz()
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'selected_traits' not in st.session_state:
        st.session_state.selected_traits = []
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

    quiz = st.session_state.quiz

    if not st.session_state.quiz_completed:
        if st.session_state.current_question < len(quiz.questions):
            st.markdown("""
                <h1 style='text-align: center;'>Discover Your Interests 🌟</h1>
                <p style='text-align: center; font-size: 1.2rem;'>
                    Choose the option that appeals to you more!
                </p>
            """, unsafe_allow_html=True)

            quiz.show_progress(st.session_state.current_question + 1, len(quiz.questions))

            choice, traits = quiz.show_animated_question(
                quiz.questions[st.session_state.current_question]
            )

            if choice:
                st.session_state.selected_traits.extend(traits)
                st.session_state.current_question += 1
                st.rerun()

        else:
            st.session_state.quiz_completed = True
            career_suggestions = quiz.get_career_suggestions(st.session_state.selected_traits)
            quiz.show_results_animation(st.session_state.selected_traits, career_suggestions)

            if st.button("Start Over"):
                st.session_state.current_question = 0
                st.session_state.selected_traits = []
                st.session_state.quiz_completed = False
                st.rerun()