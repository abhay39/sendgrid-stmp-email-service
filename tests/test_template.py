"""Tests for TemplateRenderer template engine module."""

from __future__ import annotations

from pathlib import Path
import pytest
from sendgrid_email_service.exceptions import EmailTemplateError
from sendgrid_email_service.template.renderer import TemplateRenderer


def test_default_templates_rendering() -> None:
    renderer = TemplateRenderer()
    templates = renderer.list_templates()
    assert "welcome.html" in templates
    assert "reset_password.html" in templates
    assert "verify_account.html" in templates

    # Test welcome template rendering
    html = renderer.render(
        "welcome",
        {
            "name": "Alex",
            "company_name": "FireCompass",
            "action_url": "https://example.com/start",
            "year": 2026,
        },
    )
    assert "Welcome, Alex!" in html
    assert "FireCompass" in html
    assert "https://example.com/start" in html


def test_rendering_with_extension() -> None:
    renderer = TemplateRenderer()
    html = renderer.render(
        "welcome.html",
        {"name": "Alex", "company_name": "Acme", "year": 2026},
    )
    assert "Welcome, Alex!" in html


def test_template_not_found_raises() -> None:
    renderer = TemplateRenderer()
    with pytest.raises(EmailTemplateError) as exc_info:
        renderer.render("non_existent_template", {})

    assert "non_existent_template.html' not found" in str(exc_info.value)
    assert exc_info.value.template_name == "non_existent_template"
    assert "welcome.html" in exc_info.value.available_templates


def test_empty_template_name_raises() -> None:
    renderer = TemplateRenderer()
    with pytest.raises(EmailTemplateError, match="non-empty string"):
        renderer.render("", {})


def test_custom_template_directory(tmp_path: Path) -> None:
    custom_dir = tmp_path / "templates"
    custom_dir.mkdir()
    tpl_file = custom_dir / "invoice.html"
    tpl_file.write_text("<h1>Invoice for {{ customer }}</h1><p>Amount: {{ amount }}</p>")

    renderer = TemplateRenderer(template_directory=custom_dir)
    assert "invoice.html" in renderer.list_templates()

    output = renderer.render("invoice", {"customer": "John", "amount": "$500"})
    assert "<h1>Invoice for John</h1>" in output
    assert "<p>Amount: $500</p>" in output


def test_template_syntax_error_handling(tmp_path: Path) -> None:
    custom_dir = tmp_path / "templates"
    custom_dir.mkdir()
    tpl_file = custom_dir / "broken.html"
    tpl_file.write_text("<h1>Hello {% if unclosed_tag }}</h1>")

    renderer = TemplateRenderer(template_directory=custom_dir)
    with pytest.raises(EmailTemplateError, match="Syntax error in template"):
        renderer.render("broken", {})


def test_render_string_success() -> None:
    renderer = TemplateRenderer()
    output = renderer.render_string(
        "<h1>Hello {{ name }}</h1><p>Token: {{ token }}</p>",
        {"name": "Bob", "token": "xyz123"},
    )
    assert output == "<h1>Hello Bob</h1><p>Token: xyz123</p>"


def test_render_string_syntax_error() -> None:
    renderer = TemplateRenderer()
    with pytest.raises(EmailTemplateError, match="Syntax error in template string"):
        renderer.render_string("<h1>Hello {% if unclosed_tag }}</h1>", {})


def test_render_string_invalid_type() -> None:
    renderer = TemplateRenderer()
    with pytest.raises(EmailTemplateError, match="Template source must be a string"):
        renderer.render_string(12345, {})  # type: ignore[arg-type]

