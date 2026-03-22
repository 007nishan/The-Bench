from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # admin, judge, accuser, accused, public
    
    # Optional Backref to Cases assigned to Judge
    cases_assigned = db.relationship('Case', foreign_keys='Case.judge_id', backref='judge', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='filed') # filed, assigned, ongoing, decided
    judge_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Assigned Judge
    accuser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Assigning User
    accused_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Assigning User
    description = db.Column(db.Text, nullable=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    sender_role = db.Column(db.String(20), nullable=False) # accuser, accused
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
