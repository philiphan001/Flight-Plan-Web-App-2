"""Service for generating financial planning assessments using OpenAI."""
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_financial_assessment(scenario: dict) -> str:
    """Generate a narrative assessment of a financial scenario using OpenAI."""
    try:
        # Format milestone information
        milestone_summary = ""
        if 'milestones' in scenario:
            for milestone in scenario['milestones']:
                milestone_summary += f"\n- {milestone['name']} in Year {milestone['year']}"
                if milestone['type'] == 'Marriage':
                    milestone_summary += f"\n  * Wedding cost: ${milestone['wedding_cost']:,}"
                    milestone_summary += f"\n  * Spouse occupation: {milestone['spouse_occupation']}"
                elif milestone['type'] == 'HomePurchase':
                    milestone_summary += f"\n  * Home price: ${milestone['home_price']:,}"
                    milestone_summary += f"\n  * Down payment: {milestone['down_payment']}%"
                elif milestone['type'] == 'CarPurchase':
                    milestone_summary += f"\n  * Car price: ${milestone['car_price']:,}"
                    milestone_summary += f"\n  * Vehicle type: {milestone['vehicle_type']}"
                elif milestone['type'] == 'Child':
                    milestone_summary += f"\n  * Monthly education savings: ${milestone['education_savings']/12:,.2f}"
                elif milestone['type'] == 'GraduateSchool':
                    milestone_summary += f"\n  * Total cost: ${milestone['total_cost']:,}"
                    milestone_summary += f"\n  * Expected salary increase: {milestone['salary_increase']}%"

        # Create the prompt
        prompt = f"""Analyze this financial planning scenario and provide a brief, encouraging assessment 
        focusing on the strategic planning and potential areas for optimization. Keep the tone constructive 
        and forward-looking.

        Scenario: {scenario['name']}
        Location: {scenario['location']}
        Occupation: {scenario['occupation']}
        Investment Return Rate: {scenario['investment_rate']}%
        Final Net Worth: ${scenario['final_net_worth']:,}

        Life Milestones:{milestone_summary}

        Please provide:
        1. A brief overview of the financial journey
        2. Strengths in the current plan
        3. 1-2 specific suggestions for optimization
        4. A concluding statement about long-term outlook

        Keep the response concise and conversational, around 200 words.
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a supportive financial advisor providing constructive feedback on life planning scenarios."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Unable to generate assessment at this time: {str(e)}"
