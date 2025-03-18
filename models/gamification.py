from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str  # SVG icon name
    points: int
    category: str  # e.g., 'savings', 'investment', 'budgeting'
    requirements: Dict[str, float]  # e.g., {'savings_amount': 1000}
    completed: bool = False
    completed_date: Optional[datetime] = None

@dataclass
class LearningModule:
    id: str
    title: str
    description: str
    category: str
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    points: int
    prerequisites: List[str]  # list of module IDs
    completed: bool = False
    quiz_passed: bool = False
    progress: float = 0.0  # percentage complete

class UserProgress:
    def __init__(self):
        self.total_points = 0
        self.achievements: List[Achievement] = []
        self.completed_modules: List[str] = []  # list of module IDs
        self.current_streak: int = 0
        self.badges: List[str] = []
        self.level: int = 1
        self.xp: int = 0

    def add_points(self, points: int):
        self.total_points += points
        self.xp += points
        # Level up every 1000 points
        self.level = (self.xp // 1000) + 1

    def complete_achievement(self, achievement: Achievement):
        if not achievement.completed:
            achievement.completed = True
            achievement.completed_date = datetime.now()
            self.add_points(achievement.points)
            self.achievements.append(achievement)

    def complete_module(self, module: LearningModule):
        if module.id not in self.completed_modules:
            self.completed_modules.append(module.id)
            self.add_points(module.points)

class FinancialGame:
    def __init__(self):
        self.user_progress = UserProgress()
        self.available_achievements = self._initialize_achievements()
        self.learning_modules = self._initialize_modules()

    def _initialize_achievements(self) -> List[Achievement]:
        return [
            Achievement(
                id="first_budget",
                name="Budget Master",
                description="Create your first monthly budget",
                icon="📊",
                points=100,
                category="budgeting",
                requirements={"budget_created": 1}
            ),
            Achievement(
                id="savings_milestone_1",
                name="Savings Pioneer",
                description="Save your first $1,000",
                icon="💰",
                points=200,
                category="savings",
                requirements={"savings_amount": 1000}
            ),
            Achievement(
                id="investment_starter",
                name="Investment Rookie",
                description="Make your first investment",
                icon="📈",
                points=300,
                category="investment",
                requirements={"investment_made": 1}
            )
        ]

    def _initialize_modules(self) -> List[LearningModule]:
        return [
            LearningModule(
                id="basics_budgeting",
                title="Budgeting Basics",
                description="Learn the fundamentals of creating and maintaining a budget",
                category="budgeting",
                difficulty="beginner",
                points=100,
                prerequisites=[]
            ),
            LearningModule(
                id="intro_investing",
                title="Introduction to Investing",
                description="Understand the basics of investing and different investment options",
                category="investing",
                difficulty="beginner",
                points=150,
                prerequisites=["basics_budgeting"]
            ),
            LearningModule(
                id="tax_planning",
                title="Tax Planning Fundamentals",
                description="Learn about tax brackets, deductions, and basic tax planning",
                category="taxes",
                difficulty="intermediate",
                points=200,
                prerequisites=["basics_budgeting"]
            )
        ]

    def check_achievements(self, user_stats: Dict):
        """Check if any achievements have been unlocked based on user stats"""
        for achievement in self.available_achievements:
            if not achievement.completed:
                requirements_met = all(
                    user_stats.get(req, 0) >= value 
                    for req, value in achievement.requirements.items()
                )
                if requirements_met:
                    self.user_progress.complete_achievement(achievement)
                    return achievement

        return None

    def get_available_modules(self) -> List[LearningModule]:
        """Return list of modules available based on prerequisites"""
        return [
            module for module in self.learning_modules
            if all(prereq in self.user_progress.completed_modules 
                  for prereq in module.prerequisites)
        ]

    def update_streak(self, current_date: datetime):
        """Update user's learning streak"""
        # Implement streak logic here
        pass
