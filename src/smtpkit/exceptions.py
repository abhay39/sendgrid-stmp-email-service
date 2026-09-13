"""Exceptions module for smtpkit SDK.

Provides a clean and structured exception hierarchy for handling configuration,
validation, template rendering, and delivery errors.
"""

from __future__ import annotations

from typing import Any, Sequence


class EmailError(Exception):
    """Base exception for all errors raised by the email SDK."""

    def __init__(self, message: str = "An error occurred in the email service."):
        self.message = message
        super().__init__(self.message)


class EmailConfigurationError(EmailError):
    """Raised when email configuration or environment variables are missing or invalid."""

    def __init__(self, message: str = "Invalid email configuration provided."):
        super().__init__(message)


class EmailValidationError(EmailError):
    """Raised when email parameters or payload fail validation."""

    def __init__(self, message: str = "Email validation failed.", field: str | None = None):
        self.field = field
        super().__init__(message)


class EmailTemplateError(EmailError):
    """Raised when a template cannot be found, loaded, or rendered."""

    def __init__(
        self,
        message: str = "Template error occurred.",
        template_name: str | None = None,
        available_templates: Sequence[str] | None = None,
    ):
        self.template_name = template_name
        self.available_templates = list(available_templates) if available_templates else []
        super().__init__(message)


class EmailSendError(EmailError):
    """Raised when sending an email fails via the configured transport."""

    def __init__(self, message: str = "Failed to send email."):
        super().__init__(message)


class EmailConnectionError(EmailSendError):
    """Raised when a connection cannot be established with the SMTP server."""

    def __init__(
        self,
        message: str = "Failed to connect to SMTP server.",
        host: str | None = None,
        port: int | None = None,
    ):
        self.host = host
        self.port = port
        super().__init__(message)


class EmailAuthenticationError(EmailSendError):
    """Raised when SMTP authentication with the server fails."""

    def __init__(
        self,
        message: str = "SMTP authentication failed. Please verify your credentials.",
        username: str | None = None,
    ):
        self.username = username
        super().__init__(message)


class EmailTimeoutError(EmailSendError):
    """Raised when an operation times out while connecting or sending."""

    def __init__(
        self,
        message: str = "SMTP operation timed out.",
        timeout: float | None = None,
    ):
        self.timeout = timeout
        super().__init__(message)


class EmailRecipientsRefusedError(EmailSendError):
    """Raised when one or more recipient email addresses are rejected by the server."""

    def __init__(
        self,
        message: str = "One or more recipients were refused by the SMTP server.",
        recipients: dict[str, Any] | Sequence[str] | None = None,
    ):
        self.recipients = recipients
        super().__init__(message)