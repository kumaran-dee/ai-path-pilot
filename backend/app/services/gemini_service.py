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
            print("WARNING: GEMINI_API_KEY is not set. Using schema-aware mock responses.")

    def generate_content(self, prompt: str) -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("WARNING: GEMINI_API_KEY is not configured. Falling back to mock response.")
            return self._get_mock_response(prompt)
        # Use raw HTTP request to bypass protobuf/Python 3.14 crashes!
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        data = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}]
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                result = json.loads(response.read().decode())
                # Extract text from the Gemini API response
                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                if text.strip():
                    return text
                raise ValueError("Empty response from Gemini API")
        except Exception as e:
            print(f"Gemini API Error: {e}. Falling back to mock response.")
            return self._get_mock_response(prompt)

    def _get_mock_response(self, prompt: str) -> str:
        # Schema-aware mock generation to prevent parsing crashes in modular services
        prompt_lower = prompt.lower()
        
        # 1. Resume Parser
        if "extract the following information from the resume" in prompt_lower or "fullname" in prompt_lower:
            return json.dumps({
                "FullName": "Ashwin Siva",
                "EmailAddress": "ashwin@example.com",
                "PhoneNumber": "+91 98765 43210",
                "Skills": ["Python", "JavaScript", "React", "Node.js", "Express", "Flask", "SQL", "Git", "HTML", "CSS"],
                "TechnicalSkills": ["Python", "JavaScript", "React", "Flask", "SQLite", "REST APIs"],
                "SoftSkills": ["Communication", "Problem Solving", "Team Collaboration"],
                "Education": ["B.E. Computer Science and Engineering"],
                "Experience": ["Full Stack Developer Intern @ TechCorp (3 months)"],
                "Projects": [
                    {
                        "Title": "AI Path Pilot",
                        "Description": "AI-powered career coaching and resume matching platform built with React and Flask.",
                        "TechnologiesUsed": ["React", "Flask", "Gemini API", "SQLite"]
                    }
                ],
                "Certifications": ["Google Cloud Digital Leader"],
                "Achievements": ["First Place in College Hackathon 2025"],
                "Interests": ["Artificial Intelligence", "Open Source Contribution"],
                "CareerDomain": "Software Engineering",
                "PreferredRole": "Full Stack Developer",
                "ResumeScore": 88,
                "CareerReadinessScore": 85
            })

        # 2. Job Parser / Scraper clean
        if "extract only the core job description" in prompt_lower or "companyname" in prompt_lower or "jobrole" in prompt_lower:
            return json.dumps({
                "CompanyName": "Google",
                "JobRole": "Associate Software Engineer",
                "RequiredSkills": ["Python", "JavaScript", "React", "SQL", "Git", "Docker"],
                "PreferredSkills": ["Kubernetes", "AWS Cloud", "NoSQL"],
                "ExperienceRequired": "1+ years of experience or strong internship background",
                "Education": "Bachelor's in Computer Science or equivalent practical experience",
                "Responsibilities": [
                    "Design, develop, and deploy front-end React components.",
                    "Build modular backend REST APIs in Python or Node.js.",
                    "Collaborate with senior engineering mentors and product managers."
                ],
                "Salary": "Competitive Package",
                "Location": "Bangalore / Remote",
                "EmploymentType": "Full-time",
                "ApplicationDeadline": "End of Quarter"
            })

        # 3. Matching Service / ATS
        if "expert applicant tracking system" in prompt_lower or "ats_compatibility" in prompt_lower:
            return json.dumps({
                "overall_match": 85,
                "skill_match": 80,
                "experience_match": 75,
                "education_match": 90,
                "project_relevance": 85,
                "ats_compatibility": 88
            })

        # 4. Skill Gap Service
        if "expert technical mentor" in prompt_lower or "priority_skills" in prompt_lower:
            return json.dumps({
                "matched_skills": ["Python", "JavaScript", "React", "SQL", "Git"],
                "missing_skills": ["Docker", "Kubernetes", "AWS Cloud"],
                "weak_skills": ["Flask", "REST APIs"],
                "strong_skills": ["Python", "React", "SQL"],
                "priority_skills": {
                    "critical": ["Docker"],
                    "recommended": ["AWS Cloud"],
                    "optional": ["Kubernetes"]
                }
            })

        # 5. Recommendation Service
        if "expert recruiter and career advisor" in prompt_lower or "should_apply" in prompt_lower:
            return json.dumps({
                "should_apply": "YES",
                "reason": "You possess 90% of their frontend stack and have a fully realized portfolio project (AI Path Pilot) built with Flask and React. Learning Docker containerization will make your profile an outstanding fit.",
                "resume_improvements": [
                    "Highlight metrics/impact for AI Path Pilot project.",
                    "Incorporate keywords like containerization, REST API optimization, and CI/CD."
                ],
                "missing_keywords": ["Docker", "AWS Cloud", "Kubernetes"],
                "interview_tips": [
                    "Revise standard React custom hooks and state management.",
                    "Prepare to discuss project deployment architecture."
                ],
                "recommended_changes": [
                    "Add a technical skills grid grouping libraries and tools."
                ],
                "career_advice": "Focus on cloud deployment projects to stand out for full stack roles."
            })

        # 6. Roadmap Service
        if "learning roadmap" in prompt_lower or "plan_7_day" in prompt_lower:
            return json.dumps({
                "plan_7_day": [
                    "Day 1-2: Understand Docker containerization basics and install Docker Desktop.",
                    "Day 3-5: Write Dockerfiles for your React and Flask components.",
                    "Day 6-7: Connect them together using a multi-container Docker Compose file."
                ],
                "plan_30_day": [
                    "Week 1-2: Learn AWS basics, set up an EC2 instance, and deploy via Docker.",
                    "Week 3-4: Build a simple automated CI/CD pipeline using GitHub Actions."
                ],
                "recommended_courses": [
                    "Docker & Kubernetes Masterclass by Stephen Grider",
                    "AWS Cloud Practitioner Essentials by Amazon Web Services"
                ],
                "certifications": [
                    "AWS Certified Cloud Practitioner",
                    "Docker Certified Associate"
                ],
                "project_ideas": [
                    "Containerized Microservice Application deployed on AWS EC2."
                ],
                "learning_resources": [
                    "Official Docker Getting Started Guide",
                    "AWS free tier console docs"
                ],
                "interview_prep_plan": [
                    "Practice container lifecycle commands.",
                    "Mock explain project architectural details."
                ]
            })

        # 7. Dashboard Recommendations
        if "expert ai career advisor" in prompt_lower or "career_score" in prompt_lower:
            return json.dumps({
                "career_score": 75,
                "detected_skills": ["Python", "JavaScript", "React"],
                "missing_skills": ["Docker", "AWS"],
                "jobs": ["Frontend Developer", "React Engineer"],
                "internships": ["SWE Intern", "Web Dev Intern"],
                "workshops": ["System Design Basics", "Advanced React"],
                "hackathons": ["Smart India Hackathon", "Global Hack Week"],
                "leetcode_problems": ["Two Sum", "Merge Intervals"]
            })

        # Generic default fallback
        return json.dumps({"score": 85, "username": "Mock User"})

    def extract_resume_data(self, text: str) -> dict:
        # Kept for backward compatibility
        prompt = f"Extract details from: {text}"
        response_text = self.generate_content(prompt)
        try:
            return json.loads(response_text)
        except Exception:
            return {}

    def compare_resume_to_job(self, resume_text: str, job_text: str) -> dict:
        # Kept for backward compatibility
        prompt = f"Compare candidate: {resume_text} vs Job: {job_text}"
        response_text = self.generate_content(prompt)
        try:
            return json.loads(response_text)
        except Exception:
            return {"match_score": 75, "should_apply": "MAYBE"}

    def generate_roadmap(self, missing_skills: list) -> dict:
        # Kept for backward compatibility
        prompt = f"Learning roadmap for: {missing_skills}"
        response_text = self.generate_content(prompt)
        try:
            return json.loads(response_text)
        except Exception:
            return {"roadmap": []}

# Initialize a singleton instance
gemini_service = GeminiService()
