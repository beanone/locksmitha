import smtplib
from email.message import EmailMessage

from .config import Settings


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

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if smtp_tls:
            server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
