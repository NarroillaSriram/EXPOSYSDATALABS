import csv
import io
import os
from functools import wraps
from flask import (Blueprint, render_template, flash, redirect, url_for,
                   request, session, Response, send_from_directory, abort)
from flask_login import login_required, current_user
from sqlalchemy import func
from models.models import Student, Admin, Payment, Contact, Internship, AddonPayment, Certificate, ProjectSubmission, JobApplication
from models import db

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin') or not isinstance(current_user._get_current_object(), Admin):
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    total_students = Student.query.count()
    total_payments = Payment.query.count()
    verified_payments = Payment.query.filter_by(status='verified').count() + AddonPayment.query.filter_by(status='verified').count()
    
    pending_main_count = Payment.query.filter_by(status='pending').count()
    pending_addons_count = AddonPayment.query.filter_by(status='pending').count()
    total_pending_payments = pending_main_count + pending_addons_count

    unread_contacts = Contact.query.filter_by(is_read=False).count()
    domain_stats = db.session.query(
        Student.internship_domain, func.count(Student.id)
    ).group_by(Student.internship_domain).all()
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    
    pending_submissions_count = ProjectSubmission.query.filter_by(status='submitted').count()
    recent_submissions = ProjectSubmission.query.order_by(ProjectSubmission.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_students=total_students,
        total_payments=total_payments,
        verified_payments=verified_payments,
        pending_payments=total_pending_payments,
        pending_main_count=pending_main_count,
        pending_addon_count=pending_addons_count,
        unread_contacts=unread_contacts,
        domain_stats=domain_stats,
        recent_students=recent_students,
        pending_submissions_count=pending_submissions_count,
        recent_submissions=recent_submissions
    )


@admin_bp.route('/admin/students')
@login_required
@admin_required
def students():
    search = request.args.get('search', '')
    domain = request.args.get('domain', '')
    query = Student.query
    if search:
        query = query.filter(
            Student.name.ilike(f'%{search}%') |
            Student.email.ilike(f'%{search}%') |
            Student.college.ilike(f'%{search}%')
        )
    if domain:
        query = query.filter_by(internship_domain=domain)
    students_list = query.order_by(Student.created_at.desc()).all()
    domains = db.session.query(Student.internship_domain).distinct().all()
    return render_template('admin/students.html',
        students=students_list, search=search,
        domain=domain, domains=[d[0] for d in domains]
    )


@admin_bp.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    Payment.query.filter_by(student_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {student.name} deleted successfully.', 'success')
    return redirect(url_for('admin.students'))


@admin_bp.route('/admin/students/export')
@login_required
@admin_required
def export_students():
    """Show a preview of all student data before download."""
    from datetime import datetime
    students_list = Student.query.order_by(Student.created_at.desc()).all()
    now = datetime.utcnow().strftime('%d %b %Y')
    return render_template('admin/export_preview.html',
                           students=students_list, now=now)


@admin_bp.route('/admin/students/download-csv')
@login_required
@admin_required
def download_csv():
    """Generate and download the student data as a CSV file (Excel-friendly UTF-8 BOM)."""
    import io as _io
    students_list = Student.query.order_by(Student.created_at.desc()).all()

    # Use BytesIO with utf-8-sig encoding — adds the BOM Excel needs
    output = _io.BytesIO()
    text_wrapper = _io.TextIOWrapper(output, encoding='utf-8-sig', newline='')
    writer = csv.writer(text_wrapper)
    writer.writerow(['ID', 'Name', 'Branch', 'Email', 'College', 'Phone',
                     '10th%', '12th%', 'UG', 'UG%', 'PG', 'Location', 'Domain', 'Duration', 'Registered'])
    for s in students_list:
        all_domains = [s.internship_domain] if s.internship_domain else []
        for addon in s.addon_payments:
            if addon.status == 'verified':
                all_domains.append(addon.domain)
        domains_str = ", ".join(all_domains)

        writer.writerow([s.id, s.name, s.branch or '', s.email, s.college or '',
                         s.phone or '', s.tenth_percentage or '', s.twelfth_percentage or '',
                         s.ug or '', s.ug_percentage or '', s.pg or '', s.location or '',
                         domains_str, s.duration or '',
                         s.created_at.strftime('%Y-%m-%d')])
    text_wrapper.flush()
    output.seek(0)

    from datetime import datetime
    filename = f"students_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        output.read(),
        mimetype='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@admin_bp.route('/admin/payments')
@login_required
@admin_required
def payments():
    status_filter = request.args.get('status', '')
    query = Payment.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    payments_list = query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments_list, status_filter=status_filter)


