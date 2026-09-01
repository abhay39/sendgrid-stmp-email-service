"""Tests for EmailConfig configuration module."""

from __future__ import annotations

import os
import pytest
from sendgrid_email_service.config import EmailConfig
from sendgrid_email_service.exceptions import EmailConfigurationError


def test_valid_config_init() -> None:
    config = EmailConfig(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="user@example.com",
        smtp_password="secretpassword",
        from_email="noreply@example.com",
        from_name="Test Company",
        use_tls=True,
        timeout=15,
    )
    assert config.smtp_host == "smtp.example.com"
    assert config.smtp_port == 587
    assert config.smtp_username == "user@example.com"
    assert config.smtp_password == "secretpassword"
    assert config.from_email == "noreply@example.com"
    assert config.from_name == "Test Company"
    assert config.use_tls is True
    assert config.timeout == 15


@pytest.mark.parametrize(
    "invalid_host",
    ["", "   ", None],
)
def test_invalid_smtp_host_raises(invalid_host: str | None) -> None:
    with pytest.raises(EmailConfigurationError, match="smtp_host"):
        EmailConfig(smtp_host=invalid_host)  # type: ignore


@pytest.mark.parametrize(
    "invalid_port",
    [0, -1, 65536, 100000, "587"],  # type: ignore
)
def test_invalid_smtp_port_raises(invalid_port: int) -> None:
    with pytest.raises(EmailConfigurationError, match="smtp_port"):
        EmailConfig(smtp_host="smtp.example.com", smtp_port=invalid_port)


@pytest.mark.parametrize(
    "invalid_timeout",
    [0, -5, "30"],  # type: ignore
)
def test_invalid_timeout_raises(invalid_timeout: int) -> None:
    with pytest.raises(EmailConfigurationError, match="timeout"):
        EmailConfig(smtp_host="smtp.example.com", timeout=invalid_timeout)


@pytest.mark.parametrize(
    "invalid_email",
    ["", "invalid-email-no-at", 123],  # type: ignore
)
def test_invalid_from_email_raises(invalid_email: str) -> None:
    with pytest.raises(EmailConfigurationError, match="from_email"):
        EmailConfig(smtp_host="smtp.example.com", from_email=invalid_email)


def test_password_masked_in_repr() -> None:
    config = EmailConfig(
        smtp_host="smtp.example.com",
        smtp_password="super_secret_password",
    )
    repr_str = repr(config)
    assert "super_secret_password" not in repr_str
    assert "***" in repr_str


def test_from_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.custom.org")
    monkeypatch.setenv("EMAIL_SMTP_PORT", "465")
    monkeypatch.setenv("EMAIL_SMTP_USERNAME", "custom_user")
    monkeypatch.setenv("EMAIL_SMTP_PASSWORD", "custom_pass")
    monkeypatch.setenv("EMAIL_FROM", "admin@custom.org")
    monkeypatch.setenv("EMAIL_FROM_NAME", "Custom Admin")
    monkeypatch.setenv("EMAIL_USE_TLS", "false")
    monkeypatch.setenv("EMAIL_TIMEOUT", "45")

    config = EmailConfig.from_env(load_dotenv_file=False)
    assert config.smtp_host == "smtp.custom.org"
    assert config.smtp_port == 465
    assert config.smtp_username == "custom_user"
    assert config.smtp_password == "custom_pass"
    assert config.from_email == "admin@custom.org"
    assert config.from_name == "Custom Admin"
    assert config.use_tls is False
    assert config.timeout == 45


def test_from_env_missing_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EMAIL_SMTP_HOST", raising=False)
    with pytest.raises(EmailConfigurationError, match="EMAIL_SMTP_HOST"):
        EmailConfig.from_env(load_dotenv_file=False)


def test_from_env_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.custom.org")
    monkeypatch.setenv("EMAIL_SMTP_PORT", "not_a_number")
    with pytest.raises(EmailConfigurationError, match="EMAIL_SMTP_PORT"):
        EmailConfig.from_env(load_dotenv_file=False)


def test_from_env_invalid_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.custom.org")
    monkeypatch.setenv("EMAIL_TIMEOUT", "invalid_seconds")
    with pytest.raises(EmailConfigurationError, match="EMAIL_TIMEOUT"):
        EmailConfig.from_env(load_dotenv_file=False)
