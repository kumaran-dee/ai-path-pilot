import os
import json
import urllib.request
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY is not set. Using fallback mock responses.")

    def generate_content(self, prompt: str) -> str:
        if not self.api_key:
            # Fallback mock response when no API key is provided
            if "GitHub" in prompt:
                return '{"score": 85}'
            return '{"username": "Analyzed Profile", "score": 75}'
            
        # Use raw HTTP request to bypass protobuf/Python 3.14 crashes!
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={self.api_key}"
        
        data = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}]
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                # Extract text from the Gemini API response
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return '{"username": "API Error", "score": 0}'
        
    def extract_resume_data(self, text: str) -> dict:
        prompt = f"""
        Extract the following information from the resume text below.
        Return ONLY a raw JSON object (without markdown code blocks) matching this schema exactly.
        If a field is missing or not applicable, return null or an empty array/string as appropriate.
        
        {{
            "FullName": "string",
            "EmailAddress": "string",
            "PhoneNumber": "string",
            "LinkedInProfile": "string",
            "GitHubProfile": "string",
            "PortfolioWebsite": "string",
            "CurrentLocation": "string",
            "CareerObjective": "string",
            "TotalExperienceYears": "string",
            "EducationDetails": ["string"],
            "TechnicalSkills": ["string"],
            "ProgrammingLanguages": ["string"],
            "FrameworksAndLibraries": ["string"],
            "ToolsAndTechnologies": ["string"],
            "Databases": ["string"],
            "CloudPlatforms": ["string"],
            "SoftSkills": ["string"],
            "Projects": [ {{"Title": "string", "Description": "string", "TechnologiesUsed": ["string"]}} ],
            "Internships": ["string"],
            "WorkExperience": ["string"],
            "Certifications": ["string"],
            "Achievements": ["string"],
            "ResearchPublications": ["string"],
            "LanguagesKnown": ["string"],
            "Interests": ["string"],
            "CareerDomain": "string",
            "PreferredRoles": ["string"]
        }}
        
        Resume Text:
        {text}
        """
        response_text = self.generate_content(prompt)
        try:
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            return json.loads(response_text.strip())
        except Exception as e:
            print("Failed to parse JSON from Gemini:", str(e))
            return {}

    def compare_resume_to_job(self, resume_text: str, job_text: str) -> dict:
        prompt = f"""
        Act as an expert Technical Recruiter and Career Coach. You are given a candidate's resume and a job description.
        Evaluate how well the candidate fits the job.
        
        Resume:
        {resume_text[:3000]}
        
        Job Description:
        {job_text[:3000]}
        
        Return ONLY a raw JSON object (without markdown code blocks) matching this schema exactly:
        {{
            "resume_score": 95,
            "career_readiness": 91,
            "match_score": 89,
            "matched_skills": ["string", "string"],
            "missing_skills": ["string", "string"],
            "resume_improvements": ["string", "string"],
            "recommended_courses": ["string", "string"],
            "learning_roadmap": ["string", "string"],
            "should_apply": "YES/MAYBE/NO",
            "reason": "Explain WHY they should or should not apply in a brief paragraph."
        }}
        """
        response_text = self.generate_content(prompt)
        try:
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            return json.loads(response_text.strip())
        except Exception as e:
            print("Failed to parse JSON from Gemini (Compare):", str(e))
            return {
                "resume_score": 0,
                "career_readiness": 0,
                "match_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "resume_improvements": [],
                "recommended_courses": [],
                "learning_roadmap": [],
                "should_apply": "NO",
                "reason": "Error analyzing the match."
            }

    def generate_roadmap(self, missing_skills: list) -> dict:
        skills_str = ", ".join(missing_skills)
        prompt = f"""
        Act as an expert Technical Mentor. The candidate needs to learn the following missing skills to land their target job: {skills_str}.
        Create a step-by-step learning roadmap to master these skills.
        
        Return ONLY a raw JSON object (without markdown code blocks) matching this schema exactly:
        {{
            "roadmap": [
                {{
                    "id": 1,
                    "title": "string (e.g., Advanced React Patterns)",
                    "duration": "string (e.g., 2 weeks)",
                    "status": "pending",
                    "description": "string (A brief 1-sentence description of what to learn)"
                }}
            ]
        }}
        """
        response_text = self.generate_content(prompt)
        try:
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            return json.loads(response_text.strip())
        except Exception as e:
            print("Failed to parse JSON from Gemini (Roadmap):", str(e))
            return {"roadmap": []}

# Initialize a singleton instance
gemini_service = GeminiService()
