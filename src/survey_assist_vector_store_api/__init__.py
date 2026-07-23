"""Survey Assist Vector Store API package entry point."""

from survey_assist_vector_store_api.sayt_api.main import app as sayt_app
from survey_assist_vector_store_api.vector_store_api.main import app as vector_store_app

__all__ = [
    "sayt_app",
    "vector_store_app",
]
