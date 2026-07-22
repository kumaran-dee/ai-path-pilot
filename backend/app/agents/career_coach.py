from app.services.gemini_service import gemini_service
import json

class CareerCoach:
    def generate_plan(self, user_profile, missing_skills):
        prompt = f"""
        Act as an AI Career Coach. Generate a personalized weekly and monthly learning plan.
        Return ONLY a raw JSON object (without markdown) matching this exact schema:
        {{
            "Weekly Plan": ["string"],
            "Monthly Plan": ["string"],
            "Project Ideas": ["string"],
            "Recommended Certifications": ["string"],
            "Interview Preparation": ["string"],
            "Resume Improvements": ["string"],
            "Career Guidance": "string"
        }}
        
        User Profile: {user_profile}
        Missing Skills to Focus On: {missing_skills}
        """
        response_text = gemini_service.generate_content(prompt)
        try:
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            return json.loads(response_text.strip())
        except Exception as e:
            print("Failed to parse Career Coach JSON:", str(e))
            return {}

career_coach = CareerCoach()
