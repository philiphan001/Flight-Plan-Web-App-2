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
        prompt = f"""You're a friendly financial mentor talking to a high school student about their future financial plan. 
        Keep your response fun, encouraging, and relatable to teens! Use emojis and casual language, but maintain 
        professionalism when discussing money. Think of yourself as a cool older sibling giving advice.

        Here's their plan "{scenario['name']}":
        - They want to work as a {scenario['occupation']} in {scenario['location']}
        - They're aiming for a final net worth of ${scenario['final_net_worth']:,}
        - Investment return rate: {scenario['investment_rate']}%

        Their life milestones:{milestone_summary}

        Please give them:
        1. A quick, exciting overview of their journey (1-2 sentences)
        2. One thing that's super smart about their plan (use a 🌟 emoji)
        3. One cool tip to make their plan even better (use a 💡 emoji)
        4. A fun, encouraging closing statement about their future

        Keep it short and snappy - around 100 words total. Make it feel like a text message from a mentor!
        Focus on making the financial journey sound exciting while keeping it realistic.
        """

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are an encouraging mentor helping high school students plan their financial future. Keep responses upbeat and engaging!"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Unable to generate assessment at this time: {str(e)}"