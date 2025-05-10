from unittest.mock import MagicMock, patch

import pytest

from locksmitha.email_utils import send_email


@pytest.mark.parametrize(
    "smtp_tls,smtp_user,smtp_pass,expected_from",
    [
        (False, "", "", "noreply@example.com"),  # No TLS, no auth
        (True, "", "", "noreply@example.com"),   # TLS only
        (False, "user@example.com", "pass", "user@example.com"),  # Auth only
        (True, "user@example.com", "pass", "user@example.com"),   # TLS and auth
    ]
)
def test_send_email_branches(smtp_tls, smtp_user, smtp_pass, expected_from):
    """Test send_email covers all branches: TLS, auth, and From address logic."""
    with patch("locksmitha.email_utils.Settings") as mock_settings, \
         patch("locksmitha.email_utils.smtplib.SMTP") as mock_smtp:
        # Mock settings
        instance = mock_settings.return_value
        instance.smtp_host = "localhost"
        instance.smtp_port = 1025
        instance.smtp_user = smtp_user
        instance.smtp_password = smtp_pass
        instance.smtp_tls = smtp_tls

        # Mock SMTP context manager
        smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = smtp_instance

        send_email("to@example.com", "Subject", "Body")

        mock_smtp.assert_called_once_with("localhost", 1025)
        # Check starttls if TLS is enabled
        if smtp_tls:
            smtp_instance.starttls.assert_called_once()
        else:
            smtp_instance.starttls.assert_not_called()
        # Check login if auth is provided
        if smtp_user and smtp_pass:
            smtp_instance.login.assert_called_once_with(smtp_user, smtp_pass)
        else:
            smtp_instance.login.assert_not_called()
        # Check send_message called with correct EmailMessage
        args, kwargs = smtp_instance.send_message.call_args
        msg = args[0]
        assert msg["To"] == "to@example.com"
        assert msg["Subject"] == "Subject"
        assert msg["From"] == expected_from
        assert msg.get_content().strip() == "Body"
