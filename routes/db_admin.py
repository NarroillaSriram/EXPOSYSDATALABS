from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request
from models.models import Admin as AdminModel, Student, Internship, Payment, Contact, AddonPayment, Certificate, ProjectSubmission, JobApplication
from models import db

class SecureAdminIndexView(AdminIndexView):
    def __init__(self, **kwargs):
        super(SecureAdminIndexView, self).__init__(endpoint='flask_admin', url='/admin_db', **kwargs)

    def is_accessible(self):
        return current_user.is_authenticated and isinstance(current_user._get_current_object(), AdminModel)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.admin_login'))

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and isinstance(current_user._get_current_object(), AdminModel)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.admin_login'))

def init_admin(app):
    # url='/admin_db' to avoid conflict with existing '/admin' routes
    admin = Admin(app, name='Exposys Database Viewer', template_mode='bootstrap3', url='/admin_db', endpoint='flask_admin', index_view=SecureAdminIndexView())


    
    # Add views for all major tables
    admin.add_view(AdminModelView(AdminModel, db.session, name='Admins', endpoint='admin_admins'))
    admin.add_view(AdminModelView(Student, db.session, name='Students', endpoint='admin_students'))
    admin.add_view(AdminModelView(Internship, db.session, name='Internships', endpoint='admin_internships'))
    admin.add_view(AdminModelView(Payment, db.session, name='Payments', endpoint='admin_payments'))
    admin.add_view(AdminModelView(AddonPayment, db.session, name='Addon Payments', endpoint='admin_addon_payments'))
    admin.add_view(AdminModelView(Certificate, db.session, name='Certificates', endpoint='admin_certificates_view'))
    admin.add_view(AdminModelView(ProjectSubmission, db.session, name='Submissions', endpoint='admin_submissions_view'))
    admin.add_view(AdminModelView(JobApplication, db.session, name='Job Applications', endpoint='admin_job_apps'))
    admin.add_view(AdminModelView(Contact, db.session, name='Contacts', endpoint='admin_contacts_view'))
