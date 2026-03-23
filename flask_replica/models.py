from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # admin, judge, accuser, accused
    approved = db.Column(db.Boolean, default=False)

    @property
    def is_active(self):
        return self.approved
    
    # Optional Backref to Cases assigned to Judge
    cases_assigned = db.relationship('Case', foreign_keys='Case.judge_id', backref='judge', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending_admission') # pending_admission, active, dismissed, decided
    case_type = db.Column(db.String(20), default='standard') # standard, pil
    judge_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Assigned Judge
    accuser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    accused_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    description = db.Column(db.Text, nullable=True)
    public_filer_name = db.Column(db.String(100), nullable=True)
    public_filer_contact = db.Column(db.String(200), nullable=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    sender_role = db.Column(db.String(20), nullable=False) # accuser, accused, judge
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='admitted') # admitted, rejected

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    judge_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    respondent_role = db.Column(db.String(20), nullable=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    judge_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    judge_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
