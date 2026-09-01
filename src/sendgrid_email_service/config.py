"""Configuration module for sendgrid_email_service SDK.

Provides strongly typed configuration management with environment variable loading,
input validation, secure credential masking, and structured logging.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .exceptions import EmailConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Configuration settings for SMTP transport and email metadata."""

    smtp_host: str
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None

    from_email: str = "no-reply@company.com"
    from_name: str = "Company"

    use_tls: bool = True
    timeout: int = 30

    def __post_init__(self) -> None:
        """Validate configuration parameters after initialization."""
        if not self.smtp_host or not isinstance(self.smtp_host, str) or not self.smtp_host.strip():
            raise EmailConfigurationError(
                "Invalid configuration: 'smtp_host' must be a non-empty string."
            )

        if not isinstance(self.smtp_port, int) or not (1 <= self.smtp_port <= 65535):
            raise EmailConfigurationError(
                f"Invalid configuration: 'smtp_port' must be an integer between 1 and 65535, got {self.smtp_port}."
            )

        if not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
            raise EmailConfigurationError(
                f"Invalid configuration: 'timeout' must be a positive number, got {self.timeout}."
            )

        if not self.from_email or not isinstance(self.from_email, str) or "@" not in self.from_email:
            raise EmailConfigurationError(
                f"Invalid configuration: 'from_email' must be a valid email address, got '{self.from_email}'."
            )

    @classmethod
    def from_env(
        cls,
        env_file: str | Path | None = None,
        load_dotenv_file: bool = True,
    ) -> EmailConfig:
        """Load and validate email configuration from environment variables.

        Args:
            env_file: Optional path to a .env file to load.
            load_dotenv_file: Whether to automatically load .env files. Defaults to True.

        Returns:
            EmailConfig: Validated email configuration instance.

        Raises:
            EmailConfigurationError: If required environment variables are missing or invalid.
        """
        if load_dotenv_file:
            if env_file:
                load_dotenv(dotenv_path=env_file)
            else:
                load_dotenv()

        smtp_host = os.getenv("EMAIL_SMTP_HOST")
        if not smtp_host or not smtp_host.strip():
            logger.error("Configuration error: EMAIL_SMTP_HOST environment variable is missing or empty.")
            raise EmailConfigurationError(
                "Missing required environment variable: 'EMAIL_SMTP_HOST'. "
                "Please set EMAIL_SMTP_HOST in your environment or .env file."
            )

        raw_port = os.getenv("EMAIL_SMTP_PORT", "587")
        try:
            smtp_port = int(raw_port)
        except (ValueError, TypeError):
            logger.error("Configuration error: Invalid EMAIL_SMTP_PORT '%s'.", raw_port)
            raise EmailConfigurationError(
                f"Invalid value for 'EMAIL_SMTP_PORT': '{raw_port}'. Must be a valid integer."
            )

        raw_timeout = os.getenv("EMAIL_TIMEOUT", "30")
        try:
            timeout = int(raw_timeout)
        except (ValueError, TypeError):
            logger.error("Configuration error: Invalid EMAIL_TIMEOUT '%s'.", raw_timeout)
            raise EmailConfigurationError(
                f"Invalid value for 'EMAIL_TIMEOUT': '{raw_timeout}'. Must be a valid integer."
            )

        raw_use_tls = os.getenv("EMAIL_USE_TLS", "true").strip().lower()
        use_tls = raw_use_tls in ("true", "1", "yes", "t", "on")

        config = cls(
            smtp_host=smtp_host.strip(),
            smtp_port=smtp_port,
            smtp_username=os.getenv("EMAIL_SMTP_USERNAME") or None,
            smtp_password=os.getenv("EMAIL_SMTP_PASSWORD") or None,
            from_email=os.getenv("EMAIL_FROM", "no-reply@company.com").strip(),
            from_name=os.getenv("EMAIL_FROM_NAME", "Company").strip(),
            use_tls=use_tls,
            timeout=timeout,
        )

        logger.debug(
            "EmailConfig loaded successfully from environment: host=%s, port=%d, tls=%s, from=%s <%s>",
            config.smtp_host,
            config.smtp_port,
            config.use_tls,
            config.from_name,
            config.from_email,
        )
        return config

    def __repr__(self) -> str:
        """Safe representation masking sensitive credentials."""
        masked_pwd = "***" if self.smtp_password else None
        return (
            f"EmailConfig(smtp_host={self.smtp_host!r}, smtp_port={self.smtp_port}, "
            f"smtp_username={self.smtp_username!r}, smtp_password={masked_pwd!r}, "
            f"from_email={self.from_email!r}, from_name={self.from_name!r}, "
            f"use_tls={self.use_tls}, timeout={self.timeout})"
        )