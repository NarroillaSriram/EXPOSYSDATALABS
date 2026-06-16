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
        # Neon/Supabase provide postgres:// — SQLAlchemy needs postgresql://
        SQLALCHEMY_DATABASE_URI = _db_url.replace('postgres://', 'postgresql://', 1)
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{os.environ.get('DB_USERNAME','postgres')}:"
            f"{os.environ.get('DB_PASSWORD','password')}@"
            f"{os.environ.get('DB_HOST','localhost')}:"
            f"{os.environ.get('DB_PORT','5432')}/"
            f"{os.environ.get('DB_NAME','exposys_db')}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Fix Neon/cloud DB idle connection drops
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,       # Test connection before using — auto-reconnects if dropped
        'pool_recycle': 280,         # Recycle connections every 4.5 min (Neon drops after 5 min idle)
        'pool_size': 5,
        'max_overflow': 2,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
        }
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

