# sendgrid-email-service

[![PyPI version](https://img.shields.io/pypi/v/sendgrid-email-service.svg)](https://pypi.org/project/sendgrid-email-service/)
[![Python Versions](https://img.shields.io/pypi/pyversions/sendgrid-email-service.svg)](https://pypi.org/project/sendgrid-email-service/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Type Checked: typed](https://img.shields.io/badge/typing-typed-blue.svg)](https://www.python.org/dev/peps/pep-0561/)

A modern, production-ready Python SDK for sending transactional and marketing emails via SMTP (including SendGrid SMTP relays) with built-in Jinja2 templating, structured logging, secure credential handling, and comprehensive exception management.

---

## Features

- 🚀 **Production-Grade Delivery**: Reliable SMTP transport supporting TLS encryption, authentication, and timeouts.
- 🎨 **Built-in & Custom Jinja2 Templates**: Comes with responsive pre-built templates (`welcome`, `reset_password`, `verify_account`) and allows custom template directories.
- 🪵 **Enterprise Logging**: PEP 282 compliant logging with `NullHandler` by default, granular log levels (`DEBUG`, `INFO`, `ERROR`), and automatic password masking.
- 🛡️ **Comprehensive Exception Hierarchy**: Clear, actionable exceptions for validation, templates, authentication, connection timeouts, and delivery errors.
- ⚙️ **Flexible Configuration**: Seamlessly configure via `.env` files, environment variables, or typed `EmailConfig` objects.
- 📦 **PEP 561 Compliant**: Fully typed (`py.typed`) for autocomplete and static analysis with MyPy and IDEs.

---

## Installation

Install via `pip`:

```bash
pip install sendgrid-email-service
```

---

## Quick Start

### 1. Environment Configuration

Create a `.env` file in your project root or set environment variables:

```ini
# SMTP Configuration (SendGrid, Mailpit, Amazon SES, or custom SMTP)
EMAIL_SMTP_HOST=smtp.sendgrid.net
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=apikey
EMAIL_SMTP_PASSWORD=your-sendgrid-api-key

# Sender Defaults
EMAIL_FROM=notifications@yourdomain.com
EMAIL_FROM_NAME=Your Company

# Optional Settings
EMAIL_USE_TLS=true
EMAIL_TIMEOUT=30
```

### 2. Send Plain Text or HTML Email

```python
from sendgrid_email_service import EmailClient

# Automatically loads configuration from .env / environment variables
client = EmailClient()

# Send a simple email
client.send(
    to="recipient@example.com",
    subject="Welcome to Our Platform",
    body="Hello! Thank you for joining us.",
)
```

---

## Working with Templates

`sendgrid-email-service` includes responsive, production-ready HTML templates out of the box.

### Built-in Templates

| Template Name | Description | Available Context Variables |
| :--- | :--- | :--- |
| `welcome` | Onboarding & welcome message | `name`, `company_name`, `action_url`, `year` |
| `reset_password` | Password recovery with secure action button | `name`, `reset_url`, `company_name`, `expiry_hours`, `support_email`, `year` |
| `verify_account` | Email verification & activation link | `name`, `verification_url`, `company_name`, `expiry_hours`, `support_email`, `year` |

### Example: Sending a Template Email

```python
from sendgrid_email_service import EmailClient

client = EmailClient()

client.send(
    to="user@example.com",
    subject="Welcome to FireCompass!",
    template="welcome",
    data={
        "name": "Jane Doe",
        "company_name": "FireCompass",
        "action_url": "https://app.firecompass.com/dashboard",
        "year": 2026,
    },
)
```

### Example: Using Custom Templates

You can point `EmailClient` to your own Jinja2 template directory:

```python
from pathlib import Path
from sendgrid_email_service import EmailClient

client = EmailClient(template_directory=Path("./my_custom_templates"))

client.send(
    to="customer@example.com",
    subject="Your Invoice is Ready",
    template="monthly_invoice",  # Looks for monthly_invoice.html in ./my_custom_templates
    data={
        "customer_name": "Acme Corp",
        "invoice_number": "INV-2026-001",
        "amount_due": "$149.00",
    },
)
```

---

## Programmatic Configuration

Instead of environment variables, you can configure the client directly using `EmailConfig`:

```python
from sendgrid_email_service import EmailClient, EmailConfig

config = EmailConfig(
    smtp_host="smtp.sendgrid.net",
    smtp_port=587,
    smtp_username="apikey",
    smtp_password="your-api-key-here",
    from_email="no-reply@company.com",
    from_name="My Company",
    use_tls=True,
    timeout=30,
)

client = EmailClient(config=config)
```

---

## Exception Handling

The SDK provides a clean exception hierarchy inheriting from `EmailError`:

```
EmailError (Base)
├── EmailConfigurationError
├── EmailValidationError
├── EmailTemplateError
└── EmailSendError
    ├── EmailConnectionError
    ├── EmailAuthenticationError
    ├── EmailTimeoutError
    └── EmailRecipientsRefusedError
```

### Example: Robust Error Handling

```python
import logging
from sendgrid_email_service import (
    EmailClient,
    EmailAuthenticationError,
    EmailConnectionError,
    EmailRecipientsRefusedError,
    EmailTimeoutError,
    EmailValidationError,
    EmailTemplateError,
    EmailSendError,
    EmailError,
)

client = EmailClient()

try:
    client.send(
        to="client@example.com",
        subject="Important Update",
        template="welcome",
        data={"name": "Alice", "company_name": "Acme Inc."},
    )

except EmailValidationError as e:
    print(f"Invalid email input on field '{e.field}': {e}")

except EmailTemplateError as e:
    print(f"Template error ({e.template_name}): {e}")

except EmailAuthenticationError as e:
    print(f"SMTP Auth failure for user '{e.username}': {e}")

except EmailConnectionError as e:
    print(f"Could not connect to SMTP server ({e.host}:{e.port}): {e}")

except EmailTimeoutError as e:
    print(f"Operation timed out after {e.timeout}s: {e}")

except EmailRecipientsRefusedError as e:
    print(f"Server refused recipients {e.recipients}: {e}")

except EmailSendError as e:
    print(f"Failed to send email: {e}")

except EmailError as e:
    print(f"General email SDK error: {e}")
```

---

## Logging Configuration

`sendgrid-email-service` adheres to Python library best practices (PEP 282). By default, it emits no logs unless your application configures logging.

### Example: Enabling Logs in Your Application

```python
import logging
import sys

# Configure root or package logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Enable DEBUG logging specifically for sendgrid_email_service
logging.getLogger("sendgrid_email_service").setLevel(logging.DEBUG)
```

> **Security Guarantee**: Passwords and sensitive credentials are automatically masked (e.g. `***`) and are never written to log files.

---

## Local Development with Mailpit

You can test email sending locally using [Mailpit](https://github.com/axllent/mailpit) included via Docker Compose:

1. Start Mailpit:
   ```bash
   docker compose up -d
   ```
2. Set `.env` to point to localhost:
   ```ini
   EMAIL_SMTP_HOST=localhost
   EMAIL_SMTP_PORT=1025
   EMAIL_USE_TLS=false
   ```
3. View sent emails in your browser at `http://localhost:8025`.

---

## Running Tests

Install dev dependencies and run `pytest`:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Publishing to PyPI

1. **Build distribution archives**:
   ```bash
   python -m build
   ```

2. **Verify archives with Twine**:
   ```bash
   twine check dist/*
   ```

3. **Upload to TestPyPI** (Optional):
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

---

## License

Distributed under the [MIT License](LICENSE).
# sendgrid-stmp-email-service
