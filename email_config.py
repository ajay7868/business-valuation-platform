from flask_mail import Mail, Message
from flask import current_app
import os

mail = Mail()

def send_verification_email(user_email, verification_token):
    """Send verification email to user"""
    try:
        # Create verification link
        verification_url = f"http://localhost:5000/api/auth/verify/{verification_token}"
        
        # Email content
        subject = "Verify Your Email - Business Valuation Platform"
        body = f"""
        Welcome to the Business Valuation Platform!
        
        Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        Business Valuation Platform Team
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Send email
        mail.send(msg)
        return True, "Verification email sent successfully"
        
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return False, f"Failed to send verification email: {str(e)}"

def send_welcome_email(user_email):
    """Send welcome email after successful verification"""
    try:
        subject = "Welcome to Business Valuation Platform!"
        body = f"""
        Congratulations! Your email has been verified successfully.
        
        You can now:
        - Upload financial documents
        - Generate comprehensive valuation reports
        - Access AI-powered business analysis
        - Download reports in multiple formats (PDF, Excel, Word)
        
        Login to your account and start using the platform!
        
        Best regards,
        Business Valuation Platform Team
        """
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail.send(msg)
        return True, "Welcome email sent successfully"
        
    except Exception as e:
        print(f"Welcome email error: {str(e)}")
        return False, f"Failed to send welcome email: {str(e)}"
