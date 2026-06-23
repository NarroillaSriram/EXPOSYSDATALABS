from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from sqlalchemy.orm import synonym

class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    college = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    tenth_percentage = db.Column(db.Float, nullable=True)
    twelfth_percentage = db.Column(db.Float, nullable=True)
    ug = db.Column(db.String(100), nullable=True)
    pg = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    internship_domain = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('Payment', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return f"student_{self.id}"

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return f"admin_{self.id}"

class Internship(db.Model):
    __tablename__ = 'internships'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_options = db.Column(db.String(200), nullable=True)
    stipend = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)
    screenshot_filename = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    payment_method = db.Column(db.String(50), default='UPI')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AddonPayment(db.Model):
    __tablename__ = 'addon_payments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=999)
    transaction_id = db.Column(db.String(100), nullable=True)
    screenshot_filename = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('addon_payments', lazy=True, cascade="all, delete-orphan"))

class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    student_name = db.Column(db.String(255), nullable=False)
    domain_name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    blockchain_hash = db.Column(db.String(100), nullable=True)
    tx_hash = db.Column(db.String(100), nullable=True)
    qr_code = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')
    pdf_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('certificates', lazy=True, cascade="all, delete-orphan"))

class ProjectSubmission(db.Model):
    __tablename__ = 'project_submissions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    # Map attribute 'domain_name' to actual DB column 'domain'
    domain_name = db.Column('domain', db.String(100), nullable=False)
    # Provide synonym 'domain' for ORM queries
    domain = synonym('domain_name')
    file_path = db.Column('filename', db.String(255), nullable=False)
    status = db.Column(db.String(20), default='submitted')  # submitted, approved, rejected
    created_at = db.Column('submitted_at', db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('submissions', lazy=True, cascade="all, delete-orphan"))

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    linkedin_url = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=False)
    
    # Storing dynamic fields as JSON
    experience_json = db.Column(db.Text, nullable=True)
    education_json = db.Column(db.Text, nullable=True)
    
    skills = db.Column(db.Text, nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    
    # Store the filename of the uploaded resume
    resume_filename = db.Column(db.String(255), nullable=False)
    
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, interviewing, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
