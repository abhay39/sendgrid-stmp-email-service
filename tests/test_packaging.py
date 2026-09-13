"""Tests for package exports, versioning, and structure."""

from __future__ import annotations

from pathlib import Path
import smtpkit


def test_package_version() -> None:
    assert hasattr(smtpkit, "__version__")
    assert smtpkit.__version__ == "0.1.1"



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
        assert hasattr(smtpkit, export), f"Missing export: {export}"
        assert export in smtpkit.__all__


def test_templates_exist_in_package() -> None:
    pkg_dir = Path(smtpkit.__file__).parent
    templates_dir = pkg_dir / "templates"
    assert templates_dir.is_dir()
    assert (templates_dir / "welcome.html").is_file()
    assert (templates_dir / "reset_password.html").is_file()
    assert (templates_dir / "verify_account.html").is_file()
    assert (pkg_dir / "py.typed").is_file()
