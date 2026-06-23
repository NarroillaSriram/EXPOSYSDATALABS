from flask import Blueprint, render_template, flash, redirect, url_for, request
from models.models import Contact, Internship, AddonPayment, Payment
from models import db, csrf
from forms import ContactForm
from flask_login import login_required, current_user
from models.models import Student, JobApplication

main_bp = Blueprint('main', __name__)


@main_bp.route('/verify', methods=['GET', 'POST'])
@csrf.exempt
def verify_search():
    """Public certificate search page — enter any certificate ID to verify."""
    cert = None
    certificate_id = None
    searched = False

    def clean_cert_id(raw):
        """Strip brackets, spaces, and copy-paste artifacts from certificate ID."""
        import re
        # Remove [ ] brackets and surrounding whitespace
        cleaned = raw.strip()
        cleaned = re.sub(r'^\[\s*', '', cleaned)   # remove leading [
        cleaned = re.sub(r'\s*\]$', '', cleaned)   # remove trailing ]
        cleaned = cleaned.strip()
        return cleaned

    if request.method == 'POST':
        raw = request.form.get('certificate_id', '')
        certificate_id = clean_cert_id(raw)
        searched = True
    elif request.args.get('id'):
        raw = request.args.get('id', '')
        certificate_id = clean_cert_id(raw)
        searched = True

    if certificate_id:
        from models.models import Certificate
        from sqlalchemy import func
        # Case-insensitive search — handles UPPER/lower differences
        cert = Certificate.query.filter(
            func.upper(Certificate.certificate_id) == certificate_id.upper()
        ).first()

    return render_template('verify_search.html',
                           cert=cert,
                           certificate_id=certificate_id,
                           searched=searched)


@main_bp.route('/verify/<certificate_id>')
def verify_certificate(certificate_id):
    """Public certificate verification page — no login required."""
    from models.models import Certificate
    cert = Certificate.query.filter_by(certificate_id=certificate_id).first()
    return render_template('verify_certificate.html', cert=cert, certificate_id=certificate_id)




@main_bp.route('/')
def index():
    internships = Internship.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html', internships=internships)


@main_bp.route('/go-to-domain/<path:domain_name>')
def go_to_domain(domain_name):
    # Map display names from the homepage to standard choice keys from forms.py
    mapping = {
        'Data Science / ML / AI': 'Data Science / ML / AI Intern',
        'UI/UX Design': 'UI/UX Designer',
    }
    form_domain = mapping.get(domain_name, domain_name)

    if not current_user.is_authenticated:
        return redirect(url_for('auth.register', domain=form_domain))

    # If logged in as student
    if isinstance(current_user._get_current_object(), Student):
        # Check if they have verified main payment
        has_payment = Payment.query.filter_by(student_id=current_user.id, status='verified').first() is not None
        if not has_payment:
            return redirect(url_for('student.payment'))

        # Check if they have access to this domain
        is_registered = current_user.internship_domain and current_user.internship_domain.lower() == form_domain.lower()
        is_verified_addon = AddonPayment.query.filter_by(
            student_id=current_user.id, domain=form_domain, status='verified'
        ).first() is not None

        if is_registered or is_verified_addon:
            return redirect(url_for('student.domain_detail', domain=form_domain))
        
        # Check if they have a pending addon
        is_pending_addon = AddonPayment.query.filter_by(
            student_id=current_user.id, domain=form_domain, status='pending'
        ).first() is not None
        
        if is_pending_addon:
            flash(f'Payment for {form_domain} is pending verification.', 'info')
            return redirect(url_for('main.internships'))
        
        # Otherwise redirect to unlock addon
        return redirect(url_for('student.addon_payment', domain=form_domain))
    
    # If logged in as admin or other non-student
    return redirect(url_for('admin.dashboard'))


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/internships')
def internships():
    all_internships = Internship.query.filter_by(is_active=True).all()
    addon_domains_verified = []
    addon_domains_pending = []
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), Student):
        addons = AddonPayment.query.filter_by(student_id=current_user.id).all()
        addon_domains_verified = [a.domain for a in addons if a.status == 'verified']
        addon_domains_pending  = [a.domain for a in addons if a.status == 'pending']
    return render_template('internships.html', internships=all_internships,
                           addon_domains_verified=addon_domains_verified,
                           addon_domains_pending=addon_domains_pending)



@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact_entry = Contact(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact_entry)
        db.session.commit()
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html', form=form)


@main_bp.route('/research')
def research():
    return render_template('research.html')


@main_bp.route('/promotions')
def promotions():
    return render_template('promotions.html')


@main_bp.route('/design')
def design():
    return render_template('design.html')


@main_bp.route('/careers')
def careers():
    return render_template('careers.html')


@main_bp.route('/job-application', methods=['GET', 'POST'])
@csrf.exempt
def job_application():
    import os, json, time
    from werkzeug.utils import secure_filename
    from flask import current_app

    role = request.args.get('role', 'General Application')
    if request.method == 'POST':
        try:
            # File Upload
            resume_file = request.files.get('resume')
            if not resume_file or resume_file.filename == '':
                flash('Resume file is required.', 'danger')
                return redirect(url_for('main.job_application', role=role))
            
            filename = secure_filename(resume_file.filename)
            # Make sure we have a unique filename
            import time
            unique_filename = f"resume_{int(time.time())}_{filename}"
            
            # Ensure upload dir exists
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            resume_file.save(file_path)

            # Build Experience JSON
            experiences = []
            exp_titles = request.form.getlist('exp_title[]')
            exp_companies = request.form.getlist('exp_company[]')
            exp_starts = request.form.getlist('exp_start[]')
            exp_ends = request.form.getlist('exp_end[]')
            for i in range(len(exp_titles)):
                if exp_titles[i] or exp_companies[i]:
                    experiences.append({
                        'title': exp_titles[i],
                        'company': exp_companies[i],
                        'start': exp_starts[i] if i < len(exp_starts) else '',
                        'end': exp_ends[i] if i < len(exp_ends) else ''
                    })
            
            # Build Education JSON
            educations = []
            edu_schools = request.form.getlist('edu_school[]')
            edu_degrees = request.form.getlist('edu_degree[]')
            edu_majors = request.form.getlist('edu_major[]')
            for i in range(len(edu_schools)):
                if edu_schools[i]:
                    educations.append({
                        'school': edu_schools[i],
                        'degree': edu_degrees[i] if i < len(edu_degrees) else '',
                        'major': edu_majors[i] if i < len(edu_majors) else ''
                    })

            # Create JobApplication
            new_app = JobApplication(
                role=request.form.get('role', role),
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                linkedin_url=request.form.get('linkedin'),
                portfolio_url=request.form.get('portfolio'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                country=request.form.get('other_country') if request.form.get('country') == 'Other' else request.form.get('country'),
                experience_json=json.dumps(experiences),
                education_json=json.dumps(educations),
                skills=request.form.get('skills'),
                cover_letter=request.form.get('cover_letter'),
                resume_filename=f"resumes/{unique_filename}"
            )
            
            db.session.add(new_app)
            db.session.commit()
            
            flash('Your application has been submitted successfully!', 'success')
            return redirect(url_for('main.careers'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('main.job_application', role=role))
            
    return render_template('job_application.html', role=role)

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')


@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@main_bp.route('/cookies')
def cookies():
    return render_template('cookies.html')


@main_bp.route('/reviews')
def reviews():
    return render_template('reviews.html')


@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500
