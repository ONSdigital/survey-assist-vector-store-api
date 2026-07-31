"""Dependency helpers for loading and accessing the shared SAYT suggester."""

from typing import cast

from fastapi import Request
from survey_assist_embed_core.sayt import SAYTSuggester

from survey_assist_vector_store_api.sayt_api.deps.settings import RuntimeSaytSettings


def load_suggester(settings: RuntimeSaytSettings) -> SAYTSuggester:
    """Construct the startup-loaded SAYT suggester from application settings."""
    return SAYTSuggester.from_artifact(settings.sayt_artifact_dir)


def get_suggester(request: Request) -> SAYTSuggester:
    """Return the SAYT suggester attached to application state."""
    suggester = getattr(request.state, "suggester", None)
    if suggester is None:
        raise RuntimeError("SAYT suggester is not configured in application state.")

    return cast(SAYTSuggester, suggester)
