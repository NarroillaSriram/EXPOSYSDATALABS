from app import app
from models.models import Student

with app.app_context():
    students = Student.query.filter_by(email='kalki@gmail.com').all()
    print(f"Found {len(students)} students with email kalki@gmail.com")
    for s in students:
        print(f"ID: {s.id}, Email: {s.email}, PW Check: {s.check_password('Kalki@1234')}")
