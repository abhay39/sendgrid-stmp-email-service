"""Tests for logging behavior and security (no credential leaking)."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest
from sendgrid_email_service import EmailClient, EmailConfig, SMTPTransport
from sendgrid_email_service.models import EmailMessage


def test_top_level_logger_has_null_handler() -> None:
    pkg_logger = logging.getLogger("sendgrid_email_service")
    handlers = [h for h in pkg_logger.handlers if isinstance(h, logging.NullHandler)]
    assert len(handlers) >= 1


def test_logging_during_smtp_send(caplog: pytest.LogCaptureFixture) -> None:
    config = EmailConfig(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="my_user",
        smtp_password="super_secret_password_12345",
        from_email="noreply@example.com",
        from_name="MyApp",
    )
    transport = SMTPTransport(config)
    email = EmailMessage(
        to=["recipient@example.com"],
        subject="Secret Test",
        body="Message body",
    )

    with caplog.at_level(logging.DEBUG, logger="sendgrid_email_service"):
        with patch("smtplib.SMTP") as mock_smtp_cls:
            mock_server = MagicMock()
            mock_smtp_cls.return_value.__enter__.return_value = mock_server
            transport.send(email)

    log_text = caplog.text

    # Verify meaningful logs exist
    assert "Attempting to send email 'Secret Test'" in log_text
    assert "Email 'Secret Test' sent successfully" in log_text

    # Security check: verify password is NEVER logged anywhere
    assert "super_secret_password_12345" not in log_text


def test_config_logging_does_not_leak_password(caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.production.com")
    monkeypatch.setenv("EMAIL_SMTP_PASSWORD", "ultra_sensitive_token_999")
    monkeypatch.setenv("EMAIL_FROM", "alert@prod.com")

    with caplog.at_level(logging.DEBUG, logger="sendgrid_email_service"):
        EmailConfig.from_env()

    log_text = caplog.text
    assert "ultra_sensitive_token_999" not in log_text
