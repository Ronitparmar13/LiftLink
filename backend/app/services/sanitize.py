"""Text sanitization utilities for user-generated content."""

import bleach

_ALLOWED_TAGS: list[str] = []
_ALLOWED_ATTRIBUTES: dict[str, list[str]] = {}


def sanitize_text(text: str) -> str:
    """Strip all HTML tags from user-generated text."""
    return bleach.clean(
        text,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        strip=True,
    )
