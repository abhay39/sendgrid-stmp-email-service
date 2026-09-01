"""SMTP transport implementation for sendgrid_email_service SDK.

Handles SMTP connection lifecycle, TLS negotiation, authentication, message construction,
and granular exception handling with structured logging.
"""

from __future__ import annotations

import logging
import smtplib
import socket
from email.message import EmailMessage as PythonEmailMessage

from ..config import EmailConfig
from ..exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailRecipientsRefusedError,
    EmailSendError,
    EmailTimeoutError,
    EmailValidationError,
)
from ..models import EmailMessage

logger = logging.getLogger(__name__)


class SMTPTransport:
    """Delivers email messages via SMTP."""

    def __init__(self, config: EmailConfig) -> None:
        """Initialize SMTP transport with configuration settings.

        Args:
            config: An EmailConfig instance.
        """
        self.config = config

    def _build_mime_message(self, email: EmailMessage) -> PythonEmailMessage:
        """Construct a Python standard library EmailMessage from our model."""
        message = PythonEmailMessage()

        message["From"] = f"{self.config.from_name} <{self.config.from_email}>"
        message["To"] = ", ".join(email.to)
        message["Subject"] = email.subject

        if email.cc:
            message["Cc"] = ", ".join(email.cc)

        if email.reply_to:
            message["Reply-To"] = email.reply_to

        for header_name, header_value in email.headers.items():
            message[header_name] = header_value

        if email.body and email.html:
            message.set_content(email.body)
            message.add_alternative(email.html, subtype="html")
        elif email.html:
            message.set_content(email.html, subtype="html")
        elif email.body:
            message.set_content(email.body)
        else:
            raise EmailValidationError("Email must contain body or html content.")

        return message

    def send(self, email: EmailMessage) -> None:
        """Send an email message via SMTP.

        Args:
            email: EmailMessage object containing recipients, subject, and content.

        Raises:
            EmailValidationError: If the email structure or content is invalid.
            EmailAuthenticationError: If SMTP credentials fail.
            EmailConnectionError: If connection cannot be established.
            EmailTimeoutError: If the connection or operation times out.
            EmailRecipientsRefusedError: If the server refuses recipient addresses.
            EmailSendError: For any other SMTP protocol or delivery errors.
        """
        message = self._build_mime_message(email)

        logger.info(
            "Attempting to send email '%s' to %d recipient(s) via SMTP %s:%d (TLS=%s)...",
            email.subject,
            len(email.to),
            self.config.smtp_host,
            self.config.smtp_port,
            self.config.use_tls,
        )

        try:
            with smtplib.SMTP(
                self.config.smtp_host,
                self.config.smtp_port,
                timeout=self.config.timeout,
            ) as server:
                server.set_debuglevel(0)

                if self.config.use_tls:
                    logger.debug("Starting TLS negotiation with SMTP server...")
                    server.starttls()

                if self.config.smtp_username and self.config.smtp_password:
                    logger.debug(
                        "Authenticating with SMTP server as user '%s'...",
                        self.config.smtp_username,
                    )
                    server.login(
                        self.config.smtp_username,
                        self.config.smtp_password,
                    )

                server.send_message(message)
                logger.info(
                    "Email '%s' sent successfully to %s.",
                    email.subject,
                    ", ".join(email.to),
                )

        except smtplib.SMTPAuthenticationError as exc:
            msg = (
                f"SMTP authentication failed for user '{self.config.smtp_username}' "
                f"on {self.config.smtp_host}:{self.config.smtp_port}. Please check your credentials: {exc}"
            )
            logger.error(msg)
            raise EmailAuthenticationError(
                message=msg,
                username=self.config.smtp_username,
            ) from exc

        except smtplib.SMTPRecipientsRefused as exc:
            msg = f"SMTP server refused all recipients: {exc.recipients}"
            logger.error(msg)
            raise EmailRecipientsRefusedError(
                message=msg,
                recipients=exc.recipients,
            ) from exc

        except smtplib.SMTPSenderRefused as exc:
            msg = f"Sender address '{self.config.from_email}' was refused by SMTP server: {exc}"
            logger.error(msg)
            raise EmailSendError(message=msg) from exc

        except smtplib.SMTPDataError as exc:
            msg = f"SMTP data error occurred: {exc}"
            logger.error(msg)
            raise EmailSendError(message=msg) from exc

        except (smtplib.SMTPConnectError, ConnectionRefusedError, socket.gaierror) as exc:
            msg = (
                f"Failed to connect to SMTP server at {self.config.smtp_host}:{self.config.smtp_port}: {exc}"
            )
            logger.error(msg)
            raise EmailConnectionError(
                message=msg,
                host=self.config.smtp_host,
                port=self.config.smtp_port,
            ) from exc

        except (socket.timeout, TimeoutError) as exc:
            msg = (
                f"SMTP operation timed out after {self.config.timeout}s on "
                f"{self.config.smtp_host}:{self.config.smtp_port}: {exc}"
            )
            logger.error(msg)
            raise EmailTimeoutError(
                message=msg,
                timeout=self.config.timeout,
            ) from exc

        except smtplib.SMTPServerDisconnected as exc:
            msg = f"SMTP server disconnected unexpectedly: {exc}"
            logger.error(msg)
            raise EmailConnectionError(
                message=msg,
                host=self.config.smtp_host,
                port=self.config.smtp_port,
            ) from exc

        except smtplib.SMTPException as exc:
            msg = f"SMTP protocol error occurred: {exc}"
            logger.error(msg)
            raise EmailSendError(message=msg) from exc

        except OSError as exc:
            msg = (
                f"Network/OS error while connecting to SMTP server at "
                f"{self.config.smtp_host}:{self.config.smtp_port}: {exc}"
            )
            logger.error(msg)
            raise EmailConnectionError(
                message=msg,
                host=self.config.smtp_host,
                port=self.config.smtp_port,
            ) from exc

        except EmailValidationError:
            raise

        except Exception as exc:
            msg = f"Unexpected error while sending email via SMTP: {exc}"
            logger.error(msg)
            raise EmailSendError(message=msg) from exc