@admin_bp.route('/admin/payments/update/<int:payment_id>', methods=['POST'])
@login_required
@admin_required
def update_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'verified', 'rejected']:
        old_status = payment.status
        payment.status = new_status
        if new_status == 'verified' and old_status != 'verified':
            from datetime import datetime
            payment.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Payment status updated to {new_status}.', 'success')
        
        # Send receipt email if updated to verified
        if new_status == 'verified' and old_status != 'verified':
            from routes.email_utils import send_receipt_email
            student = Student.query.get(payment.student_id)
            if student:
                send_receipt_email(student, payment)
                
    return redirect(url_for('admin.payments'))


@admin_bp.route('/admin/uploads/<path:filename>')
@login_required
@admin_required
def serve_upload(filename):
    """Securely serve uploaded payment screenshots to admins only."""
    from flask import current_app
    upload_folder = current_app.config['UPLOAD_FOLDER']
    # Ensure filename does not start with a slash which would bypass the upload folder
    filename = filename.lstrip('/')
    full_path = os.path.join(upload_folder, filename)
    if not os.path.exists(full_path):
        current_app.logger.warning(f"Upload file not found: {full_path}")
        abort(404)
    return send_from_directory(upload_folder, filename)


@admin_bp.route('/admin/contacts')
@login_required
@admin_required
def contacts():
    contacts_list = Contact.query.order_by(Contact.created_at.desc()).all()
    Contact.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/contacts.html', contacts=contacts_list)


