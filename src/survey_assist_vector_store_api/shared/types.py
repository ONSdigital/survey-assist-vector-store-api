"""Shared typing helpers for service entrypoints."""

from typing import Any, Protocol


class StructuredLogger(Protocol):  # pylint: disable=too-few-public-methods
    """Minimal logger interface required by shared HTTP and app helpers."""

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message with structured context."""
