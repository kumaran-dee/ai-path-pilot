from app.extensions import db

class Resume(db.Model):
    __tablename__ = 'resumes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255))
    parsed_json = db.Column(db.JSON)
    score = db.Column(db.Float)
    readiness = db.Column(db.String(50))
    
    # Relationships
    user = db.relationship('User', back_populates='resume')
    skills = db.relationship('Skill', back_populates='resume', cascade="all, delete-orphan")
    projects = db.relationship('Project', back_populates='resume', cascade="all, delete-orphan")

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    resume = db.relationship('Resume', back_populates='skills')

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    resume = db.relationship('Resume', back_populates='projects')
