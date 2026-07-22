from app.extensions import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    resume = db.relationship('Resume', back_populates='user', uselist=False, cascade="all, delete-orphan")
    applications = db.relationship('Application', back_populates='user', cascade="all, delete-orphan")
    saved_opportunities = db.relationship('SavedOpportunity', back_populates='user', cascade="all, delete-orphan")
    notifications = db.relationship('Notification', back_populates='user', cascade="all, delete-orphan")
    roadmaps = db.relationship('Roadmap', back_populates='user', cascade="all, delete-orphan")
