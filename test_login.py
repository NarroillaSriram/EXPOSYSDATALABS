from app import app
from models.models import Student

with app.app_context():
    email = 'kalki@gmail.com'
    password = 'Kalki@1234'
    student = Student.query.filter_by(email=email).first()
    if student:
        print(f"Student found: {student.email}")
        is_correct = student.check_password(password)
        print(f"Password check for '{password}': {is_correct}")
    else:
        print("Student not found.")
