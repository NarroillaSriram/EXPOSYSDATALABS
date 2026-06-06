import os
from flask import Flask
from models import db
from models.models import Student
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    # Use raw SQL to alter the columns to allow NULLs
    engine = db.engine
    with engine.connect() as conn:
        conn.execute("ALTER TABLE students MODIFY COLUMN branch VARCHAR(100) NULL;")
        conn.execute("ALTER TABLE students MODIFY COLUMN college VARCHAR(200) NULL;")
        conn.execute("ALTER TABLE students MODIFY COLUMN phone VARCHAR(15) NULL;")
        conn.execute("ALTER TABLE students MODIFY COLUMN tenth_percentage FLOAT NULL;")
        conn.execute("ALTER TABLE students MODIFY COLUMN twelfth_percentage FLOAT NULL;")
        conn.execute("ALTER TABLE students MODIFY COLUMN location VARCHAR(100) NULL;")
        conn.execute("ALTER TABLE students MODIFY COLUMN internship_domain VARCHAR(100) NULL;")
        conn.execute("ALTER TABLE students MODIFY COLUMN duration VARCHAR(50) NULL;")
        print("Database schema successfully altered.")
