"""Template rendering module for sendgrid_email_service SDK.

Uses Jinja2 to render HTML email templates with comprehensive error handling,
contextual error messages, and logging.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Mapping

import jinja2

from ..exceptions import EmailTemplateError

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders Jinja2 HTML email templates from a configured directory."""

    def __init__(
        self,
        template_directory: str | Path | None = None,
    ) -> None:
        """Initialize the TemplateRenderer.

        Args:
            template_directory: Directory containing HTML templates.
                Defaults to the built-in package templates directory.
        """
        if template_directory is None:
            self.template_directory = (Path(__file__).parent.parent / "templates").resolve()
        else:
            self.template_directory = Path(template_directory).resolve()

        if not self.template_directory.exists():
            logger.warning(
                "Template directory '%s' does not exist.",
                self.template_directory,
            )

        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_directory)),
            autoescape=True,
        )
        logger.debug(
            "TemplateRenderer initialized with directory: %s",
            self.template_directory,
        )

    def list_templates(self) -> list[str]:
        """List all available template names in the template directory."""
        if not self.template_directory.is_dir():
            return []
        return sorted([p.name for p in self.template_directory.glob("*.html")])

    def render(
        self,
        template_name: str,
        data: Mapping[str, Any] | None = None,
    ) -> str:
        """Render an HTML template with the given context data.

        Args:
            template_name: Name of the template (with or without '.html' extension).
            data: Context dictionary passed into the template.

        Returns:
            str: Rendered HTML string.

        Raises:
            EmailTemplateError: If the template is missing, has syntax errors, or fails rendering.
        """
        if not template_name or not isinstance(template_name, str):
            raise EmailTemplateError("Template name must be a non-empty string.")

        # Normalize filename
        filename = template_name if template_name.endswith(".html") else f"{template_name}.html"
        context = dict(data or {})

        logger.debug("Rendering template '%s' with context keys: %s", filename, list(context.keys()))

        try:
            template = self.environment.get_template(filename)
            rendered = template.render(**context)
            logger.debug("Successfully rendered template '%s' (output length: %d bytes).", filename, len(rendered))
            return rendered

        except jinja2.exceptions.TemplateNotFound as exc:
            available = self.list_templates()
            msg = (
                f"Template '{filename}' not found in template directory '{self.template_directory}'. "
                f"Available templates: {available}"
            )
            logger.error(msg)
            raise EmailTemplateError(
                message=msg,
                template_name=template_name,
                available_templates=available,
            ) from exc

        except jinja2.exceptions.TemplateSyntaxError as exc:
            msg = (
                f"Syntax error in template '{filename}' at line {exc.lineno}: {exc.message}"
            )
            logger.error(msg)
            raise EmailTemplateError(
                message=msg,
                template_name=template_name,
            ) from exc

        except jinja2.exceptions.TemplateError as exc:
            msg = f"Failed to render template '{filename}': {exc}"
            logger.error(msg)
            raise EmailTemplateError(
                message=msg,
                template_name=template_name,
            ) from exc

        except Exception as exc:
            msg = f"Unexpected error while rendering template '{filename}': {exc}"
            logger.error(msg)
            raise EmailTemplateError(
                message=msg,
                template_name=template_name,
            ) from exc

    def render_string(
        self,
        source: str,
        data: Mapping[str, Any] | None = None,
    ) -> str:
        """Render an in-memory HTML template string with the given context data.

        Args:
            source: Raw HTML template string containing Jinja2 syntax or static HTML.
            data: Context dictionary passed into the template.

        Returns:
            str: Rendered HTML string.

        Raises:
            EmailTemplateError: If the template string has syntax errors or fails rendering.
        """
        if not isinstance(source, str):
            raise EmailTemplateError("Template source must be a string.")

        context = dict(data or {})
        logger.debug("Rendering inline template string with context keys: %s", list(context.keys()))

        try:
            template = self.environment.from_string(source)
            rendered = template.render(**context)
            logger.debug("Successfully rendered template string (output length: %d bytes).", len(rendered))
            return rendered

        except jinja2.exceptions.TemplateSyntaxError as exc:
            msg = f"Syntax error in template string at line {exc.lineno}: {exc.message}"
            logger.error(msg)
            raise EmailTemplateError(
                message=msg,
                template_name="<string>",
            ) from exc

        except jinja2.exceptions.TemplateError as exc:
            msg = f"Failed to render template string: {exc}"
            logger.error(msg)
            raise EmailTemplateError(
                message=msg,
                template_name="<string>",
            ) from exc

        except Exception as exc:
            msg = f"Unexpected error while rendering template string: {exc}"
            logger.error(msg)
            raise EmailTemplateError(
                message=msg,
                template_name="<string>",
            ) from exc