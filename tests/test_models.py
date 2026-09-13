"""Tests for EmailMessage data model."""

from __future__ import annotations

import pytest
from smtpkit.exceptions import EmailValidationError
from smtpkit.models import EmailMessage


def test_valid_email_message_creation() -> None:
    msg = EmailMessage(
        to=["user1@example.com", "user2@example.com"],
        subject="Test Subject",
        body="Hello Plaintext",
        html="<p>Hello HTML</p>",
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        reply_to="reply@example.com",
        headers={"X-Custom-Header": "value"},
    )
    assert msg.to == ["user1@example.com", "user2@example.com"]
    assert msg.subject == "Test Subject"
    assert msg.body == "Hello Plaintext"
    assert msg.html == "<p>Hello HTML</p>"
    assert msg.cc == ["cc@example.com"]
    assert msg.bcc == ["bcc@example.com"]
    assert msg.reply_to == "reply@example.com"
    assert msg.headers == {"X-Custom-Header": "value"}


def test_normalize_single_string_recipients() -> None:
    msg = EmailMessage(
        to="single@example.com",  # type: ignore
        subject="Test",
        body="Body",
        cc="cc@example.com",  # type: ignore
        bcc="bcc@example.com",  # type: ignore
    )
    assert msg.to == ["single@example.com"]
    assert msg.cc == ["cc@example.com"]
    assert msg.bcc == ["bcc@example.com"]


def test_empty_to_raises() -> None:
    with pytest.raises(EmailValidationError, match="'to' recipient list cannot be empty"):
        EmailMessage(to=[], subject="Test", body="Body")


def test_invalid_email_in_to_raises() -> None:
    with pytest.raises(EmailValidationError, match="Invalid email address"):
        EmailMessage(to=["not-an-email"], subject="Test", body="Body")


def test_empty_subject_raises() -> None:
    with pytest.raises(EmailValidationError, match="'subject' must be a non-empty string"):
        EmailMessage(to=["user@example.com"], subject="   ", body="Body")


def test_missing_body_and_html_raises() -> None:
    with pytest.raises(EmailValidationError, match="Either 'body' or 'html' content must be provided"):
        EmailMessage(to=["user@example.com"], subject="Subject", body=None, html=None)


def test_invalid_reply_to_raises() -> None:
    with pytest.raises(EmailValidationError, match="Invalid 'reply_to' address"):
        EmailMessage(to=["user@example.com"], subject="Subject", body="Body", reply_to="invalid-email")
