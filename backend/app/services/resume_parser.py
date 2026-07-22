import pypdf
import urllib.request
import json
import os
class ResumeParser:

    def extract_text(self, pdf_path):
        text = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
        return text

    def extract_candidate_profile(self, resume_text):

        prompt = f"""
You are an advanced ATS Resume Parser and AI Resume Extraction Agent.

Your task is to analyze the uploaded resume and extract ONLY the information that is explicitly present in the resume.

==========================
STRICT RULES
==========================

1. NEVER invent or assume any information.
2. NEVER generate placeholder values.
3. NEVER infer experience, skills, certifications, projects, or achievements.
4. If a field is not present, return:
   - null for single values
   - [] for arrays
5. Every extracted value must be directly supported by the resume.
6. Do not summarize or rewrite information.
7. Return ONLY valid JSON.
8. Do NOT include markdown or explanations.

==========================
EXTRACT THE FOLLOWING
==========================

{{
  "personal_information": {{
    "full_name": "",
    "date_of_birth": null,
    "gender": null,
    "nationality": null,
    "current_location": null
  }},

  "contact_details": {{
    "email": "",
    "phone": "",
    "linkedin": "",
    "github": "",
    "portfolio": "",
    "website": "",
    "location": null
  }},

  "education": [
    {{
      "degree": "",
      "specialization": "",
      "institution": "",
      "university": "",
      "cgpa": "",
      "percentage": "",
      "start_year": "",
      "end_year": ""
    }}
  ],

  "experience": [
    {{
      "company": "",
      "role": "",
      "employment_type": "",
      "duration": "",
      "responsibilities": []
    }}
  ],

  "skills": [],

  "technical_skills": {{
    "programming_languages": [],
    "frameworks": [],
    "database": [],
    "ai_ml": [],
    "tools": []
  }},

  "soft_skills": [],

  "projects": [
    {{
      "title": "",
      "description": "",
      "technologies_used": [],
      "github": "",
      "live_demo": ""
    }}
  ],

  "certifications": [
    {{
      "name": "",
      "organization": "",
      "year": ""
    }}
  ],

  "achievements": [],

  "research": [
    {{
      "title": "",
      "publication": "",
      "year": ""
    }}
  ],

  "languages": [],

  "career_domain": "",

  "preferred_roles": [],

  "resume_score": 0,

  "career_readiness": 0,

  "additional_metadata": {{
    "resume_pages": 0,
    "detected_sections": [],
    "keywords": [],
    "primary_programming_languages": [],
    "frameworks": [],
    "databases": [],
    "cloud_platforms": [],
    "tools": [],
    "version_control": [],
    "operating_systems": []
  }}
}}

==========================
SCORING RULES
==========================

ResumeScore (0-100):
Evaluate the overall quality of the resume based on:
- Completeness
- Formatting
- Skills
- Projects
- Experience
- Certifications
- ATS Friendliness

CareerReadiness (0-100):
Evaluate the candidate's readiness for internships/jobs considering:
- Skills
- Projects
- Experience
- Education
- Certifications

==========================
IMPORTANT
==========================

Only ResumeScore and CareerReadiness may be AI-evaluated.

Every other field MUST be extracted directly from the resume without assumptions.

Return ONLY the JSON object.

{resume_text}
"""

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY is not set. Using fallback empty profile.")
            result = "{}"
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
            data = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}]
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
            try:
                with urllib.request.urlopen(req) as response:
                    response_data = json.loads(response.read().decode())
                    result = response_data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                print(f"Error calling Gemini REST API: {e}")
                result = "{}"

        result = result.replace("```json","")
        result = result.replace("```","")
        
        try:
            profile = json.loads(result)
        except json.JSONDecodeError:
            profile = {}

        # ── Inject compatibility keys for front-end rendering ──
        personal_info = profile.get("personal_information") or {}
        contact = profile.get("contact_details") or {}
        
        profile["FullName"] = personal_info.get("full_name") or ""
        profile["ResumeScore"] = profile.get("resume_score") or 0
        profile["CareerReadinessScore"] = profile.get("career_readiness") or 0
        profile["Skills"] = profile.get("skills") or []
        
        # Flatten technical_skills if it's a nested dict now
        tech_skills = profile.get("technical_skills") or []
        if isinstance(tech_skills, dict):
            flat_tech = []
            for v in tech_skills.values():
                if isinstance(v, list): flat_tech.extend(v)
            profile["TechnicalSkills"] = flat_tech
        else:
            profile["TechnicalSkills"] = tech_skills if isinstance(tech_skills, list) else []
            
        profile["SoftSkills"] = profile.get("soft_skills") or []
        
        profile["Education"] = profile.get("education") or []
        profile["Experience"] = profile.get("experience") or []
        profile["Projects"] = profile.get("projects") or []
        profile["Certifications"] = profile.get("certifications") or []
        profile["Achievements"] = profile.get("achievements") or []
        profile["Research"] = profile.get("research") or []
        profile["Languages"] = profile.get("languages") or []
        profile["Interests"] = [] # Not explicitly in new schema
        
        c_domain = profile.get("career_domain") or ""
        profile["CareerDomain"] = ", ".join(c_domain) if isinstance(c_domain, list) else str(c_domain)
        pref_roles = profile.get("preferred_roles") or ""
        profile["PreferredRole"] = ", ".join(pref_roles) if isinstance(pref_roles, list) else str(pref_roles)
        profile["PreferredRoles"] = pref_roles if isinstance(pref_roles, list) else [str(pref_roles)]
        
        profile["EmailAddress"] = contact.get("email") or ""
        profile["PhoneNumber"] = contact.get("phone") or ""
        profile["Location"] = contact.get("location") or personal_info.get("current_location") or ""
        profile["LinkedInURL"] = contact.get("linkedin") or ""
        profile["GitHubURL"] = contact.get("github") or ""
        profile["PortfolioURL"] = contact.get("portfolio") or ""
            
        profile["YearsOfExperience"] = "0 (Student/Fresher)" # Derived later usually
        profile["ResumeStrengths"] = []
        profile["ResumeWeaknesses"] = []

        return profile

    def parse_resume(self, filepath, filename):
        text = self.extract_text(filepath)
        return self.extract_candidate_profile(text)


resume_parser = ResumeParser()

if __name__ == "__main__":

    parser = ResumeParser()

    resume_text = parser.extract_text("uploads/resume.pdf")

    profile = parser.extract_candidate_profile(resume_text)

    print(json.dumps(profile, indent=4))
