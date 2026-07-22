from flask import Flask, jsonify
from .config import Config
from .extensions import db
from .utilities.response import error_response

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Register blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    from app.routes.resume import bp as resume_bp
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    
    from app.routes.opportunity import bp as opportunity_bp
    app.register_blueprint(opportunity_bp, url_prefix='/api/opportunity')
    
    from app.routes.skill_gap import bp as skill_gap_bp
    app.register_blueprint(skill_gap_bp, url_prefix='/api/skill_gap')
    
    from app.routes.roadmap import bp as roadmap_bp
    app.register_blueprint(roadmap_bp, url_prefix='/api/roadmap')
    
    from app.routes.chat import bp as chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    from app.routes.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    @app.route('/health')
    def health():
        return {"status": "ok"}

    # Global Exception Handler for standardized JSON responses
    @app.errorhandler(Exception)
    def handle_exception(e):
        return error_response(f"Internal Server Error: {str(e)}", 500)

    return app
