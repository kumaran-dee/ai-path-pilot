import os
import json
import tempfile
import pdfplumber
import docx
from werkzeug.utils import secure_filename
from flask import Blueprint, request
from app.utilities.response import success_response, error_response
from app.services.gemini_service import gemini_service

bp = Blueprint('resume', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

@bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return error_response("No file part in the request", 400)

    file = request.files['file']
    if file.filename == '':
        return error_response("No selected file", 400)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(tempfile.gettempdir(), filename)
        file.save(filepath)

        try:
            # 1. Extract raw text
            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'pdf':
                raw_text = extract_text_from_pdf(filepath)
            else:
                raw_text = extract_text_from_docx(filepath)

            if not raw_text.strip():
                return error_response("Could not extract text. The file may be scanned or corrupted.", 422)

            # 2. Send to Gemini for structured extraction
            prompt = f"""
You are an expert resume parser. Extract ALL the following information from the resume text below.
Return ONLY a valid JSON object (no markdown code blocks, no backticks, no extra text).

Schema:
{{
    "FullName": "string",
    "EmailAddress": "string",
    "PhoneNumber": "string",
    "LinkedInURL": "string or null",
    "GitHubURL": "string or null",
    "PortfolioURL": "string or null",
    "Location": "string or null",
    "Skills": ["list of all skills"],
    "TechnicalSkills": ["programming languages, frameworks, tools, databases, etc."],
    "SoftSkills": ["communication, teamwork, leadership, etc."],
    "Languages": ["spoken/written languages and proficiency level"],
    "Education": [
        {{
            "Degree": "string",
            "Institution": "string",
            "FieldOfStudy": "string",
            "Year": "string",
            "CGPA": "string or null"
        }}
    ],
    "Experience": [
        {{
            "Title": "string",
            "Company": "string",
            "Duration": "string",
            "Description": "string"
        }}
    ],
    "Projects": [
        {{
            "Title": "string",
            "Description": "string",
            "TechnologiesUsed": ["list"],
            "Link": "string or null"
        }}
    ],
    "Certifications": ["list of certifications with issuer if available"],
    "Achievements": ["list of awards, honors, recognitions"],
    "Research": ["list of research papers, publications, or presentations"],
    "VolunteerWork": ["list of volunteer or extracurricular activities"],
    "Interests": ["hobbies and interests"],
    "CareerDomain": "primary career domain (e.g. Software Engineering, Data Science)",
    "PreferredRoles": ["list of target job roles based on the resume"],
    "YearsOfExperience": "number or '0 (Student/Fresher)'",
    "ResumeScore": integer between 1-100,
    "CareerReadinessScore": integer between 1-100,
    "ResumeStrengths": ["2-3 key strengths of this resume"],
    "ResumeWeaknesses": ["2-3 areas for improvement in this resume"]
}}

Resume Text:
{raw_text}
"""
            response_text = gemini_service.generate_content(prompt)

            # 3. Clean and parse JSON
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            structured_data = json.loads(cleaned)
            structured_data["_filename"] = filename
            structured_data["_source"] = "Extracted from uploaded resume via Gemini AI"

            # 4. Try to save to DB (non-blocking — Vercel may reset DB between invocations)
            try:
                from app.extensions import db
                from app.models.resume import Resume
                from app.models.user import User
                user_id = 1
                user = User.query.get(user_id)
                if not user:
                    user = User(id=user_id, username='testuser', email='test@example.com', password_hash='mock')
                    db.session.add(user)
                    db.session.flush()

                resume_record = Resume.query.filter_by(user_id=user_id).first()
                if resume_record:
                    resume_record.filename = filename
                    resume_record.parsed_json = structured_data
                    resume_record.score = float(structured_data.get("ResumeScore", 0))
                    resume_record.readiness = str(structured_data.get("CareerReadinessScore", 0))
                else:
                    resume_record = Resume(
                        user_id=user_id,
                        filename=filename,
                        parsed_json=structured_data,
                        score=float(structured_data.get("ResumeScore", 0)),
                        readiness=str(structured_data.get("CareerReadinessScore", 0))
                    )
                    db.session.add(resume_record)
                db.session.commit()
            except Exception as db_err:
                print(f"DB save skipped (non-critical): {db_err}")

            # 5. Return the structured data directly in the response
            # The frontend stores this in localStorage for the Detailed Resume viewer
            return success_response("Resume analyzed successfully.", structured_data)

        except json.JSONDecodeError as je:
            return error_response(f"AI returned invalid JSON. Please try again. Details: {str(je)}", 500)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return error_response(f"Failed to parse resume: {str(e)}", 500)

    return error_response("File type not allowed. Please upload PDF or DOCX.", 400)


@bp.route('/analyze', methods=['GET'])
def analyze_resume():
    return success_response("Analyze resume stub")


@bp.route('/details', methods=['GET'])
def get_resume_details():
    """
    Try DB first; if the table is missing or empty (Vercel resets SQLite per invocation),
    return 404 so the frontend can fall back to localStorage.
    """
    try:
        from app.extensions import db
        from app.models.resume import Resume
        user_id = 1
        resume_record = Resume.query.filter_by(user_id=user_id).first()
        if resume_record and resume_record.parsed_json:
            return success_response("Resume details retrieved.", resume_record.parsed_json)
        return error_response("No extracted resume data found. Please upload a resume first.", 404)
    except Exception as e:
        # Table may not exist yet on a fresh Vercel invocation — clean 404 for frontend
        return error_response("No extracted resume data found. Please upload a resume first.", 404)
