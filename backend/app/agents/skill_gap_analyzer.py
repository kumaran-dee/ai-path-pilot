from app.services.gemini_service import gemini_service
import json

class SkillGapAnalyzer:
    def analyze(self, user_skills, job_requirements):
        prompt = f"""
        Compare the user's skills with the job requirements and perform a skill gap analysis.
        Return ONLY a raw JSON object (without markdown) matching this exact schema:
        {{
            "Matched Skills": ["string"],
            "Missing Skills": ["string"],
            "Career Readiness Score": 80,
            "Recommended Courses": ["string"],
            "Suggested Projects": ["string"],
            "Learning Roadmap": "string"
        }}
        
        User Skills: {user_skills}
        Job Requirements: {job_requirements}
        """
        response_text = gemini_service.generate_content(prompt)
        try:
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            return json.loads(response_text.strip())
        except Exception as e:
            print("Failed to parse Skill Gap JSON:", str(e))
            return {}

skill_gap_analyzer = SkillGapAnalyzer()
