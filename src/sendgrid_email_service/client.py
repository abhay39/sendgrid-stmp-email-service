"""Client module for sendgrid_email_service SDK.

Provides the primary user-facing EmailClient class for configuring, rendering,
and dispatching emails.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Mapping, Sequence

from .config import EmailConfig
from .models import EmailMessage
from .template.renderer import TemplateRenderer
from .transport.smtp import SMTPTransport

logger = logging.getLogger(__name__)


class EmailClient:
    """Main client interface for sending emails using SMTP and Jinja2 templates."""

    def __init__(
        self,
        config: EmailConfig | None = None,
        template_directory: str | Path | None = None,
        transport: SMTPTransport | None = None,
    ) -> None:
        """Initialize the EmailClient instance.

        Args:
            config: Optional EmailConfig instance. If omitted, loaded from environment variables.
            template_directory: Optional path to custom Jinja2 template directory.
            transport: Optional custom transport instance. If omitted, SMTPTransport is used.
        """
        self.config = config or EmailConfig.from_env()
        self.transport = transport or SMTPTransport(self.config)
        self.renderer = TemplateRenderer(template_directory)

        logger.info(
            "EmailClient initialized successfully (Host: %s:%d, Sender: %s <%s>)",
            self.config.smtp_host,
            self.config.smtp_port,
            self.config.from_name,
            self.config.from_email,
        )

    def send(
        self,
        to: str | Sequence[str],
        subject: str,
        body: str | None = None,
        html: str | None = None,
        template: str | None = None,
        data: Mapping[str, Any] | None = None,
        cc: str | Sequence[str] | None = None,
        bcc: str | Sequence[str] | None = None,
        reply_to: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Send an email to one or more recipients.

        Args:
            to: Recipient email address or sequence of email addresses.
            subject: Subject line of the email.
            body: Plain text content of the email.
            html: HTML content of the email.
            template: Optional template name (e.g., 'welcome', 'reset_password') to render.
            data: Context variables dictionary to pass into the template.
            cc: Optional CC recipient(s).
            bcc: Optional BCC recipient(s).
            reply_to: Optional Reply-To address.
            headers: Optional custom email headers dictionary.

        Raises:
            EmailValidationError: If recipient, subject, or content is invalid.
            EmailTemplateError: If template rendering fails.
            EmailAuthenticationError: If SMTP authentication fails.
            EmailConnectionError: If connection to SMTP server fails.
            EmailTimeoutError: If connection or transmission times out.
            EmailRecipientsRefusedError: If the server rejects recipients.
            EmailSendError: If email delivery fails.
        """
        logger.debug("Preparing email with subject '%s'...", subject)

        rendered_html = html
        if template:
            logger.debug("Rendering template '%s' for outgoing email...", template)
            rendered_html = self.renderer.render(template, data or {})

        email = EmailMessage(
            to=to if isinstance(to, list) else list(to) if isinstance(to, (tuple, set)) else [to],
            subject=subject,
            body=body,
            html=rendered_html,
            cc=cc if isinstance(cc, list) else list(cc) if isinstance(cc, (tuple, set)) else [cc] if cc else [],
            bcc=bcc if isinstance(bcc, list) else list(bcc) if isinstance(bcc, (tuple, set)) else [bcc] if bcc else [],
            reply_to=reply_to,
            headers=dict(headers or {}),
        )

        self.transport.send(email)