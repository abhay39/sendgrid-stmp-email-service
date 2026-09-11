"""Tests for EmailClient user-facing client module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sendgrid_email_service.client import EmailClient
from sendgrid_email_service.config import EmailConfig
from sendgrid_email_service.exceptions import EmailValidationError
from sendgrid_email_service.models import EmailMessage


@pytest.fixture
def mock_transport() -> MagicMock:
    return MagicMock()


@pytest.fixture
def sample_config() -> EmailConfig:
    return EmailConfig(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="user",
        smtp_password="password",
        from_email="noreply@example.com",
        from_name="App",
    )


def test_client_send_plain_body(mock_transport: MagicMock, sample_config: EmailConfig) -> None:
    client = EmailClient(config=sample_config, transport=mock_transport)

    client.send(
        to="user@example.com",
        subject="Greetings",
        body="Hello there!",
    )

    mock_transport.send.assert_called_once()
    sent_email: EmailMessage = mock_transport.send.call_args[0][0]
    assert sent_email.to == ["user@example.com"]
    assert sent_email.subject == "Greetings"
    assert sent_email.body == "Hello there!"
    assert sent_email.html is None


def test_client_send_template(mock_transport: MagicMock, sample_config: EmailConfig) -> None:
    client = EmailClient(config=sample_config, transport=mock_transport)

    client.send(
        to=["user1@example.com", "user2@example.com"],
        subject="Welcome Onboard",
        template="welcome",
        data={"name": "Alice", "company_name": "FireCompass", "year": 2026},
        cc="manager@example.com",
        bcc=["archive@example.com"],
        reply_to="support@example.com",
    )

    mock_transport.send.assert_called_once()
    sent_email: EmailMessage = mock_transport.send.call_args[0][0]
    assert sent_email.to == ["user1@example.com", "user2@example.com"]
    assert sent_email.subject == "Welcome Onboard"
    assert "Welcome, Alice!" in (sent_email.html or "")
    assert "FireCompass" in (sent_email.html or "")
    assert sent_email.cc == ["manager@example.com"]
    assert sent_email.bcc == ["archive@example.com"]
    assert sent_email.reply_to == "support@example.com"


def test_client_validation_error_on_empty_recipients(
    mock_transport: MagicMock, sample_config: EmailConfig
) -> None:
    client = EmailClient(config=sample_config, transport=mock_transport)

    with pytest.raises(EmailValidationError, match="'to' recipient list cannot be empty"):
        client.send(to=[], subject="Test", body="Body")

    mock_transport.send.assert_not_called()


def test_client_send_raw_html(mock_transport: MagicMock, sample_config: EmailConfig) -> None:
    client = EmailClient(config=sample_config, transport=mock_transport)

    raw_html = "<html><body><h1>Hello World</h1></body></html>"
    client.send(
        to="user@example.com",
        subject="Raw HTML Test",
        html=raw_html,
    )

    mock_transport.send.assert_called_once()
    sent_email: EmailMessage = mock_transport.send.call_args[0][0]
    assert sent_email.to == ["user@example.com"]
    assert sent_email.subject == "Raw HTML Test"
    assert sent_email.html == raw_html


def test_client_send_html_with_data_template(mock_transport: MagicMock, sample_config: EmailConfig) -> None:
    client = EmailClient(config=sample_config, transport=mock_transport)

    html_template = "<html><body><p>Token: {{ verification_token }}, Year: {{ year }}</p></body></html>"
    client.send(
        to="user@example.com",
        subject="Account verification",
        html=html_template,
        data={
            "verification_token": "abc-123-xyz",
            "year": 2026,
        },
    )

    mock_transport.send.assert_called_once()
    sent_email: EmailMessage = mock_transport.send.call_args[0][0]
    assert sent_email.to == ["user@example.com"]
    assert sent_email.subject == "Account verification"
    assert "Token: abc-123-xyz, Year: 2026" in (sent_email.html or "")

