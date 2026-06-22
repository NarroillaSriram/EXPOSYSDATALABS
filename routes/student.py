import os
import hmac
import hashlib
import razorpay
from flask import (Blueprint, render_template, flash, redirect, url_for,
                   request, current_app, jsonify, session, abort)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.models import Payment, Student, AddonPayment, Certificate, ProjectSubmission
from models import db, csrf
from forms import PaymentForm
from domain_content import get_domain_content

student_bp = Blueprint('student', __name__)

PAYMENT_AMOUNT = 1  # ₹1 for testing (change to 999 for production)


def get_razorpay_client():
    return razorpay.Client(
        auth=(current_app.config['RAZORPAY_KEY_ID'],
              current_app.config['RAZORPAY_KEY_SECRET'])
    )


def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user._get_current_object(), Student):
            flash('Please login as a student.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def student_has_domain_access(student, domain):
    """Returns True if student has access to the given domain (registered or addon verified)."""
    if student.internship_domain and student.internship_domain.lower() == domain.lower():
        main_payment = Payment.query.filter_by(student_id=student.id).first()
        if main_payment and main_payment.status == 'verified':
            return True
            
    addon = AddonPayment.query.filter_by(
        student_id=student.id, domain=domain
    ).first()
    if addon and addon.status == 'verified':
        return True
        
    return False


def verify_razorpay_signature(order_id, payment_id, signature):
    """Cryptographically verify that the payment came from Razorpay."""
    key_secret = current_app.config['RAZORPAY_KEY_SECRET']
    message = f"{order_id}|{payment_id}"
    generated = hmac.new(
        key_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(generated, signature)


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    main_payments = Payment.query.filter_by(student_id=current_user.id).all()
    # Check if student has at least one main payment to access the dashboard
    has_main_payment = len(main_payments) > 0
    if not has_main_payment:
        flash('Please complete your payment to access the dashboard.', 'warning')
        return redirect(url_for('student.payment'))
        
    addon_payments = AddonPayment.query.filter_by(student_id=current_user.id).all()
    
    # Unified list for rendering in the payments history table
    all_payments = []
    for p in main_payments:
        all_payments.append({
            'id': p.id,
            'type_raw': 'main',
            'type': 'Main Registration',
            'domain': current_user.internship_domain or 'Registration',
            'amount': p.amount,
            'transaction_id': p.transaction_id,
            'status': p.status,
            'created_at': p.created_at,
            'updated_at': p.updated_at
        })
    for ap in addon_payments:
        all_payments.append({
            'id': ap.id,
            'type_raw': 'addon',
            'type': 'Add-on',
            'domain': ap.domain,
            'amount': ap.amount,
            'transaction_id': ap.transaction_id,
            'status': ap.status,
            'created_at': ap.created_at,
            'updated_at': ap.updated_at
        })
    # Sort payments by created_at descending
    all_payments.sort(key=lambda x: x['created_at'], reverse=True)

    # Get string of all verified domains
    active_domains = [current_user.internship_domain] if current_user.internship_domain else []
    for ap in addon_payments:
        active_domains.append(ap.domain)
    domains_str = ", ".join(active_domains)

    # Re-fetch the latest payment for backward compatibility
    latest_payment = next((p for p in reversed(main_payments) if p.status == 'verified'), None) or (main_payments[-1] if main_payments else None)

    certificates = Certificate.query.filter_by(student_id=current_user.id, status='approved').all()

    return render_template('student/dashboard.html', 
                           student=current_user, 
                           payment=latest_payment,
                           addon_payments=addon_payments,
                           all_payments=all_payments,
                           domains_str=domains_str,
                           certificates=certificates)


# ─────────────────────────────────────────────
# MAIN PAYMENT — Create Razorpay Order
# ─────────────────────────────────────────────

@student_bp.route('/payment', methods=['GET'])
@login_required
@student_required
def payment():
    existing = Payment.query.filter_by(student_id=current_user.id).first()
    razorpay_key = current_app.config['RAZORPAY_KEY_ID']

    # Fetch all payments for history display
    main_payments = Payment.query.filter_by(student_id=current_user.id).all()
    addon_payments = AddonPayment.query.filter_by(student_id=current_user.id).all()
    all_payments = []
    for p in main_payments:
        all_payments.append({
            'id': p.id,
            'type_raw': 'main',
            'type': 'Main Registration',
            'domain': current_user.internship_domain or 'Registration',
            'amount': p.amount,
            'transaction_id': p.transaction_id,
            'status': p.status,
            'created_at': p.created_at,
            'updated_at': p.updated_at
        })
    for ap in addon_payments:
        all_payments.append({
            'id': ap.id,
            'type_raw': 'addon',
            'type': 'Add-on',
            'domain': ap.domain,
            'amount': ap.amount,
            'transaction_id': ap.transaction_id,
            'status': ap.status,
            'created_at': ap.created_at,
            'updated_at': ap.updated_at
        })
    all_payments.sort(key=lambda x: x['created_at'], reverse=True)

    return render_template('student/payment.html', existing=existing,
                           razorpay_key=razorpay_key, amount=PAYMENT_AMOUNT,
                           all_payments=all_payments)


@student_bp.route('/create-order', methods=['POST'])
@csrf.exempt
@login_required
@student_required
def create_order():
    """Create a Razorpay order and return order_id to the frontend."""
    # Prevent double payment
    existing = Payment.query.filter_by(student_id=current_user.id,
                                       status='verified').first()
    if existing:
        return jsonify({'error': 'Payment already verified'}), 400

    try:
        client = get_razorpay_client()
        order = client.order.create({
            'amount': PAYMENT_AMOUNT * 100,   # Razorpay uses paise
            'currency': 'INR',
            'payment_capture': 1,             # Auto-capture
            'notes': {
                'student_id': str(current_user.id),
                'student_name': current_user.name,
                'student_email': current_user.email,
                'domain': current_user.internship_domain or '',
            }
        })
        return jsonify({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'name': current_user.name,
            'email': current_user.email,
        })
    except Exception as e:
        current_app.logger.error(f"Razorpay order creation failed: {e}")
        return jsonify({'error': 'Payment gateway error. Please try again.'}), 500


@student_bp.route('/verify-payment', methods=['POST'])
@csrf.exempt
@login_required
@student_required
def verify_payment():
    """Verify Razorpay signature and mark payment as verified."""
    data = request.get_json()
    razorpay_order_id   = data.get('razorpay_order_id', '')
    razorpay_payment_id = data.get('razorpay_payment_id', '')
    razorpay_signature  = data.get('razorpay_signature', '')

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return jsonify({'success': False, 'error': 'Incomplete payment data'}), 400

    if not verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        return jsonify({'success': False, 'error': 'Payment verification failed'}), 400

    # Check no duplicate
    existing = Payment.query.filter_by(student_id=current_user.id,
                                       status='verified').first()
    if existing:
        return jsonify({'success': True, 'redirect': url_for('student.dashboard')})

    pay = Payment(
        student_id=current_user.id,
        amount=PAYMENT_AMOUNT,
        transaction_id=razorpay_payment_id,
        status='verified',
        payment_method='Razorpay',
    )
    db.session.add(pay)
    db.session.commit()

    # Send receipt email to student
    from routes.email_utils import send_receipt_email
    send_receipt_email(current_user._get_current_object(), pay)

    return jsonify({
        'success': True,
        'redirect': url_for('student.registration_success')
    })


# ─────────────────────────────────────────────
# UPI / QR MANUAL PAYMENT SUBMISSION
# ─────────────────────────────────────────────

@student_bp.route('/submit-upi-payment', methods=['POST'])
@csrf.exempt
@login_required
@student_required
def submit_upi_payment():
    """Accept a UPI transaction ID + screenshot and create a pending payment record."""
    # Prevent duplicate submissions
    existing = Payment.query.filter_by(student_id=current_user.id).first()
    if existing:
        if existing.status == 'verified':
            return jsonify({'success': False, 'error': 'Payment already verified.'}), 400
        if existing.status == 'pending':
            return jsonify({'success': False, 'error': 'Payment already submitted, pending verification.'}), 400

    transaction_id = request.form.get('transaction_id', '').strip()
    if not transaction_id:
        return jsonify({'success': False, 'error': 'Transaction ID is required.'}), 400

    screenshot = request.files.get('screenshot')
    screenshot_filename = None
    if screenshot and screenshot.filename:
        ext = screenshot.filename.rsplit('.', 1)[-1].lower()
        allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if ext not in allowed:
            return jsonify({'success': False, 'error': 'Screenshot must be an image (png, jpg, jpeg, gif, webp).'}), 400
        safe_name = secure_filename(f"upi_{current_user.id}_{transaction_id[:12]}.{ext}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        screenshot.save(os.path.join(upload_folder, safe_name))
        screenshot_filename = safe_name

    pay = Payment(
        student_id=current_user.id,
        amount=PAYMENT_AMOUNT,
        transaction_id=transaction_id,
        status='pending',
        payment_method='UPI/QR',
    )
    if screenshot_filename:
        pay.screenshot_filename = screenshot_filename

    db.session.add(pay)
    db.session.commit()

    current_app.logger.info(
        f"UPI payment submitted — student_id={current_user.id}, txn={transaction_id}, file={screenshot_filename}"
    )
    return jsonify({'success': True})


# ─────────────────────────────────────────────
# SUCCESS PAGE
# ─────────────────────────────────────────────

@student_bp.route('/registration-success')
@login_required
@student_required
def registration_success():
    payment = Payment.query.filter_by(student_id=current_user.id).order_by(Payment.created_at.desc()).first()
    return render_template('student/success.html', student=current_user, payment=payment)


# ─────────────────────────────────────────────
# MY COURSES & CERTIFICATES
# ─────────────────────────────────────────────

@student_bp.route('/my-courses')
@login_required
@student_required
def my_courses():
    main_payment = Payment.query.filter_by(student_id=current_user.id).first()
    addon_payments = AddonPayment.query.filter_by(student_id=current_user.id).all()
    
    courses = []
    if main_payment and main_payment.status == 'verified' and current_user.internship_domain:
        courses.append(current_user.internship_domain)
        
    for ap in addon_payments:
        if ap.status == 'verified' and ap.domain and ap.domain not in courses:
            courses.append(ap.domain)
            
    return render_template('student/my_courses.html', my_courses=courses, student=current_user)


@student_bp.route('/certificates')
@login_required
@student_required
def certificates():
    certs = Certificate.query.filter_by(student_id=current_user.id, status='approved').all()
    
    return render_template('student/certificates.html', 
                           certificates=certs, 
                           student=current_user)

@student_bp.route('/download-certificate/<certificate_id>')
@login_required
@student_required
def download_certificate(certificate_id):
    cert = Certificate.query.filter_by(student_id=current_user.id, certificate_id=certificate_id, status='approved').first_or_404()
    
    from flask import send_from_directory, current_app, abort
    base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'certificate_system', 'backend', 'uploads', 'certificates'
    )
    
    filename = f"{certificate_id}.pdf"
    if not os.path.exists(os.path.join(base, filename)):
        abort(404)
        
    return send_from_directory(base, filename, as_attachment=False)



# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────

@student_bp.route('/profile')
@login_required
@student_required
def profile():
    return render_template('student/profile.html', student=current_user)


# ─────────────────────────────────────────────
# ADDON PAYMENT — Create Razorpay Order
# ─────────────────────────────────────────────

@student_bp.route('/addon-payment/<path:domain>', methods=['GET'])
@login_required
@student_required
def addon_payment(domain):
    main_payment = Payment.query.filter_by(student_id=current_user.id).first()
    if not main_payment:
        flash('Your main internship payment must be verified before unlocking additional domains.', 'warning')
        return redirect(url_for('student.payment'))

    if current_user.internship_domain and current_user.internship_domain.lower() == domain.lower():
        flash('This is already your registered domain.', 'info')
        return redirect(url_for('student.domain_detail', domain=domain))

    existing_addon = AddonPayment.query.filter_by(
        student_id=current_user.id, domain=domain
    ).first()

    razorpay_key = current_app.config['RAZORPAY_KEY_ID']
    return render_template('student/addon_payment.html',
                           domain=domain,
                           existing_addon=existing_addon,
                           razorpay_key=razorpay_key,
                           amount=PAYMENT_AMOUNT)


@student_bp.route('/create-addon-order/<path:domain>', methods=['POST'])
@csrf.exempt
@login_required
@student_required
def create_addon_order(domain):
    """Create a Razorpay order for an add-on domain."""
    existing_addon = AddonPayment.query.filter_by(
        student_id=current_user.id, domain=domain, status='verified'
    ).first()
    if existing_addon:
        return jsonify({'error': 'Domain already unlocked'}), 400

    try:
        client = get_razorpay_client()
        order = client.order.create({
            'amount': PAYMENT_AMOUNT * 100,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'student_id': str(current_user.id),
                'student_name': current_user.name,
                'student_email': current_user.email,
                'addon_domain': domain,
                'type': 'addon',
            }
        })
        return jsonify({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'name': current_user.name,
            'email': current_user.email,
        })
    except Exception as e:
        current_app.logger.error(f"Razorpay addon order creation failed: {e}")
        return jsonify({'error': 'Payment gateway error. Please try again.'}), 500


@student_bp.route('/verify-addon-payment/<path:domain>', methods=['POST'])
@csrf.exempt
@login_required
@student_required
def verify_addon_payment(domain):
    """Verify Razorpay signature and auto-unlock the add-on domain."""
    data = request.get_json()
    razorpay_order_id   = data.get('razorpay_order_id', '')
    razorpay_payment_id = data.get('razorpay_payment_id', '')
    razorpay_signature  = data.get('razorpay_signature', '')

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return jsonify({'success': False, 'error': 'Incomplete payment data'}), 400

    if not verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        return jsonify({'success': False, 'error': 'Payment verification failed'}), 400

    # Avoid duplicates
    existing = AddonPayment.query.filter_by(
        student_id=current_user.id, domain=domain, status='verified'
    ).first()
    if existing:
        return jsonify({'success': True, 'redirect': url_for('student.domain_detail', domain=domain)})

    addon = AddonPayment(
        student_id=current_user.id,
        domain=domain,
        amount=PAYMENT_AMOUNT,
        transaction_id=razorpay_payment_id,
        status='verified',
    )
    db.session.add(addon)
    db.session.commit()

    # Send receipt email to student
    from routes.email_utils import send_receipt_email
    send_receipt_email(current_user._get_current_object(), addon)

    return jsonify({
        'success': True,
        'redirect': url_for('student.domain_detail', domain=domain)
    })


@student_bp.route('/submit-upi-addon-payment/<path:domain>', methods=['POST'])
@csrf.exempt
@login_required
@student_required
def submit_upi_addon_payment(domain):
    """Accept a UPI transaction ID + screenshot and create a pending addon payment record."""
    main_payment = Payment.query.filter_by(student_id=current_user.id).first()
    if not main_payment:
        return jsonify({'success': False, 'error': 'Main internship payment must be submitted before unlocking additional domains.'}), 400

    existing_addon = AddonPayment.query.filter_by(
        student_id=current_user.id, domain=domain
    ).first()
    if existing_addon:
        if existing_addon.status == 'verified':
            return jsonify({'success': False, 'error': 'Domain already unlocked.'}), 400
        if existing_addon.status == 'pending':
            return jsonify({'success': False, 'error': 'Payment already submitted, pending verification.'}), 400

    transaction_id = request.form.get('transaction_id', '').strip()
    if not transaction_id:
        return jsonify({'success': False, 'error': 'Transaction ID is required.'}), 400

    screenshot = request.files.get('screenshot')
    screenshot_filename = None
    if screenshot and screenshot.filename:
        ext = screenshot.filename.rsplit('.', 1)[-1].lower()
        allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if ext not in allowed:
            return jsonify({'success': False, 'error': 'Screenshot must be an image (png, jpg, jpeg, gif, webp).'}), 400
        safe_name = secure_filename(f"upi_addon_{current_user.id}_{transaction_id[:12]}.{ext}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        screenshot.save(os.path.join(upload_folder, safe_name))
        screenshot_filename = safe_name

    addon = AddonPayment(
        student_id=current_user.id,
        domain=domain,
        amount=PAYMENT_AMOUNT,
        transaction_id=transaction_id,
        status='pending',
    )
    if screenshot_filename:
        addon.screenshot_filename = screenshot_filename

    db.session.add(addon)
    db.session.commit()

    current_app.logger.info(
        f"UPI addon payment submitted — student_id={current_user.id}, domain={domain}, txn={transaction_id}, file={screenshot_filename}"
    )
    return jsonify({'success': True})



# ─────────────────────────────────────────────
# DOMAIN DETAIL
# ─────────────────────────────────────────────

@student_bp.route('/domain/<path:domain>')
@login_required
@student_required
def domain_detail(domain):
    main_payment = Payment.query.filter_by(student_id=current_user.id).first()
    if not main_payment:
        flash('Please complete your payment to access internship content.', 'warning')
        return redirect(url_for('student.payment'))

    if not student_has_domain_access(current_user._get_current_object(), domain):
        flash(f'You do not have access to "{domain}". Please purchase it first.', 'warning')
        return redirect(url_for('student.addon_payment', domain=domain))

    content = get_domain_content(domain)
    submission = ProjectSubmission.query.filter_by(student_id=current_user.id, domain=domain).first()
    return render_template('student/domain_detail.html', domain=domain,
                           student=current_user, content=content, submission=submission)


# ─────────────────────────────────────────────
# PAYMENT RECEIPT VIEW
# ─────────────────────────────────────────────

@student_bp.route('/receipt/<string:payment_type>/<int:payment_id>')
@login_required
def view_receipt(payment_type, payment_id):
    if payment_type == 'main':
        payment = Payment.query.get_or_404(payment_id)
        if payment.status != 'verified':
            abort(403)
        if not session.get('is_admin') and payment.student_id != current_user.id:
            abort(403)
        student = Student.query.get_or_404(payment.student_id)
        domain = student.internship_domain or 'Registration'
    elif payment_type == 'addon':
        payment = AddonPayment.query.get_or_404(payment_id)
        if payment.status != 'verified':
            abort(403)
        if not session.get('is_admin') and payment.student_id != current_user.id:
            abort(403)
        student = Student.query.get_or_404(payment.student_id)
        domain = payment.domain
    else:
        abort(404)

    return render_template('student/receipt_view.html', payment=payment, student=student, domain=domain, type_raw=payment_type)


# ─────────────────────────────────────────────
# PROJECT SUBMISSION
# ─────────────────────────────────────────────

@student_bp.route('/submit-project/<path:domain>', methods=['POST'])
@login_required
@student_required
def submit_project(domain):
    if not student_has_domain_access(current_user._get_current_object(), domain):
        flash('You do not have access to submit a project for this domain.', 'danger')
        return redirect(url_for('student.dashboard'))

    if 'project_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.referrer or url_for('student.dashboard'))
        
    file = request.files['project_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.referrer or url_for('student.dashboard'))
        
    if file:
        filename = secure_filename(file.filename)
        # Create unique filename
        import uuid
        unique_filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}_{filename}"
        
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Check if already submitted
        submission = ProjectSubmission.query.filter_by(
            student_id=current_user.id, 
            domain_name=domain
        ).first()
        
        if submission:
            submission.file_path = unique_filename
            submission.status = 'submitted'
        else:
            submission = ProjectSubmission(
                student_id=current_user.id,
                domain_name=domain,
                file_path=unique_filename
            )
            db.session.add(submission)
            
        db.session.commit()
        flash('Your project has been submitted successfully!', 'success')
        
    return redirect(request.referrer or url_for('student.domain_detail', domain=domain))