@admin_bp.route('/admin/contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
@admin_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact message deleted.', 'success')
    return redirect(url_for('admin.contacts'))


@admin_bp.route('/admin/addon-payments')
@login_required
@admin_required
def addon_payments():
    status_filter = request.args.get('status', '')
    query = AddonPayment.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    addon_list = query.order_by(AddonPayment.created_at.desc()).all()
    return render_template('admin/addon_payments.html', addon_payments=addon_list, status_filter=status_filter)


@admin_bp.route('/admin/addon-payments/update/<int:addon_id>', methods=['POST'])
@login_required
@admin_required
def update_addon_payment(addon_id):
    addon = AddonPayment.query.get_or_404(addon_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'verified', 'rejected']:
        old_status = addon.status
        addon.status = new_status
        if new_status == 'verified' and old_status != 'verified':
            from datetime import datetime
            addon.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Addon payment status updated to {new_status}.', 'success')
        
        # Send receipt email if updated to verified
        if new_status == 'verified' and old_status != 'verified':
            from routes.email_utils import send_receipt_email
            student = Student.query.get(addon.student_id)
            if student:
                send_receipt_email(student, addon)
    return redirect(url_for('admin.addon_payments'))


@admin_bp.route('/admin/students/approve-certificate/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def approve_certificate(student_id):
    return _issue_certificate(student_id, redirect_to=request.referrer or url_for('admin.certificates'))


def _issue_certificate(student_id, redirect_to=None, replace_existing=False):
    """Core logic to generate and issue a certificate (used for both issue and re-issue)."""
    import secrets
    from routes.cert_generator import (
        generate_qr_code, generate_certificate_pdf, compute_blockchain_hash
    )

    start_date  = request.form.get('start_date')
    end_date    = request.form.get('end_date')
    issue_date  = request.form.get('issue_date')
    domain_name = request.form.get('domain_name')

    if not start_date or not end_date or not issue_date or not domain_name:
        flash('All certificate fields (including domain name) are required.', 'danger')
        return redirect(redirect_to or url_for('admin.certificates'))

    student = Student.query.get_or_404(student_id)

    try:
        # Remove any existing certificate for this student + domain
        Certificate.query.filter_by(
            student_id=student_id, domain_name=domain_name
        ).delete()
        db.session.flush()

        # Unique certificate ID
        rand_hex = secrets.token_hex(4).upper()
        certificate_id = f"EXPOSYS-CERT-{student_id}-{rand_hex}"

        # Build verification URL
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        verification_url = f"{frontend_url}/verify/{certificate_id}"

        # QR code
        qr_path = generate_qr_code(certificate_id, verification_url)

        # Blockchain hash (simulated)
        meta = {
            'certificateId': certificate_id,
            'studentName': student.name,
            'domainName': domain_name,
            'startDate': start_date,
            'endDate': end_date,
            'issueDate': issue_date,
            'verificationUrl': verification_url,
        }
        blockchain_hash = compute_blockchain_hash(meta)
        tx_hash = f"0xSIM{secrets.token_hex(16)}"
        
        # Integrate with Blockchain via Node Backend
        try:
            import requests
            node_url = "http://localhost:5001/api/blockchain/register"
            headers = {"x-internal-secret": "exposys_internal_secret_key"}
            payload = {
                "certificateId": certificate_id,
                "studentName": student.name,
                "domainName": domain_name,
                "issueDate": str(issue_date),
                "certificateHash": blockchain_hash,
                "verificationUrl": verification_url
            }
            resp = requests.post(node_url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('success'):
                    tx_hash = data.get('txHash', tx_hash)
        except Exception as api_err:
            from flask import current_app
            current_app.logger.error(f"Failed to register on blockchain API: {api_err}")

        # Generate PDF
        pdf_path = generate_certificate_pdf(
            student_name=student.name,
            domain_name=domain_name,
            start_date=start_date,
            end_date=end_date,
            issue_date=issue_date,
            certificate_id=certificate_id,
            qr_code_path=qr_path
        )

        # Store relative paths (served via /certificate-files/ route)
        qr_rel  = f"/uploads/qr_codes/{certificate_id}.png"
        pdf_rel = f"/uploads/certificates/{certificate_id}.pdf"

        cert = Certificate(
            certificate_id=certificate_id,
            student_id=student_id,
            student_name=student.name,
            domain_name=domain_name,
            start_date=start_date,
            end_date=end_date,
            issue_date=issue_date,
            blockchain_hash=blockchain_hash,
            tx_hash=tx_hash,
            qr_code=qr_rel,
            pdf_path=pdf_rel,
            status='approved',
        )
        db.session.add(cert)
        
        # Update submission status if it exists
        submission = ProjectSubmission.query.filter_by(student_id=student_id, domain_name=domain_name).first()
        if submission:
            submission.status = 'approved'
            
        db.session.commit()

        flash(f'Certificate for {student.name} ({domain_name}) generated successfully! ✅', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Certificate generation failed: {str(e)}', 'danger')

    return redirect(redirect_to or url_for('admin.certificates'))


@admin_bp.route('/admin/students/revoke-certificate/<string:certificate_id>', methods=['POST'])
@login_required
@admin_required
def revoke_certificate(certificate_id):
    cert = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    try:
        cert.status = 'revoked'
        db.session.commit()
        flash('Certificate has been successfully revoked.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to revoke certificate: {str(e)}', 'danger')
    return redirect(request.referrer or url_for('admin.certificates'))


@admin_bp.route('/admin/students/reissue-certificate/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def reissue_certificate(student_id):
    """Delete the old (revoked) certificate and generate a brand-new one."""
    return _issue_certificate(student_id, redirect_to=request.referrer or url_for('admin.certificates'), replace_existing=True)


@admin_bp.route('/admin/students/hold-certificate/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def hold_certificate(student_id):
    import secrets
    domain_name = request.form.get('domain_name') or 'Unassigned'
    student = Student.query.get_or_404(student_id)
    try:
        Certificate.query.filter_by(student_id=student_id, domain_name=domain_name).delete()
        rand_hex = secrets.token_hex(4).upper()
        cert = Certificate(
            certificate_id=f"EXPOSYS-HLD-{student_id}-{rand_hex}",
            student_id=student_id,
            student_name=student.name,
            domain_name=domain_name,
            start_date=__import__('datetime').date.today(),
            end_date=__import__('datetime').date.today(),
            issue_date=__import__('datetime').date.today(),
            status='held',
        )
        db.session.add(cert)
        db.session.commit()
        flash('Certificate application placed on hold.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to place certificate on hold: {str(e)}', 'danger')
    return redirect(request.referrer or url_for('admin.certificates'))


@admin_bp.route('/admin/students/reject-certificate/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def reject_certificate(student_id):
    import secrets
    domain_name = request.form.get('domain_name') or 'Unassigned'
    student = Student.query.get_or_404(student_id)
    try:
        Certificate.query.filter_by(student_id=student_id, domain_name=domain_name).delete()
        rand_hex = secrets.token_hex(4).upper()
        cert = Certificate(
            certificate_id=f"EXPOSYS-REJ-{student_id}-{rand_hex}",
            student_id=student_id,
            student_name=student.name,
            domain_name=domain_name,
            start_date=__import__('datetime').date.today(),
            end_date=__import__('datetime').date.today(),
            issue_date=__import__('datetime').date.today(),
            status='rejected',
        )
        db.session.add(cert)
        db.session.commit()
        flash('Certificate application rejected.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to reject certificate: {str(e)}', 'danger')
    return redirect(request.referrer or url_for('admin.certificates'))


@admin_bp.route('/admin/certificates')
@login_required
@admin_required
def certificates():
    search = request.args.get('search', '')
    domain_filter = request.args.get('domain', '')
    
    # Query all students
    query = Student.query
    if search:
        query = query.filter(
            Student.name.ilike(f'%{search}%') |
            Student.email.ilike(f'%{search}%')
        )
    students_list = query.order_by(Student.created_at.desc()).all()
    
    # Construct list of courses/certificates
    courses = []
    for s in students_list:
        # 1. Main Internship Domain
        if s.internship_domain:
            cert = Certificate.query.filter_by(student_id=s.id, domain_name=s.internship_domain).first()
            courses.append({
                'student': s,
                'domain': s.internship_domain,
                'type': 'Main',
                'duration': s.duration or '1 Month',
                'certificate': cert
            })
        
        # 2. Add-on Domains
        for addon in s.addon_payments:
            if addon.status == 'verified':
                cert = Certificate.query.filter_by(student_id=s.id, domain_name=addon.domain).first()
                courses.append({
                    'student': s,
                    'domain': addon.domain,
                    'type': 'Add-on',
                    'duration': '1 Month', # Default addon duration or custom
                    'certificate': cert
                })
                
    # Apply domain filter if set
    if domain_filter:
        courses = [c for c in courses if c['domain'] == domain_filter]
        
    # Get distinct list of domains for filter dropdown
    domains = db.session.query(Student.internship_domain).distinct().all()
    addon_domains = db.session.query(AddonPayment.domain).distinct().all()
    all_domains = sorted(list(set([d[0] for d in domains if d[0]] + [ad[0] for ad in addon_domains if ad[0]])))

    return render_template('admin/certificates.html',
                           courses=courses,
                           search=search,
                           domain_filter=domain_filter,
                           domains=all_domains)


@admin_bp.route('/cert-files/<path:filepath>')
@login_required
@admin_required
def serve_cert_file(filepath):
    """Serve certificate PDFs and QR code images from the configured upload folder."""
    from flask import current_app, send_from_directory as sfd
    # Use the upload folder configured in the app's settings (certificate files are stored there)
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'certificate_system', 'backend', 'uploads')
    full_path = os.path.join(base, filepath)
    if not os.path.exists(full_path):
        abort(404)
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    return sfd(directory, filename)


@admin_bp.route('/public/cert-files/<path:filepath>')
def serve_cert_file_public(filepath):
    """Public route — serves QR code images for the public verification page (no login required)."""
    from flask import send_from_directory as sfd
    # Only allow qr_codes sub-folder for public access (not PDFs)
    if not filepath.startswith('qr_codes/'):
        abort(403)
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'certificate_system', 'backend', 'uploads')
    full_path = os.path.join(base, filepath)
    if not os.path.exists(full_path):
        abort(404)
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    return sfd(directory, filename)


@admin_bp.route('/admin/submissions')
@login_required
@admin_required
def submissions():
    submissions_list = ProjectSubmission.query.order_by(ProjectSubmission.created_at.desc()).all()
    return render_template('admin/submissions.html', submissions=submissions_list)

@admin_bp.route('/admin/job-applications')
@login_required
@admin_required
def job_applications():
    import json
    status_filter = request.args.get('status', '')
    query = JobApplication.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    applications = query.order_by(JobApplication.created_at.desc()).all()
    
    # Parse JSON fields for the template
    for app in applications:
        app.experience = json.loads(app.experience_json) if app.experience_json else []
        app.education = json.loads(app.education_json) if app.education_json else []
        
    return render_template('admin/job_applications.html', applications=applications, status_filter=status_filter)

@admin_bp.route('/admin/job-applications/update/<int:app_id>', methods=['POST'])
@login_required
@admin_required
def update_job_application(app_id):
    application = JobApplication.query.get_or_404(app_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'reviewed', 'interviewing', 'rejected']:
        application.status = new_status
        db.session.commit()
        flash(f'Application status updated to {new_status}.', 'success')
    return redirect(url_for('admin.job_applications'))

@admin_bp.route('/admin/job-applications/resume/<int:app_id>')
@login_required
@admin_required
def download_resume(app_id):
    application = JobApplication.query.get_or_404(app_id)
    from flask import current_app
    upload_folder = current_app.config['UPLOAD_FOLDER']
    # The resume_filename includes 'resumes/' e.g. resumes/resume_123_file.pdf
    filename = application.resume_filename
    full_path = os.path.join(upload_folder, filename)
    if not os.path.exists(full_path):
        flash('Resume file not found on server.', 'danger')
        return redirect(url_for('admin.job_applications'))
        
    directory = os.path.dirname(full_path)
    base_name = os.path.basename(full_path)
    return send_from_directory(directory, base_name, as_attachment=False)

