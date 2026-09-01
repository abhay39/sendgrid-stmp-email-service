"""SendGrid Email Service SDK.

A modern, robust Python SDK for sending transactional and marketing emails
via SMTP with built-in Jinja2 templating, structured logging, and comprehensive
error handling.
"""

from __future__ import annotations

import logging

from .client import EmailClient
from .config import EmailConfig
from .exceptions import (
    EmailAuthenticationError,
    EmailConfigurationError,
    EmailConnectionError,
    EmailError,
    EmailRecipientsRefusedError,
    EmailSendError,
    EmailTemplateError,
    EmailTimeoutError,
    EmailValidationError,
)
from .models import EmailMessage
from .template.renderer import TemplateRenderer
from .transport.smtp import SMTPTransport

# Set up NullHandler for library logging according to PEP 282
logging.getLogger("sendgrid_email_service").addHandler(logging.NullHandler())

__version__ = "0.0.1"

__all__ = [
    "EmailClient",
    "EmailConfig",
    "EmailMessage",
    "TemplateRenderer",
    "SMTPTransport",
    # Exceptions
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