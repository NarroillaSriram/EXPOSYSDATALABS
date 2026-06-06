import csv
import io
from functools import wraps
from flask import (Blueprint, render_template, flash, redirect, url_for,
                   request, session, Response)
from flask_login import login_required, current_user
from sqlalchemy import func
from models.models import Student, Admin, Payment, Contact, Internship, AddonPayment
from models import db

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin') or not isinstance(current_user, Admin):
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
    verified_payments = Payment.query.filter_by(status='verified').count()
    pending_payments = Payment.query.filter_by(status='pending').count()
    unread_contacts = Contact.query.filter_by(is_read=False).count()
    domain_stats = db.session.query(
        Student.internship_domain, func.count(Student.id)
    ).group_by(Student.internship_domain).all()
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
        total_students=total_students,
        total_payments=total_payments,
        verified_payments=verified_payments,
        pending_payments=pending_payments,
        unread_contacts=unread_contacts,
        domain_stats=domain_stats,
        recent_students=recent_students
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
    students_list = Student.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Branch', 'Email', 'College', 'Phone',
                     '10th%', '12th%', 'UG', 'PG', 'Location', 'Domain', 'Duration', 'Registered'])
    for s in students_list:
        writer.writerow([s.id, s.name, s.branch, s.email, s.college, s.phone,
                         s.tenth_percentage, s.twelfth_percentage, s.ug, s.pg,
                         s.location, s.internship_domain, s.duration,
                         s.created_at.strftime('%Y-%m-%d')])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=students.csv'})


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
        payment.status = new_status
        db.session.commit()
        flash(f'Payment status updated to {new_status}.', 'success')
    return redirect(url_for('admin.payments'))


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
        addon.status = new_status
        db.session.commit()
        flash(f'Addon payment status updated to {new_status}.', 'success')
    return redirect(url_for('admin.addon_payments'))

