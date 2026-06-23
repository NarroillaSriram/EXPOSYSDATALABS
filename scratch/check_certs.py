import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.models import Certificate

with app.app_context():
    certs = Certificate.query.all()
    for c in certs:
        print(f"ID: {c.id}, CertID: {c.certificate_id}, StudentID: {c.student_id}, Status: {c.status}, PDF: {c.pdf_path}")
        if c.pdf_path:
            import os
            # check if file exists
            base = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'certificate_system', 'backend'
            )
            # pdf_path is stored as '/uploads/certificates/...'
            full_path = base + c.pdf_path.replace('/', os.sep)
            print(f"  File exists: {os.path.exists(full_path)}")
            print(f"  Expected path: {full_path}")
