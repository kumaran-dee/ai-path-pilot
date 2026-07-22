import os
import pdfplumber
import docx
from werkzeug.utils import secure_filename
from flask import Blueprint, request, current_app
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
        
        upload_folder = os.path.join(current_app.root_path, '..', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        ext = filename.rsplit('.', 1)[1].lower()
        extracted_text = ""
        try:
            if ext == 'pdf':
                extracted_text = extract_text_from_pdf(filepath)
            elif ext == 'docx':
                extracted_text = extract_text_from_docx(filepath)
                
            structured_data = gemini_service.extract_resume_data(extracted_text)
            
        except Exception as e:
            return error_response(f"Failed to parse file: {str(e)}", 500)
            
        return success_response("File uploaded and parsed successfully", {
            "filename": filename,
            "structured_data": structured_data
        })
        
    return error_response("File type not allowed. Please upload PDF or DOCX.", 400)

@bp.route('/analyze', methods=['GET'])
def analyze_resume():
    return success_response("Analyze resume stub")

@bp.route('/details', methods=['GET'])
def get_resume_details():
    return success_response("Resume details stub")
