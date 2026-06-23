import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flask import Flask
from config import Config
from models import db, login_manager, oauth, csrf, mail
from models.models import Admin
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
 

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'warning'

    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_payment_status():
        from flask_login import current_user
        has_payment = False
        if current_user.is_authenticated:
            from models.models import Student, Payment
            if isinstance(current_user._get_current_object(), Student):
                has_payment = Payment.query.filter_by(student_id=current_user.id, status='verified').first() is not None
        return dict(has_payment=has_payment)

    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    from models.models import Admin, Internship

    admin = Admin.query.first()
    if not admin:
        admin = Admin(
            name='Admin',
            email=os.environ.get('ADMIN_EMAIL', 'admin@exposys.com')
        )
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'Admin@123'))
        db.session.add(admin)
    else:
        # Update existing admin details to match current configuration
        admin.email = os.environ.get('ADMIN_EMAIL', 'admin@exposys.com')
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'Admin@123'))

    if not Internship.query.first():
        internships = [
            Internship(title='Web Development', domain='Web Development',
                       description='Learn full-stack web development with modern frameworks.',
                       duration_options='1 Month, 2 Months, 3 Months', stipend='Certificate + LOR'),
            Internship(title='Data Science', domain='Data Science',
                       description='Master data analysis, visualization and statistical modeling.',
                       duration_options='2 Months, 3 Months, 6 Months', stipend='Certificate + LOR'),
            Internship(title='Machine Learning', domain='Machine Learning',
                       description='Build intelligent systems using ML algorithms.',
                       duration_options='2 Months, 3 Months, 6 Months', stipend='Certificate + LOR'),
            Internship(title='Artificial Intelligence', domain='Artificial Intelligence',
                       description='Explore AI concepts, NLP, and computer vision.',
                       duration_options='3 Months, 6 Months', stipend='Certificate + LOR'),
            Internship(title='Android Development', domain='Android Development',
                       description='Build Android apps using Java and Kotlin.',
                       duration_options='1 Month, 2 Months, 3 Months', stipend='Certificate + LOR'),
            Internship(title='Cloud Computing', domain='Cloud Computing',
                       description='Learn AWS, Azure, and GCP cloud platforms.',
                       duration_options='2 Months, 3 Months', stipend='Certificate + LOR'),
            Internship(title='Cybersecurity', domain='Cybersecurity',
                       description='Ethical hacking, penetration testing and security.',
                       duration_options='2 Months, 3 Months', stipend='Certificate + LOR'),
            Internship(title='UI/UX Design', domain='UI/UX Design',
                       description='Design beautiful user interfaces and experiences.',
                       duration_options='1 Month, 2 Months', stipend='Certificate + LOR'),
        ]
        db.session.add_all(internships)

    db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
