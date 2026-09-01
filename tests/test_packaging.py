"""Tests for package exports, versioning, and structure."""

from __future__ import annotations

from pathlib import Path
import sendgrid_email_service


def test_package_version() -> None:
    assert hasattr(sendgrid_email_service, "__version__")
    assert sendgrid_email_service.__version__ == "0.1.0"


def test_package_exports() -> None:
    expected_exports = [
        "EmailClient",
        "EmailConfig",
        "EmailMessage",
        "TemplateRenderer",
        "SMTPTransport",
        "EmailError",
        "EmailConfigurationError",
        "EmailValidationError",
        "EmailTemplateError",
        "EmailSendError",
        "EmailConnectionError",
        "EmailAuthenticationError",
        "EmailTimeoutError",
        "EmailRecipientsRefusedError",
        "__version__",
    ]
    for export in expected_exports:
        assert hasattr(sendgrid_email_service, export), f"Missing export: {export}"
        assert export in sendgrid_email_service.__all__


def test_templates_exist_in_package() -> None:
    pkg_dir = Path(sendgrid_email_service.__file__).parent
    templates_dir = pkg_dir / "templates"
    assert templates_dir.is_dir()
    assert (templates_dir / "welcome.html").is_file()
    assert (templates_dir / "reset_password.html").is_file()
    assert (templates_dir / "verify_account.html").is_file()
    assert (pkg_dir / "py.typed").is_file()
