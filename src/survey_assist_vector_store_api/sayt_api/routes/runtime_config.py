"""Routes for runtime SAYT configuration."""

from typing import Annotated

from fastapi import APIRouter, Depends
from survey_assist_embed_core.sayt import SaytConfiguration, SAYTSuggester

from survey_assist_vector_store_api.sayt_api.deps.suggester import get_suggester

router = APIRouter(tags=["runtime"])


@router.get("/runtime-config", response_model=SaytConfiguration)
def runtime_config(
    suggester: Annotated[SAYTSuggester, Depends(get_suggester)],
) -> SaytConfiguration:
    """Return the effective configuration of the loaded SAYT suggester."""
    return suggester.get_config()
