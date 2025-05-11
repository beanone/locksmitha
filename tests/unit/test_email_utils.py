import logging
import smtplib
from unittest.mock import MagicMock, patch

import pytest

from locksmitha.config import Settings
from locksmitha.email_utils import send_email


@pytest.mark.parametrize(
    "smtp_tls,smtp_user,smtp_pass,expected_from",
    [
        (False, "", "", "noreply@example.com"),  # No TLS, no auth
        (True, "", "", "noreply@example.com"),  # TLS only
        (False, "user@example.com", "pass", "user@example.com"),  # Auth only
        (True, "user@example.com", "pass", "user@example.com"),  # TLS and auth
    ],
)
def test_send_email_branches(smtp_tls, smtp_user, smtp_pass, expected_from):
    """Test send_email covers all branches: TLS, auth, and From address logic."""
    with (
        patch("locksmitha.email_utils.Settings") as mock_settings,
        patch("locksmitha.email_utils.smtplib.SMTP") as mock_smtp,
    ):
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


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "user@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "password")
    monkeypatch.setenv("SMTP_TLS", "True")
    # Add other necessary env vars for Settings if any
    return Settings()


def test_send_email_smtp_exception(mock_settings, caplog):
    """Test that SMTPException is logged correctly."""
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        # Simulate an SMTPException during send_message
        mock_server.send_message.side_effect = smtplib.SMTPException("Test SMTP Error")
        mock_smtp.return_value.__enter__.return_value = mock_server

        with caplog.at_level(logging.ERROR):
            send_email("recipient@example.com", "Test Subject", "Test Body")

        assert any(
            "SMTP error: Test SMTP Error" in record.message
            and record.levelname == "ERROR"
            for record in caplog.records
        ), "SMTPException was not logged as expected."
        # Check that exc_info=True was used (exception info is present in the log)
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if "SMTP error" in record.message
        ), "exc_info was not True for SMTPException log."


def test_send_email_generic_exception(mock_settings, caplog):
    """Test that a generic Exception during SMTP operations is logged correctly."""
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        # Simulate a generic Exception during login, for instance
        mock_server.login.side_effect = Exception("Test Generic Error")
        mock_smtp.return_value.__enter__.return_value = mock_server

        with caplog.at_level(logging.ERROR):
            send_email("recipient@example.com", "Test Subject", "Test Body")

        assert any(
            "Unexpected error Test Generic Error" in record.message
            and record.levelname == "ERROR"
            for record in caplog.records
        ), "Generic Exception was not logged as expected."
        # Check that exc_info=True was used
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if "Unexpected error" in record.message
        ), "exc_info was not True for generic Exception log."


def test_send_email_smtp_exception_on_starttls(mock_settings, caplog):
    """Test that SMTPException during starttls is logged correctly."""
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_server.starttls.side_effect = smtplib.SMTPException(
            "Test SMTP Error on STARTTLS"
        )
        mock_smtp.return_value.__enter__.return_value = mock_server

        with caplog.at_level(logging.ERROR):
            send_email("recipient@example.com", "Test Subject", "Test Body")

        assert any(
            "SMTP error: Test SMTP Error on STARTTLS" in record.message
            and record.levelname == "ERROR"
            for record in caplog.records
        ), "SMTPException on STARTTLS was not logged as expected."
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if "SMTP error" in record.message
        ), "exc_info was not True for SMTPException (STARTTLS) log."


def test_send_email_generic_exception_on_context_manager(mock_settings, caplog):
    """Test that a generic Exception from SMTP context manager is logged."""
    with patch("smtplib.SMTP") as mock_smtp:
        # Simulate an exception when entering the SMTP context manager
        mock_smtp.side_effect = Exception("Test Generic Error on SMTP init")

        with caplog.at_level(logging.ERROR):
            send_email("recipient@example.com", "Test Subject", "Test Body")

        assert any(
            "Unexpected error Test Generic Error on SMTP init" in record.message
            and record.levelname == "ERROR"
            for record in caplog.records
        ), "Generic Exception on SMTP init was not logged as expected."
        assert any(
            record.exc_info is not None
            for record in caplog.records
            if "Unexpected error" in record.message
        ), "exc_info was not True for generic Exception (SMTP init) log."
