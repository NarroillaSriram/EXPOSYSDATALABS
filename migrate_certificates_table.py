import os
import sys
from datetime import datetime, timedelta
import re

# Add the project directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db
from models.models import Certificate

def parse_duration_months(duration_str):
    if not duration_str:
        return 1
    match = re.search(r'(\d+)\s*month', duration_str, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 1

with app.app_context():
    # 1. Fetch current certificates data using raw SQL
    connection = db.engine.raw_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, student_id, student_name, domain, duration, issue_date, certificate_hash, pdf_filename, qr_code_path FROM certificates")
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} certificates for backup.")
    except Exception as e:
        print(f"Error fetching certificates: {e}")
        sys.exit(1)
    finally:
        connection.close()

    # 2. Drop the existing tables
    print("Dropping table 'blockchain_records' (unused)...")
    db.session.execute("DROP TABLE IF EXISTS blockchain_records")
    print("Dropping table 'certificates'...")
    db.session.execute("DROP TABLE IF EXISTS certificates")
    db.session.commit()
    print("Dropped table 'certificates' successfully.")

    # 3. Recreate the table with the new schema from models.py
    print("Recreating table 'certificates' with updated schema...")
    db.create_all()
    print("Recreated table 'certificates' successfully.")

    # 4. Migrate and insert records
    print("Migrating and inserting records...")
    for row in rows:
        old_id, student_id, student_name, domain, duration, issue_date, certificate_hash, pdf_filename, qr_code_path = row
        
        # Parse issue_date
        if isinstance(issue_date, datetime):
            issue_date_val = issue_date.date()
        elif issue_date:
            try:
                issue_date_val = datetime.strptime(str(issue_date).split(' ')[0], "%Y-%m-%d").date()
            except Exception:
                issue_date_val = datetime.utcnow().date()
        else:
            issue_date_val = datetime.utcnow().date()
            
        months = parse_duration_months(duration)
        start_date_val = issue_date_val - timedelta(days=months * 30)
        end_date_val = issue_date_val
        
        certificate_id = old_id
        # Map paths to match the expected new format
        qr_code = f"/uploads/qr_codes/{certificate_id}.png"
        pdf_path = f"/uploads/certificates/{certificate_id}.pdf"
        
        # We simulate tx_hash as it wasn't present in the old schema
        tx_hash = "0xSIMULATED_MIGRATION"
        
        cert = Certificate(
            certificate_id=certificate_id,
            student_id=student_id,
            student_name=student_name,
            domain_name=domain,
            start_date=start_date_val,
            end_date=end_date_val,
            issue_date=issue_date_val,
            blockchain_hash=certificate_hash,
            tx_hash=tx_hash,
            qr_code=qr_code,
            status='approved',
            pdf_path=pdf_path,
            created_at=datetime.combine(issue_date_val, datetime.min.time()),
            updated_at=datetime.combine(issue_date_val, datetime.min.time())
        )
        db.session.add(cert)
        
    db.session.commit()
    print(f"Data migration completed successfully! All {len(rows)} records restored in the new schema.")
