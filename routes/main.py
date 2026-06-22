from flask import Blueprint, render_template, flash, redirect, url_for, request
from models.models import Contact, Internship, AddonPayment, Payment
from models import db
from forms import ContactForm
from flask_login import login_required, current_user
from models.models import Student

main_bp = Blueprint('main', __name__)


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
