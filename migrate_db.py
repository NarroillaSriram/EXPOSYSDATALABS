import os
from flask import Flask
from models import db
from models.models import Student
from config import Config
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    # Use raw SQL to alter the columns to allow NULLs
    engine = db.engine
    with engine.connect() as conn:
        # Existing student table alterations
        # Adjust columns to be nullable (PostgreSQL syntax)
        conn.execute(text("ALTER TABLE students ALTER COLUMN branch TYPE VARCHAR(100);") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN branch DROP NOT NULL;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN college TYPE VARCHAR(200);") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN college DROP NOT NULL;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN phone TYPE VARCHAR(15);") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN phone DROP NOT NULL;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN tenth_percentage TYPE FLOAT;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN tenth_percentage DROP NOT NULL;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN twelfth_percentage TYPE FLOAT;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN twelfth_percentage DROP NOT NULL;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN location TYPE VARCHAR(100);") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN location DROP NOT NULL;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN internship_domain TYPE VARCHAR(100);") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN internship_domain DROP NOT NULL;") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN duration TYPE VARCHAR(50);") )
        conn.execute(text("ALTER TABLE students ALTER COLUMN duration DROP NOT NULL;") )
        # Add missing column to project_submissions if not exists
        conn.execute(text("ALTER TABLE project_submissions ADD COLUMN IF NOT EXISTS domain_name VARCHAR(100) NOT NULL DEFAULT 'unknown';"))
        print("Database schema successfully altered.")
