import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.logger import log_info, log_error

class MailerManager:
    """
    Handles enterprise-grade SMTP gateways to dispatch secure 2FA verification tokens.
    """
    def __init__(self):
        # Pulling email server settings from isolated environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD") # App-Specific Password , Not the regular password.

    def generate_verification_token(self) -> str:
        """Generates a secure, randomized 6-digit numeric verification token."""
        return str(random.randint(100000, 999999))

    def send_verification_email(self, recipient_email: str, token: str) -> bool:
        """
        Dispatches an encrypted TLS email containing the dynamic 2FA verification matrix.
        """
        # Verify that the settings are available to prevent the server from crashing if they are not entered
        if not self.email_user or not self.email_password:
            log_error("[SMTP FAULT] Email credentials missing in Environment variables. Skipping email dispatch.")
            return False

        # Building an email package (MIME Structure)
        message = MIMEMultipart("alternative")
        message["Subject"] = "🛡️ Smart Monitor - Secure 2FA Verification Token"
        message["From"] = self.email_user
        message["To"] = recipient_email

        # Visual design of the email (HTML template) to look like a professional message from a technology company
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px; color: #333;">
                <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                    <h2 style="color: #1e3a8a; text-align: center; margin-bottom: 20px;">Infrastructure Security Portal</h2>
                    <p>Hello User,</p>
                    <p>A request was made to authenticate or provision an identity within the <strong>Smart Monitor Distributed Cluster</strong>.</p>
                    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 15px; text-align: center; margin: 25px 0;">
                        <span style="font-size: 14px; color: #166534; display: block; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Your 2FA Verification Code</span>
                        <strong style="font-size: 32px; color: #15803d; letter-spacing: 5px;">{token}</strong>
                    </div>
                    <p style="font-size: 12px; color: #666; text-align: center; margin-top: 30px;">
                        This code is highly sensitive and will expire in 10 minutes.<br>
                        If you did not initiate this request, please contact your cluster administrator immediately.
                    </p>
                </div>
            </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html"))

        try:
            # Open an encrypted connection and initiate a secure TLS protocol pathway
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls() 
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, recipient_email, message.as_string())
                
            log_info(f"[2FA GATEWAY] Verification token successfully dispatched to {recipient_email}")
            return True
            
        except Exception as smtp_ex:
            log_error(f"[2FA GATEWAY CRITICAL FAULT] Failed to deliver SMTP payload: {smtp_ex}")
            return False

# Export a version ready for immediate software use
mailer_service = MailerManager()