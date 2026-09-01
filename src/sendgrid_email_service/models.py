"""Data models for sendgrid_email_service SDK.

Defines the core EmailMessage model with recipient normalization and validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .exceptions import EmailValidationError


@dataclass
class EmailMessage:
    """Represents an email message to be sent."""

    to: list[str]
    subject: str
    body: str | None = None
    html: str | None = None
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    reply_to: str | None = None
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize and validate message fields."""
        self.to = self._normalize_recipients(self.to, field_name="to")
        self.cc = self._normalize_recipients(self.cc, field_name="cc")
        self.bcc = self._normalize_recipients(self.bcc, field_name="bcc")

        if not self.to:
            raise EmailValidationError(
                "EmailMessage validation error: 'to' recipient list cannot be empty.",
                field="to",
            )

        if not self.subject or not isinstance(self.subject, str) or not self.subject.strip():
            raise EmailValidationError(
                "EmailMessage validation error: 'subject' must be a non-empty string.",
                field="subject",
            )
        self.subject = self.subject.strip()

        if not self.body and not self.html:
            raise EmailValidationError(
                "EmailMessage validation error: Either 'body' or 'html' content must be provided.",
                field="body",
            )

        if self.reply_to:
            self.reply_to = self.reply_to.strip()
            if not self.reply_to or "@" not in self.reply_to:
                raise EmailValidationError(
                    f"EmailMessage validation error: Invalid 'reply_to' address '{self.reply_to}'.",
                    field="reply_to",
                )

    @staticmethod
    def _normalize_recipients(recipients: str | Sequence[str] | None, field_name: str) -> list[str]:
        """Normalize recipient parameter into a clean list of email strings."""
        if recipients is None:
            return []
        if isinstance(recipients, str):
            recipients = [recipients]

        cleaned: list[str] = []
        for item in recipients:
            if not isinstance(item, str) or not item.strip():
                continue
            email_str = item.strip()
            if "@" not in email_str:
                raise EmailValidationError(
                    f"Invalid email address '{email_str}' in field '{field_name}'.",
                    field=field_name,
                )
            cleaned.append(email_str)

        return cleaned