"""Tests for SMTPTransport transport module."""

from __future__ import annotations

import smtplib
import socket
from unittest.mock import MagicMock, patch

import pytest
from smtpkit.config import EmailConfig
from smtpkit.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailRecipientsRefusedError,
    EmailSendError,
    EmailTimeoutError,
    EmailValidationError,
)
from smtpkit.models import EmailMessage
from smtpkit.transport.smtp import SMTPTransport


@pytest.fixture
def sample_config() -> EmailConfig:
    return EmailConfig(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="apikey",
        smtp_password="secret-password",
        from_email="noreply@example.com",
        from_name="Test Company",
        use_tls=True,
        timeout=10,
    )


def test_smtp_send_plain_text(sample_config: EmailConfig) -> None:
    transport = SMTPTransport(sample_config)
    email = EmailMessage(
        to=["recipient@example.com"],
        subject="Plain Text Email",
        body="Hello world!",
    )

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        transport.send(email)

        mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("apikey", "secret-password")
        mock_server.send_message.assert_called_once()

        sent_msg = mock_server.send_message.call_args[0][0]
        assert sent_msg["From"] == "Test Company <noreply@example.com>"
        assert sent_msg["To"] == "recipient@example.com"
        assert sent_msg["Subject"] == "Plain Text Email"
        assert sent_msg.get_content().strip() == "Hello world!"


def test_smtp_send_html_and_body_multipart(sample_config: EmailConfig) -> None:
    transport = SMTPTransport(sample_config)
    email = EmailMessage(
        to=["recipient@example.com"],
        subject="Multipart Email",
        body="Plain text fallback",
        html="<h1>HTML Content</h1>",
        cc=["cc@example.com"],
        reply_to="support@example.com",
        headers={"X-Custom": "Value123"},
    )

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        transport.send(email)

        sent_msg = mock_server.send_message.call_args[0][0]
        assert sent_msg["Cc"] == "cc@example.com"
        assert sent_msg["Reply-To"] == "support@example.com"
        assert sent_msg["X-Custom"] == "Value123"
        assert sent_msg.is_multipart()


def test_smtp_authentication_failure(sample_config: EmailConfig) -> None:
    transport = SMTPTransport(sample_config)
    email = EmailMessage(to=["user@example.com"], subject="Test", body="Body")

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        with pytest.raises(EmailAuthenticationError) as exc_info:
            transport.send(email)

        assert "SMTP authentication failed" in str(exc_info.value)
        assert exc_info.value.username == "apikey"


def test_smtp_recipients_refused(sample_config: EmailConfig) -> None:
    transport = SMTPTransport(sample_config)
    email = EmailMessage(to=["invalid@example.com"], subject="Test", body="Body")

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_server.send_message.side_effect = smtplib.SMTPRecipientsRefused(
            {"invalid@example.com": (550, b"User not found")}
        )
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        with pytest.raises(EmailRecipientsRefusedError) as exc_info:
            transport.send(email)

        assert "refused all recipients" in str(exc_info.value)
        assert "invalid@example.com" in exc_info.value.recipients


def test_smtp_connection_refused(sample_config: EmailConfig) -> None:
    transport = SMTPTransport(sample_config)
    email = EmailMessage(to=["user@example.com"], subject="Test", body="Body")

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_smtp_cls.side_effect = ConnectionRefusedError("Connection refused by host")

        with pytest.raises(EmailConnectionError) as exc_info:
            transport.send(email)

        assert "Failed to connect to SMTP server" in str(exc_info.value)
        assert exc_info.value.host == "smtp.example.com"
        assert exc_info.value.port == 587


def test_smtp_timeout_error(sample_config: EmailConfig) -> None:
    transport = SMTPTransport(sample_config)
    email = EmailMessage(to=["user@example.com"], subject="Test", body="Body")

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_server.send_message.side_effect = socket.timeout("Timed out waiting for socket")
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        with pytest.raises(EmailTimeoutError) as exc_info:
            transport.send(email)

        assert "timed out after 10" in str(exc_info.value)
        assert exc_info.value.timeout == 10


def test_smtp_protocol_error(sample_config: EmailConfig) -> None:
    transport = SMTPTransport(sample_config)
    email = EmailMessage(to=["user@example.com"], subject="Test", body="Body")

    with patch("smtplib.SMTP") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_server.send_message.side_effect = smtplib.SMTPDataError(554, b"Transaction failed")
        mock_smtp_cls.return_value.__enter__.return_value = mock_server

        with pytest.raises(EmailSendError, match="SMTP data error"):
            transport.send(email)
