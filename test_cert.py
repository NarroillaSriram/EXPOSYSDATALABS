import os
import sys

# Add the project root to sys.path so we can import from routes
sys.path.append(r"c:\Users\narro\Downloads\OneDrive\Desktop\exposys_project")

from datetime import date
from routes.cert_generator import generate_certificate_pdf

try:
    pdf_path = generate_certificate_pdf(
        student_name="John Doe",
        domain_name="Web Development",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 2, 1),
        issue_date=date(2023, 2, 5),
        certificate_id="TEST-CERT-1234",
        qr_code_path=None,  # skip qr code for testing
        duration_text="1 Month"
    )
    print("Successfully generated PDF at:", pdf_path)
except Exception as e:
    print("Error:", e)
