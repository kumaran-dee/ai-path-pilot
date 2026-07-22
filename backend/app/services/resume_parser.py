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
  "PersonalInformation": {{
    "FullName": "",
    "DateOfBirth": null,
    "Gender": null,
    "Nationality": null,
    "CurrentLocation": null
  }},

  "ContactDetails": {{
    "Email": "",
    "Phone": "",
    "LinkedIn": "",
    "GitHub": "",
    "Portfolio": "",
    "Website": "",
    "Address": null
  }},

  "Education": [
    {{
      "Degree": "",
      "Specialization": "",
      "Institution": "",
      "University": "",
      "CGPA": "",
      "Percentage": "",
      "StartYear": "",
      "EndYear": ""
    }}
  ],

  "Experience": [
    {{
      "Company": "",
      "Role": "",
      "EmploymentType": "",
      "Duration": "",
      "Responsibilities": []
    }}
  ],

  "Skills": [],

  "TechnicalSkills": [],

  "SoftSkills": [],

  "Projects": [
    {{
      "Title": "",
      "Description": "",
      "TechnologiesUsed": [],
      "GitHub": "",
      "LiveDemo": ""
    }}
  ],

  "Certifications": [
    {{
      "Name": "",
      "Organization": "",
      "Year": ""
    }}
  ],

  "Achievements": [],

  "Research": [
    {{
      "Title": "",
      "Publication": "",
      "Year": ""
    }}
  ],

  "Languages": [],

  "CareerDomain": "",

  "PreferredRoles": [],

  "ResumeScore": 0,

  "CareerReadiness": 0,

  "AdditionalMetadata": {{
    "ResumePages": 0,
    "DetectedSections": [],
    "Keywords": [],
    "PrimaryProgrammingLanguages": [],
    "Frameworks": [],
    "Databases": [],
    "CloudPlatforms": [],
    "Tools": [],
    "VersionControl": [],
    "OperatingSystems": []
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
        personal_info = profile.get("PersonalInformation") or {}
        contact = profile.get("ContactDetails") or {}
        
        profile["FullName"] = personal_info.get("FullName") or ""
        profile["ResumeScore"] = profile.get("ResumeScore") or 0
        profile["CareerReadinessScore"] = profile.get("CareerReadiness") or 0
        profile["Skills"] = profile.get("Skills") or []
        
        tech_skills = profile.get("TechnicalSkills") or []
        profile["TechnicalSkills"] = tech_skills if isinstance(tech_skills, list) else []
        profile["SoftSkills"] = profile.get("SoftSkills") or []
        
        profile["Education"] = profile.get("Education") or []
        profile["Experience"] = profile.get("Experience") or []
        profile["Projects"] = profile.get("Projects") or []
        profile["Certifications"] = profile.get("Certifications") or []
        profile["Achievements"] = profile.get("Achievements") or []
        profile["Research"] = profile.get("Research") or []
        profile["Languages"] = profile.get("Languages") or []
        profile["Interests"] = [] # Not explicitly in new schema
        
        c_domain = profile.get("CareerDomain") or ""
        profile["CareerDomain"] = ", ".join(c_domain) if isinstance(c_domain, list) else str(c_domain)
        pref_roles = profile.get("PreferredRoles") or ""
        profile["PreferredRole"] = ", ".join(pref_roles) if isinstance(pref_roles, list) else str(pref_roles)
        profile["PreferredRoles"] = pref_roles if isinstance(pref_roles, list) else [str(pref_roles)]
        
        profile["EmailAddress"] = contact.get("Email") or ""
        profile["PhoneNumber"] = contact.get("Phone") or ""
        profile["Location"] = contact.get("Address") or personal_info.get("CurrentLocation") or ""
        profile["LinkedInURL"] = contact.get("LinkedIn") or ""
        profile["GitHubURL"] = contact.get("GitHub") or ""
        profile["PortfolioURL"] = contact.get("Portfolio") or ""
            
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
