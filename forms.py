from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SelectField, FloatField,
                     TextAreaField, SubmitField, BooleanField, HiddenField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                NumberRange, Optional, ValidationError, Regexp)


DOMAINS = [
    ('', '-- Select Domain --'),
    # --- Project Based Learning Domains ---
    ('Frontend Developer', 'Frontend Developer'),
    ('Backend Developer', 'Backend Developer'),
    ('MEAN Stack Developer', 'MEAN Stack Developer'),
    ('Full Stack Developer', 'Full Stack Developer'),
    ('Web Developer', 'Web Developer'),
    ('App Developer', 'App Developer'),
    ('UI/UX Designer', 'UI/UX Designer'),
    ('Cyber Security', 'Cyber Security'),
    ('Data Science / ML / AI Intern', 'Data Science / ML / AI Intern'),
    # --- Business & Marketing Domains ---
    ('Business Development Associate', 'Business Development Associate'),
    ('Human Resources (HR)', 'Human Resources (HR)'),
    ('Marketing', 'Marketing'),
    ('Digital Marketing', 'Digital Marketing'),
    ('Digital Content Creator', 'Digital Content Creator'),
    ('Social Media Promotion', 'Social Media Promotion'),
    ('SMS / Email Marketing', 'SMS / Email Marketing'),
    ('Content Writer', 'Content Writer'),
    # --- Other Domains ---
    ('Process Associate', 'Process Associate'),
    ('Short Film Maker / Ads Creator', 'Short Film Maker / Ads Creator'),
    ('Technical Support', 'Technical Support'),
    # --- Existing Domains ---
    ('Machine Learning', 'Machine Learning'),
    ('Artificial Intelligence', 'Artificial Intelligence'),
    ('Android Development', 'Android Development'),
    ('Python Programming', 'Python Programming'),
    ('Java Development', 'Java Development'),
    ('Cloud Computing', 'Cloud Computing'),
    ('Embedded Systems', 'Embedded Systems'),
]

DURATIONS = [
    ('', 'Select Duration'),
    ('1 Month', '1 Month'),
    ('2 Months', '2 Months'),
    ('3 Months', '3 Months'),
    ('6 Months', '6 Months'),
]

BRANCHES = [
    ('', '-- Select Branch --'),
    ('Computer Science', 'Computer Science (CSE)'),
    ('Information Technology', 'Information Technology (IT)'),
    ('Electronics', 'Electronics & Communication (ECE)'),
    ('Electrical', 'Electrical Engineering (EEE)'),
    ('Mechanical', 'Mechanical Engineering (ME)'),
    ('Civil', 'Civil Engineering (CE)'),
    ('Chemical', 'Chemical Engineering'),
    ('Biotechnology', 'Biotechnology'),
    ('MBA', 'MBA'),
    ('MCA', 'MCA'),
    ('Other', 'Other'),
]


def validate_not_empty(form, field):
    if not field.data or field.data.strip() == '':
        raise ValidationError('This field is required.')


class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(), 
        Length(min=2, max=100),
        Regexp(r'^[a-zA-Z]+( [a-zA-Z]+)*$', message='Name must contain only letters and single spaces between words (no leading/trailing or multiple spaces).')
    ])
    branch = SelectField('Branch', choices=BRANCHES, validators=[DataRequired(), validate_not_empty])
    other_branch = StringField('Other Branch Name', validators=[
        Optional(), 
        Length(max=100),
        Regexp(r'^[a-zA-Z][a-zA-Z\s]*$', message='Must start with a letter and contain only letters and spaces.')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    college = StringField('College Name', validators=[
        DataRequired(), 
        Length(min=3, max=200),
        Regexp(r'^[a-zA-Z\s.,()\'\-&]+$', message='College Name must contain only letters, spaces, and basic punctuation')
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message='Enter valid 10-digit phone number')
    ])
    tenth_percentage = FloatField('10th Percentage', validators=[
        DataRequired(), NumberRange(min=0, max=100, message='Enter a valid percentage between 0 and 100')
    ])
    twelfth_percentage = FloatField('12th Percentage', validators=[
        DataRequired(), NumberRange(min=0, max=100, message='Enter a valid percentage between 0 and 100')
    ])
    ug = StringField('UG Degree', validators=[
        DataRequired(), 
        Length(max=100),
        Regexp(r'^[a-zA-Z]+( [a-zA-Z]+)*$', message='UG Degree must contain only letters and a single space between words.')
    ])
    ug_percentage = FloatField('UG Percentage', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message='Enter a valid percentage between 0 and 100')
    ])
    pg = StringField('PG Degree (optional)', validators=[
        Optional(), 
        Length(max=100),
        Regexp(r'^[a-zA-Z]+( [a-zA-Z]+)*$', message='PG Degree must contain only letters and a single space between words.')
    ])
    location = StringField('Location / City', validators=[DataRequired(), Length(max=100)])
    internship_domain = SelectField('Internship Domain', choices=DOMAINS, validators=[DataRequired(), validate_not_empty])
    duration = SelectField('Duration', choices=DURATIONS, validators=[DataRequired(), validate_not_empty])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Submit Registration')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AdminLoginForm(FlaskForm):
    email = StringField('Admin Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Admin Login')


class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[
        DataRequired(), 
        Length(min=2, max=100),
        Regexp(r'^[a-zA-Z]+( [a-zA-Z]+)*$', message='Name must contain only letters and single spaces between words (no leading/trailing or multiple spaces).')
    ])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[
        Optional(),
        Regexp(r'^\d{10}$', message='Enter a valid 10-digit phone number')
    ])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=3, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')


class PaymentForm(FlaskForm):
    amount = HiddenField('Amount', default='999')
    transaction_id = StringField('Transaction / UTR ID', validators=[DataRequired(), Length(min=5, max=100)])
    screenshot = FileField('Payment Screenshot', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!')
    ])
    submit = SubmitField('Submit Payment')
