"""Application lifespan helpers for the SAYT API."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from survey_assist_utils.logging import get_logger

from survey_assist_vector_store_api.sayt_api.deps.settings import get_settings
from survey_assist_vector_store_api.sayt_api.deps.suggester import load_suggester

logger = get_logger(__name__)


def _cloud_run_cpu_limit() -> float | str | None:
    cpu_max_path = Path("/sys/fs/cgroup/cpu.max")
    if cpu_max_path.exists():
        quota_text, period_text = (
            cpu_max_path.read_text(encoding="utf-8").strip().split()
        )
        if quota_text == "max":
            return "max"
        return int(quota_text) / int(period_text)

    quota_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    period_path = Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    if quota_path.exists() and period_path.exists():
        quota_us = int(quota_path.read_text(encoding="utf-8").strip())
        period_us = int(period_path.read_text(encoding="utf-8").strip())
        if quota_us > 0:
            return quota_us / period_us
        return "max"

    return None


@asynccontextmanager
async def sayt_lifespan(_app: FastAPI) -> AsyncIterator[dict[str, object]]:
    """Load the SAYT suggester once and expose it through request state."""
    logger.info(
        "SAYT debug CPU info",
        os_cpu_count=os.cpu_count(),
        cgroup_cpu_limit=_cloud_run_cpu_limit(),
    )
    settings = get_settings()
    suggester = load_suggester(settings)
    yield {
        "suggester": suggester,
    }
