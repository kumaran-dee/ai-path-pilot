import os
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
from app.models.match_report import MatchReport
from app.routes.resume import allowed_file
from app.services.resume_parser import resume_parser
from app.services.job_scraper import job_scraper
from app.services.job_parser import job_parser
from app.services.matching_service import matching_service
from app.services.skill_gap_service import skill_gap_service
from app.services.recommendation_service import recommendation_service
from app.services.roadmap_service import roadmap_service
from app.utilities.response import success_response, error_response

bp = Blueprint('compare', __name__)

@bp.route('/match', methods=['POST'])
def match_resume_job():
    if 'resume' not in request.files:
        return error_response("No resume provided", 400)
    
    file = request.files['resume']
    job_link = request.form.get('jobLink', '')
    
    if file.filename == '':
        return error_response("No selected file", 400)
    
    if not job_link:
        return error_response("No job link provided", 400)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = tempfile.gettempdir()
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            # 1. Parse and extract resume profile
            from app.routes.resume import extract_text_pdfplumber, extract_text_pypdf, extract_text_docx, extract_via_gemini_vision
            
            with open(filepath, 'rb') as f:
                file_bytes = f.read()
                
            ext = filename.rsplit('.', 1)[1].lower()
            raw_text = ""
            resume_data = None
            
            if ext == 'pdf':
                raw_text = extract_text_pdfplumber(filepath)
                if not raw_text:
                    raw_text = extract_text_pypdf(filepath)
                if not raw_text:
                    resume_data = extract_via_gemini_vision(file_bytes, filename, "application/pdf")
            elif ext in ('docx', 'doc'):
                raw_text = extract_text_docx(filepath)
                if not raw_text:
                    resume_data = extract_via_gemini_vision(
                        file_bytes, filename,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            
            if resume_data is None:
                resume_data = resume_parser.extract_candidate_profile(raw_text)

            # Save the detailed resume profile to a JSON file as requested
            import json
            with open("detailed_resume_profile.json", "w", encoding="utf-8") as f:
                json.dump(resume_data, f, indent=4)
            
            # Associate with dummy user_id = 1
            user_id = 1
            user = User.query.get(user_id)
            if not user:
                user = User(id=user_id, username='testuser', email='test@example.com', password_hash='mock')
                db.session.add(user)
                db.session.commit()
            
            # Replace previous resume record
            resume_record = Resume.query.filter_by(user_id=user_id).first()
            if resume_record:
                resume_record.filename = filename
                resume_record.parsed_json = resume_data
                resume_record.score = float(resume_data.get("ResumeScore", 0))
                resume_record.readiness = str(resume_data.get("CareerReadinessScore", 0))
            else:
                resume_record = Resume(
                    user_id=user_id, 
                    filename=filename, 
                    parsed_json=resume_data,
                    score=float(resume_data.get("ResumeScore", 0)),
                    readiness=str(resume_data.get("CareerReadinessScore", 0))
                )
                db.session.add(resume_record)
            
            # 2. Scrape job description
            raw_job_text = job_scraper.scrape_url(job_link)
            
            # 3. Parse job description
            structured_job = job_parser.parse_job_description(raw_job_text)
            
            # 4. Evaluate match
            matching_results = matching_service.evaluate_match(resume_data, structured_job)
            
            # 5. Skill gap detection
            skill_gaps = skill_gap_service.detect_gaps(
                resume_skills=resume_data.get("Skills", []),
                job_skills=structured_job.get("RequiredSkills", []),
                preferred_skills=structured_job.get("PreferredSkills", [])
            )
            
            # 6. Generate recommendation
            recommendations = recommendation_service.generate_recommendation(
                resume_data=resume_data,
                job_requirements=structured_job,
                matching_results=matching_results,
                skill_gaps=skill_gaps
            )
            
            # 7. Generate learning roadmap
            roadmap_data = roadmap_service.generate_roadmap_plan(
                missing_skills=skill_gaps.get("missing_skills", []),
                role=structured_job.get("JobRole", "Software Engineer")
            )
            
            # Formulate final response
            final_report = {
                "resume_score": resume_data.get("ResumeScore", 80),
                "career_readiness": resume_data.get("CareerReadinessScore", 80),
                "match_score": matching_results.get("overall_match", 75),
                "matched_skills": skill_gaps.get("matched_skills", []),
                "missing_skills": skill_gaps.get("missing_skills", []),
                "resume_improvements": recommendations.get("resume_improvements", []),
                "recommended_courses": roadmap_data.get("recommended_courses", []),
                "learning_roadmap": roadmap_data.get("plan_7_day", []) + roadmap_data.get("plan_30_day", []),
                "should_apply": recommendations.get("should_apply", "MAYBE"),
                "reason": recommendations.get("reason", "Matches well with key requirements.")
            }
            
            # Save report to db
            report_record = MatchReport(
                user_id=user_id,
                company_name=structured_job.get("CompanyName", "Target Company"),
                job_role=structured_job.get("JobRole", "Target Role"),
                job_url=job_link,
                job_description=raw_job_text,
                resume_score=final_report["resume_score"],
                career_readiness=final_report["career_readiness"],
                match_score=final_report["match_score"],
                matched_skills=final_report["matched_skills"],
                missing_skills=final_report["missing_skills"],
                resume_improvements=final_report["resume_improvements"],
                recommended_courses=final_report["recommended_courses"],
                learning_roadmap=final_report["learning_roadmap"],
                should_apply=final_report["should_apply"],
                reason=final_report["reason"]
            )
            
            MatchReport.query.filter_by(user_id=user_id).delete()
            db.session.add(report_record)
            db.session.commit()
            
            # Return matching success structure wrapper
            return success_response("Comparison successful", final_report)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return error_response(f"Failed to parse and match resume: {str(e)}", 500)
            
    return error_response("Invalid file type. Please upload a PDF or DOCX file.", 400)
