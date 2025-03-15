import os
from typing import Dict, List, Optional
from openai import OpenAI
import json
from datetime import datetime, timedelta

class CareerSuggestionService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    def generate_career_suggestions(
        self,
        interests: List[str],
        skills: List[str],
        education_level: str,
        preferred_work_style: str,
        preferred_industry: Optional[str] = None,
        salary_expectation: Optional[str] = None
    ) -> str:
        """
        Generate career suggestions based on user inputs using OpenAI's API.
        Returns a JSON string.
        """
        prompt = self._create_prompt(
            interests, skills, education_level,
            preferred_work_style, preferred_industry,
            salary_expectation
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better career analysis
                messages=[
                    {"role": "system", "content": """You are a career counselor helping to create detailed career paths. 
                    Format your response as JSON with the following structure:
                    {
                        "primary_path": {
                            "title": "Main career path title",
                            "description": "Brief description",
                            "timeline": [
                                {
                                    "year": 2025,
                                    "milestone": "Start position",
                                    "skills_needed": ["skill1", "skill2"],
                                    "estimated_salary": "salary range"
                                }
                            ]
                        },
                        "alternative_paths": [
                            {
                                "title": "Alternative career path",
                                "description": "Brief description",
                                "timeline": []
                            }
                        ]
                    }"""},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )

            # Return the response content as a string - it's already JSON formatted
            return response.choices[0].message.content

        except Exception as e:
            # Return error as a JSON string
            return json.dumps({
                "error": f"Failed to generate career suggestions: {str(e)}"
            })

    def _create_prompt(
        self,
        interests: List[str],
        skills: List[str],
        education_level: str,
        preferred_work_style: str,
        preferred_industry: Optional[str],
        salary_expectation: Optional[str]
    ) -> str:
        """
        Create a detailed prompt for the OpenAI API.
        """
        current_year = datetime.now().year
        prompt = f"""Based on the following information, suggest a detailed career path with timeline from {current_year} to {current_year + 10}:

        Interests: {', '.join(interests)}
        Current Skills: {', '.join(skills)}
        Education Level: {education_level}
        Preferred Work Style: {preferred_work_style}
        """

        if preferred_industry:
            prompt += f"\nPreferred Industry: {preferred_industry}"
        if salary_expectation:
            prompt += f"\nSalary Expectation: {salary_expectation}"

        prompt += """\n\nProvide a detailed career progression timeline including:
        1. Starting position and subsequent role advancements
        2. Required skills and certifications for each stage
        3. Estimated timeline for transitions
        4. Salary ranges for each position
        5. Alternative career paths that leverage the same skill set

        Format the response as a JSON object with a primary career path and alternative options."""

        return prompt

    def get_skill_recommendations(self, career_path: str) -> str:
        """
        Get specific skill recommendations for a given career path.
        Returns a JSON string.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a career development expert. Provide specific, actionable skill recommendations."},
                    {"role": "user", "content": f"What are the most important skills to develop for a career in {career_path}? Include both technical and soft skills."}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )

            return response.choices[0].message.content
        except Exception as e:
            return json.dumps({
                "error": f"Error getting skill recommendations: {str(e)}"
            })