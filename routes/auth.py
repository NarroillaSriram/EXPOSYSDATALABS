from flask import Blueprint, render_template, flash, redirect, url_for, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.models import Student, Admin
from models import db, login_manager
from forms import RegistrationForm, LoginForm, AdminLoginForm
from models import oauth
import uuid

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('student_'):
        return Student.query.get(int(user_id.split('_')[1]))
    elif user_id.startswith('admin_'):
        return Admin.query.get(int(user_id.split('_')[1]))
    return None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), Student):
            from models.models import Payment
            payment = Payment.query.filter_by(student_id=current_user.id).first()
            if not payment:
                return redirect(url_for('student.payment'))
            return redirect(url_for('student.dashboard'))
        elif isinstance(current_user._get_current_object(), Admin):
            return redirect(url_for('admin.dashboard'))
    form = RegistrationForm()
    if request.method == 'GET' and request.args.get('domain'):
        form.internship_domain.data = request.args.get('domain')
    if form.validate_on_submit():
        existing = Student.query.filter_by(email=form.email.data).first()
        if existing:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('auth.login'))
        student = Student(
            name=form.name.data,
            branch=form.branch.data,
            email=form.email.data,
            college=form.college.data,
            phone=form.phone.data,
            tenth_percentage=form.tenth_percentage.data,
            twelfth_percentage=form.twelfth_percentage.data,
            ug=form.ug.data,
            pg=form.pg.data,
            location=form.location.data,
            internship_domain=form.internship_domain.data,
            duration=form.duration.data
        )
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()
        # Auto-login and redirect directly to payment page
        login_user(student)
        flash(f'Welcome {student.name}! Please complete your payment to confirm registration.', 'success')
        return redirect(url_for('student.payment'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), Student):
            from models.models import Payment
            payment = Payment.query.filter_by(student_id=current_user.id).first()
            if not payment:
                return redirect(url_for('student.payment'))
            return redirect(url_for('student.dashboard'))
        elif isinstance(current_user._get_current_object(), Admin):
            return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        if student and student.check_password(form.password.data):
            login_user(student, remember=form.remember.data)
            flash(f'Welcome back, {student.name}!', 'success')
            
            # Check if student has a payment
            from models.models import Payment
            payment = Payment.query.filter_by(student_id=student.id).first()
            if not payment:
                return redirect(url_for('student.payment'))
                
            next_page = request.args.get('next')
            return redirect(next_page or url_for('student.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)





@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        if isinstance(current_user._get_current_object(), Admin):
            return redirect(url_for('admin.dashboard'))
        elif isinstance(current_user._get_current_object(), Student):
            return redirect(url_for('student.dashboard'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('auth/admin_login.html', form=form)


@auth_bp.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    logout_user()
    flash('Admin logged out.', 'info')
    return redirect(url_for('auth.admin_login'))
