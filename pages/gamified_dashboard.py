import streamlit as st
from models.gamification import FinancialGame
import plotly.graph_objects as go
from datetime import datetime

def show_achievements(game: FinancialGame):
    st.subheader("🏆 Achievements")
    
    # Create three columns for different achievement categories
    col1, col2, col3 = st.columns(3)
    
    categories = {
        "budgeting": col1,
        "savings": col2,
        "investment": col3
    }
    
    for achievement in game.available_achievements:
        with categories.get(achievement.category, col1):
            achievement_card = f"""
            <div style='padding: 10px; border-radius: 10px; background-color: {'#E8F5E9' if achievement.completed else '#F5F5F5'}'>
                <h3>{achievement.icon} {achievement.name}</h3>
                <p>{achievement.description}</p>
                <p>Points: {achievement.points}</p>
                {'✅ Completed!' if achievement.completed else '🔒 Locked'}
            </div>
            """
            st.markdown(achievement_card, unsafe_allow_html=True)

def show_learning_progress(game: FinancialGame):
    st.subheader("📚 Learning Modules")
    
    # Create tabs for different difficulty levels
    tabs = st.tabs(["Beginner", "Intermediate", "Advanced"])
    
    difficulties = {
        "beginner": 0,
        "intermediate": 1,
        "advanced": 2
    }
    
    available_modules = game.get_available_modules()
    
    for module in available_modules:
        with tabs[difficulties[module.difficulty]]:
            module_card = f"""
            <div style='padding: 15px; border-radius: 10px; background-color: {'#E3F2FD' if not module.completed else '#E8F5E9'}'>
                <h3>{module.title}</h3>
                <p>{module.description}</p>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span>Points: {module.points}</span>
                    <span>Progress: {int(module.progress)}%</span>
                </div>
                <div style='background-color: #DDD; height: 10px; border-radius: 5px; margin-top: 10px;'>
                    <div style='background-color: #2196F3; width: {module.progress}%; height: 100%; border-radius: 5px;'></div>
                </div>
            </div>
            """
            st.markdown(module_card, unsafe_allow_html=True)
            
            if not module.completed:
                if st.button(f"Start {module.title}", key=f"start_{module.id}"):
                    st.session_state.current_module = module.id
                    st.rerun()

def show_user_stats(game: FinancialGame):
    st.subheader("📊 Your Progress")
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Level", game.user_progress.level)
    with col2:
        st.metric("Total Points", game.user_progress.total_points)
    with col3:
        st.metric("Current Streak", f"{game.user_progress.current_streak} days")
    with col4:
        st.metric("Completed Modules", len(game.user_progress.completed_modules))
    
    # Create XP progress bar
    xp_to_next_level = (game.user_progress.level * 1000) - game.user_progress.xp
    xp_progress = (game.user_progress.xp % 1000) / 1000
    
    st.markdown("### Level Progress")
    st.progress(xp_progress)
    st.text(f"XP to next level: {xp_to_next_level}")

def show_leaderboard():
    st.subheader("🏅 Leaderboard")
    
    # Placeholder leaderboard data
    leaderboard_data = {
        "Names": ["Alex", "Jordan", "Sam", "Taylor", "Morgan"],
        "Points": [2500, 2300, 2100, 1900, 1800],
        "Level": [3, 3, 2, 2, 2]
    }
    
    # Create a styled leaderboard
    for i, (name, points, level) in enumerate(zip(
        leaderboard_data["Names"],
        leaderboard_data["Points"],
        leaderboard_data["Level"]
    )):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "👤"
        st.markdown(f"""
        <div style='padding: 10px; background-color: {'#FFD700' if i == 0 else '#C0C0C0' if i == 1 else '#CD7F32' if i == 2 else '#F5F5F5'}; 
                    border-radius: 5px; margin: 5px;'>
            {medal} {i+1}. {name} - Level {level} - {points} points
        </div>
        """, unsafe_allow_html=True)

def load_gamified_dashboard():
    st.title("🎮 Financial Learning Dashboard")
    
    # Initialize game state if not exists
    if 'game' not in st.session_state:
        st.session_state.game = FinancialGame()
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Your Progress", "Learning Modules", "Leaderboard"])
    
    with tab1:
        show_user_stats(st.session_state.game)
        show_achievements(st.session_state.game)
    
    with tab2:
        show_learning_progress(st.session_state.game)
    
    with tab3:
        show_leaderboard()

if __name__ == "__main__":
    load_gamified_dashboard()
