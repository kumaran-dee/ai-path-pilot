import os
import io
import json
import base64
import tempfile
import traceback
from werkzeug.utils import secure_filename
from flask import Blueprint, request
from app.utilities.response import success_response, error_response
from app.services.gemini_service import gemini_service

bp = Blueprint('resume', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Text extraction helpers ───────────────────────────────────────────────

def extract_text_pdfplumber(filepath):
    """Layer 1: pdfplumber (best for text-based PDFs)."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        return text.strip()
    except Exception as e:
        print(f"pdfplumber failed: {e}")
        return ""

def extract_text_pypdf(filepath):
    """Layer 2: pypdf (works on most text-layer PDFs)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception as e:
        print(f"pypdf failed: {e}")
        return ""

def extract_text_docx(filepath):
    """Layer 3: python-docx for .docx files."""
    try:
        import docx as docx_lib
        doc = docx_lib.Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        print(f"python-docx failed: {e}")
        return ""

def extract_via_gemini_vision(file_bytes, filename, mime_type="application/pdf"):
    """
    Layer 4 (ultimate fallback): Send the raw file bytes to Gemini's multimodal API.
    This works for scanned PDFs, image-based PDFs, and unusual encodings.
    """
    import urllib.request
    import os

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return None  # No key → skip, use mock

    b64_data = base64.b64encode(file_bytes).decode("utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"

    prompt_text = f"""
You are an expert resume parser with OCR capabilities.
The attached file is a resume (filename: {filename}).
Extract ALL resume content you can read from it.

Return ONLY a valid JSON object (no markdown, no backticks) with this exact schema:
{{
    "FullName": "string",
    "EmailAddress": "string or null",
    "PhoneNumber": "string or null",
    "LinkedInURL": "string or null",
    "GitHubURL": "string or null",
    "PortfolioURL": "string or null",
    "Location": "string or null",
    "Skills": ["all skills mentioned"],
    "TechnicalSkills": ["programming languages, frameworks, tools, databases"],
    "SoftSkills": ["communication, teamwork, leadership, etc."],
    "Languages": ["spoken/written languages with proficiency"],
    "Education": [
        {{"Degree": "string", "Institution": "string", "FieldOfStudy": "string", "Year": "string", "CGPA": "string or null"}}
    ],
    "Experience": [
        {{"Title": "string", "Company": "string", "Duration": "string", "Description": "string"}}
    ],
    "Projects": [
        {{"Title": "string", "Description": "string", "TechnologiesUsed": ["list"], "Link": "string or null"}}
    ],
    "Certifications": ["list"],
    "Achievements": ["list"],
    "Research": ["list of publications or research work"],
    "VolunteerWork": ["list"],
    "Interests": ["hobbies and interests"],
    "CareerDomain": "primary career domain",
    "PreferredRoles": ["target job roles based on resume content"],
    "YearsOfExperience": "number or 0 (Student/Fresher)",
    "ResumeScore": 85,
    "CareerReadinessScore": 80,
    "ResumeStrengths": ["2-3 key strengths"],
    "ResumeWeaknesses": ["2-3 areas to improve"]
}}
"""

    payload = json.dumps({
        "contents": [{
            "parts": [
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": b64_data
                    }
                },
                {"text": prompt_text}
            ]
        }]
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            raw = result['candidates'][0]['content']['parts'][0]['text']
            raw = raw.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
            return json.loads(raw)
    except Exception as e:
        print(f"Gemini Vision extraction failed: {e}")
        return None


def gemini_text_to_profile(raw_text, filename):
    """Send extracted text to Gemini to get structured JSON profile."""
    prompt = f"""
You are an expert resume parser. Extract ALL the following information from the resume text below.
Return ONLY a valid JSON object (no markdown, no backticks, no extra text).

Schema:
{{
    "FullName": "string",
    "EmailAddress": "string or null",
    "PhoneNumber": "string or null",
    "LinkedInURL": "string or null",
    "GitHubURL": "string or null",
    "PortfolioURL": "string or null",
    "Location": "string or null",
    "Skills": ["all skills mentioned"],
    "TechnicalSkills": ["programming languages, frameworks, tools, databases, etc."],
    "SoftSkills": ["communication, teamwork, leadership, etc."],
    "Languages": ["spoken/written languages and proficiency"],
    "Education": [
        {{"Degree": "string", "Institution": "string", "FieldOfStudy": "string", "Year": "string", "CGPA": "string or null"}}
    ],
    "Experience": [
        {{"Title": "string", "Company": "string", "Duration": "string", "Description": "string"}}
    ],
    "Projects": [
        {{"Title": "string", "Description": "string", "TechnologiesUsed": ["list"], "Link": "string or null"}}
    ],
    "Certifications": ["list of certifications with issuer"],
    "Achievements": ["awards, honors, recognitions"],
    "Research": ["research papers, publications, presentations"],
    "VolunteerWork": ["volunteer or extracurricular activities"],
    "Interests": ["hobbies and interests"],
    "CareerDomain": "primary career domain (e.g. Software Engineering, Data Science)",
    "PreferredRoles": ["list of target job roles based on resume"],
    "YearsOfExperience": "number or 0 (Student/Fresher)",
    "ResumeScore": integer 1-100,
    "CareerReadinessScore": integer 1-100,
    "ResumeStrengths": ["2-3 key strengths of this resume"],
    "ResumeWeaknesses": ["2-3 areas for improvement"]
}}

Resume Text:
{raw_text}
"""
    response_text = gemini_service.generate_content(prompt)

    cleaned = response_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    return json.loads(cleaned)


# ─── Routes ────────────────────────────────────────────────────────────────

@bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return error_response("No file part in the request.", 400)

    file = request.files['file']
    if not file or file.filename == '':
        return error_response("No file selected.", 400)

    if not allowed_file(file.filename):
        return error_response("File type not allowed. Please upload a PDF or DOCX file.", 400)

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()

    # Read file bytes once — needed for both saving and Gemini vision fallback
    file_bytes = file.read()

    # Save to temp for pdfplumber / pypdf
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    with open(tmp_path, 'wb') as f:
        f.write(file_bytes)

    raw_text = ""
    structured_data = None

    try:
        # ── Extraction waterfall ──────────────────────────────────────────
        if ext == 'pdf':
            raw_text = extract_text_pdfplumber(tmp_path)
            if not raw_text:
                print("pdfplumber yielded nothing — trying pypdf…")
                raw_text = extract_text_pypdf(tmp_path)
            if not raw_text:
                print("pypdf yielded nothing — using Gemini Vision (multimodal OCR)…")
                structured_data = extract_via_gemini_vision(file_bytes, filename, "application/pdf")

        elif ext in ('docx', 'doc'):
            raw_text = extract_text_docx(tmp_path)
            if not raw_text:
                # For docx, try base64 Gemini vision too
                print("python-docx yielded nothing — using Gemini Vision…")
                structured_data = extract_via_gemini_vision(
                    file_bytes, filename,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        # ── Text → Gemini structured parse (if vision didn't handle it) ──
        if structured_data is None:
            from app.services.resume_parser import resume_parser
            structured_data = resume_parser.extract_candidate_profile(raw_text)

        # ── Attach metadata ───────────────────────────────────────────────
        structured_data["_filename"] = filename
        structured_data["_source"] = "AI-extracted from uploaded resume"
        if raw_text:
            structured_data["_raw_text_preview"] = raw_text[:500] + ("…" if len(raw_text) > 500 else "")

        # ── Try to persist in DB (non-fatal if Vercel resets it) ──────────
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
            print(f"DB save skipped (non-critical on Vercel): {db_err}")

        return success_response("Resume analyzed successfully.", structured_data)

    except json.JSONDecodeError as je:
        print(f"JSON parse error: {je}")
        traceback.print_exc()
        # Return raw mock so the UI never crashes
        mock = {
            "FullName": filename.replace(".pdf", "").replace(".docx", "").replace("_", " ").title(),
            "EmailAddress": None, "PhoneNumber": None, "Location": None,
            "Skills": [], "TechnicalSkills": [], "SoftSkills": [],
            "Languages": [], "Education": [], "Experience": [], "Projects": [],
            "Certifications": [], "Achievements": [], "Research": [],
            "Interests": [], "CareerDomain": "Software Engineering",
            "PreferredRoles": ["Software Engineer"],
            "YearsOfExperience": "0 (Student/Fresher)",
            "ResumeScore": 60, "CareerReadinessScore": 60,
            "ResumeStrengths": ["Resume uploaded successfully"],
            "ResumeWeaknesses": ["Could not fully parse content — try a text-based PDF"],
            "_filename": filename, "_source": "Partial extraction (JSON parse error)"
        }
        return success_response("Resume partially analyzed.", mock)

    except Exception as e:
        print(f"Resume upload error: {e}")
        traceback.print_exc()
        return error_response(f"Failed to process resume: {str(e)}", 500)


@bp.route('/analyze', methods=['GET'])
def analyze_resume():
    return success_response("Analyze resume stub")


@bp.route('/details', methods=['GET'])
def get_resume_details():
    """Try DB; if empty/missing (stateless Vercel), return 404 so frontend uses localStorage."""
    try:
        from app.extensions import db
        from app.models.resume import Resume
        resume_record = Resume.query.filter_by(user_id=1).first()
        if resume_record and resume_record.parsed_json:
            return success_response("Resume details retrieved.", resume_record.parsed_json)
        return error_response("No resume found. Please upload first.", 404)
    except Exception:
        return error_response("No resume found. Please upload first.", 404)

@bp.route('/extract-json', methods=['POST'])
def extract_raw_json():
    """Extract resume and return the raw JSON file directly to the user."""
    from flask import Response
    file = request.files.get('file')
    if not file or file.filename == '':
        return error_response("No file selected.", 400)
    if not allowed_file(file.filename):
        return error_response("File type not allowed.", 400)

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    file_bytes = file.read()

    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    with open(tmp_path, 'wb') as f:
        f.write(file_bytes)

    raw_text = ""
    structured_data = None

    try:
        if ext == 'pdf':
            raw_text = extract_text_pdfplumber(tmp_path)
            if not raw_text:
                raw_text = extract_text_pypdf(tmp_path)
            if not raw_text:
                structured_data = extract_via_gemini_vision(file_bytes, filename, "application/pdf")

        elif ext in ('docx', 'doc'):
            raw_text = extract_text_docx(tmp_path)
            if not raw_text:
                structured_data = extract_via_gemini_vision(
                    file_bytes, filename,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        if structured_data is None:
            from app.services.resume_parser import resume_parser
            structured_data = resume_parser.extract_candidate_profile(raw_text)

        # Remove backend-specific injected compatibility keys to give pure JSON
        keys_to_remove = ["FullName", "ResumeScore", "CareerReadinessScore", "Skills", "TechnicalSkills", "SoftSkills", "Education", "Experience", "Projects", "Certifications", "Achievements", "Research", "Languages", "Interests", "CareerDomain", "PreferredRole", "PreferredRoles", "EmailAddress", "PhoneNumber", "Location", "LinkedInURL", "GitHubURL", "PortfolioURL", "YearsOfExperience", "ResumeStrengths", "ResumeWeaknesses", "_filename", "_source", "_raw_text_preview"]
        pure_json = {k: v for k, v in structured_data.items() if k not in keys_to_remove}

        json_str = json.dumps(pure_json, indent=4)
        return Response(
            json_str,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=extracted_resume_{filename}.json"}
        )
    except Exception as e:
        print(f"Error in extract_raw_json: {e}")
        return error_response(f"Extraction failed: {str(e)}", 500)
