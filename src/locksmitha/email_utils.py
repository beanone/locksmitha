import logging
import smtplib
from email.message import EmailMessage

from .config import Settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    """Send an email using SMTP settings from environment variables."""
    settings = Settings()
    smtp_host = settings.smtp_host
    smtp_port = settings.smtp_port
    smtp_user = settings.smtp_user
    smtp_pass = settings.smtp_password
    smtp_tls = settings.smtp_tls

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user or "noreply@example.com"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_tls:
                logger.info("Starting TLS")
                server.starttls()
            if smtp_user and smtp_pass:
                logger.info("Logging in to SMTP server")
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            logger.info(f"Email successfully sent to {to_email}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error {e}", exc_info=True)
