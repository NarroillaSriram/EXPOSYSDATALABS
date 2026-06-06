import os
import hmac
import hashlib
import razorpay
from flask import (Blueprint, render_template, flash, redirect, url_for,
                   request, current_app, jsonify)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.models import Payment, Student, AddonPayment
from models import db
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
        return True
    addon = AddonPayment.query.filter_by(
        student_id=student.id, domain=domain, status='verified'
    ).first()
    return addon is not None


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
    payment = Payment.query.filter_by(student_id=current_user.id).order_by(Payment.created_at.desc()).first()
    if not payment:
        flash('Please complete your payment to access the dashboard.', 'warning')
        return redirect(url_for('student.payment'))
    addon_payments = AddonPayment.query.filter_by(student_id=current_user.id).all()
    return render_template('student/dashboard.html', student=current_user, payment=payment,
                           addon_payments=addon_payments)


# ─────────────────────────────────────────────
# MAIN PAYMENT — Create Razorpay Order
# ─────────────────────────────────────────────

@student_bp.route('/payment', methods=['GET'])
@login_required
@student_required
def payment():
    existing = Payment.query.filter_by(student_id=current_user.id).first()
    razorpay_key = current_app.config['RAZORPAY_KEY_ID']
    return render_template('student/payment.html', existing=existing,
                           razorpay_key=razorpay_key, amount=PAYMENT_AMOUNT)


@student_bp.route('/create-order', methods=['POST'])
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

    return jsonify({
        'success': True,
        'redirect': url_for('student.registration_success')
    })


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
    main_payment = Payment.query.filter_by(student_id=current_user.id, status='verified').first()
    if not main_payment:
        flash('Your main internship payment must be verified before unlocking additional domains.', 'warning')
        return redirect(url_for('student.dashboard'))

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

    return jsonify({
        'success': True,
        'redirect': url_for('student.domain_detail', domain=domain)
    })


# ─────────────────────────────────────────────
# DOMAIN DETAIL
# ─────────────────────────────────────────────

@student_bp.route('/domain/<path:domain>')
@login_required
@student_required
def domain_detail(domain):
    main_payment = Payment.query.filter_by(student_id=current_user.id, status='verified').first()
    if not main_payment:
        flash('Please complete your payment to access internship content.', 'warning')
        return redirect(url_for('student.payment'))

    if not student_has_domain_access(current_user._get_current_object(), domain):
        flash(f'You do not have access to "{domain}". Please purchase it first.', 'warning')
        return redirect(url_for('student.addon_payment', domain=domain))

    content = get_domain_content(domain)
    return render_template('student/domain_detail.html', domain=domain,
                           student=current_user, content=content)
