from app.extensions import db
from datetime import datetime, timezone

class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50)) # job, internship, hackathon, research
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text) # Stored as comma-separated or text block
    location = db.Column(db.String(100))
    deadline = db.Column(db.DateTime)
    
    # Relationships
    applications = db.relationship('Application', back_populates='opportunity')
    saved_by = db.relationship('SavedOpportunity', back_populates='opportunity')

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False)
    status = db.Column(db.String(50), default='applied')
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', back_populates='applications')
    opportunity = db.relationship('Opportunity', back_populates='applications')

class SavedOpportunity(db.Model):
    __tablename__ = 'saved_opportunities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', back_populates='saved_opportunities')
    opportunity = db.relationship('Opportunity', back_populates='saved_by')
