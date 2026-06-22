import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'exposys_fallback_key')
    WTF_CSRF_SECRET_KEY = os.environ.get('SECRET_KEY', 'exposys_fallback_key')
    WTF_CSRF_TIME_LIMIT = None  # Tokens never expire — avoids "CSRF token expired" errors
    # Cloud DB: set DATABASE_URL in .env (e.g. from Neon/Supabase)
    # Local DB: set individual DB_* variables
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.environ.get('DB_USERNAME','root')}:"
            f"{os.environ.get('DB_PASSWORD','password')}@"
            f"{os.environ.get('DB_HOST','localhost')}:"
            f"{os.environ.get('DB_PORT','3306')}/"
            f"{os.environ.get('DB_NAME','exposys_db')}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    if "tidbcloud" in os.environ.get('DB_HOST', ''):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {
                'ssl': {'ssl_verify_cert': True, 'ssl_verify_identity': True}
            }
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 280,
            'pool_size': 5,
            'max_overflow': 2
        }

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    # Razorpay
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')

