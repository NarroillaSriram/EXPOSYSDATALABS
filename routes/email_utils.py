import logging
from flask import render_template, current_app
from flask_mail import Message
from models import mail

def send_receipt_email(student, payment):
    """Send a payment receipt email to the student's email address."""
    try:
        subject = "Payment Receipt - Exposys Data Labs"
        
        # Render the HTML template for the email
        html_body = render_template('emails/payment_receipt.html', student=student, payment=payment)
        
        # Determine sender email, fallback to MAIL_USERNAME if MAIL_DEFAULT_SENDER is empty
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        if not sender:
            # Fallback when neither is defined (avoids mailing error)
            sender = "hr@exposysdata.com"
            
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[student.email]
        )
        msg.html = html_body
        
        mail.send(msg)
        current_app.logger.info(f"Receipt email successfully sent to {student.email} for payment ID {payment.transaction_id}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send receipt email to {student.email}: {e}", exc_info=True)
        return False
