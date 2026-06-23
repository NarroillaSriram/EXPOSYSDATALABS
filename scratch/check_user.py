import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.models import Student, Admin

with app.app_context():
    print("--- Admins ---")
    admins = Admin.query.all()
    for a in admins:
        print(f"ID: {a.id}, Name: {a.name}, Email: {a.email}")
        
    print("\n--- Students matching varanasi ---")
    students = Student.query.filter(Student.email.like('%varanasi%')).all()
    for s in students:
        print(f"ID: {s.id}, Name: {s.name}, Email: {s.email}, Password Correct: {s.check_password('Varanasi@1234')}")
        # Let's set it to Varanasi@1234 just in case they forgot or had typo
        s.set_password('Varanasi@1234')
        import sqlalchemy
        db_session = sqlalchemy.orm.object_session(s)
        db_session.commit()
        print(f"--> Password updated to 'Varanasi@1234' for {s.email}")
