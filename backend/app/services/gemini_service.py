import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
        
    def extract_resume_data(self, text: str) -> dict:
        prompt = f"""
        Extract the following information from the resume text below.
        Return ONLY a raw JSON object (without markdown code blocks) matching this schema exactly:
        {{
            "Name": "string",
            "Skills": ["string"],
            "Projects": [ {{"title": "string", "description": "string"}} ],
            "Education": ["string"],
            "Certifications": ["string"],
            "Experience": ["string"],
            "Interests": ["string"],
            "Career Domain": "string",
            "Resume Score": 85,
            "Career Readiness": "string"
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

# Initialize a singleton instance
gemini_service = GeminiService()
