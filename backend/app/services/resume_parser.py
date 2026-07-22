import pypdf
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


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

You are an expert ATS Resume Parser.

Read the following resume carefully.

Extract every possible detail.

Return ONLY VALID JSON.

JSON Schema:

{{
"personal_information": {{
"full_name":"",
"career_summary":"",
"current_status":""
}},

"contact_details": {{
"email":"",
"phone":"",
"location":"",
"linkedin":"",
"github":"",
"portfolio":""
}},

"education":[],

"experience":[],

"skills":[],

"technical_skills": {{
"programming_languages":[],
"frameworks":[],
"libraries":[],
"tools":[],
"databases":[],
"cloud_platforms":[]
}},

"soft_skills":[],

"projects":[],

"certifications":[],

"achievements":[],

"research":[],

"languages":[],

"interests":[],

"career_domain":[],

"preferred_roles":[],

"resume_score":0,

"career_readiness": {{
"overall_score":0,
"level":"",
"strengths":[],
"areas_to_improve":[]
}},

"additional_metadata": {{
"skills_count":0,
"projects_count":0,
"experience_count":0
}}
}}

Rules:

Return JSON ONLY.

Do not explain anything.

If information is missing, use null or [].

Resume:

{resume_text}

"""

        response = model.generate_content(prompt)

        result = response.text

        result = result.replace("```json","")
        result = result.replace("```","")

        profile = json.loads(result)

        # ── Inject compatibility keys for front-end rendering ──
        profile["FullName"] = profile.get("personal_information", {}).get("full_name") or ""
        profile["ResumeScore"] = profile.get("resume_score", 0)
        profile["CareerReadinessScore"] = profile.get("career_readiness", {}).get("overall_score") or 0
        profile["Skills"] = profile.get("skills", [])
        
        tech_skills_dict = profile.get("technical_skills", {})
        all_tech_skills = []
        if isinstance(tech_skills_dict, dict):
            for k, v in tech_skills_dict.items():
                if isinstance(v, list):
                    all_tech_skills.extend(v)
        profile["TechnicalSkills"] = all_tech_skills
        profile["SoftSkills"] = profile.get("soft_skills", [])
        
        profile["Education"] = profile.get("education", [])
        profile["Experience"] = profile.get("experience", [])
        profile["Projects"] = profile.get("projects", [])
        profile["Certifications"] = profile.get("certifications", [])
        profile["Achievements"] = profile.get("achievements", [])
        profile["Research"] = profile.get("research", [])
        profile["Languages"] = profile.get("languages", [])
        profile["Interests"] = profile.get("interests", [])
        
        c_domain = profile.get("career_domain", "")
        profile["CareerDomain"] = ", ".join(c_domain) if isinstance(c_domain, list) else str(c_domain)
        pref_roles = profile.get("preferred_roles", "")
        profile["PreferredRole"] = ", ".join(pref_roles) if isinstance(pref_roles, list) else str(pref_roles)
        profile["PreferredRoles"] = pref_roles if isinstance(pref_roles, list) else [str(pref_roles)]
        
        contact = profile.get("contact_details", {})
        if isinstance(contact, dict):
            profile["EmailAddress"] = contact.get("email") or ""
            profile["PhoneNumber"] = contact.get("phone") or ""
            profile["Location"] = contact.get("location") or ""
            profile["LinkedInURL"] = contact.get("linkedin") or ""
            profile["GitHubURL"] = contact.get("github") or ""
            profile["PortfolioURL"] = contact.get("portfolio") or ""
            
        profile["YearsOfExperience"] = profile.get("years_of_experience") or "0 (Student/Fresher)"
        profile["ResumeStrengths"] = profile.get("career_readiness", {}).get("strengths", [])
        profile["ResumeWeaknesses"] = profile.get("career_readiness", {}).get("areas_to_improve", [])

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