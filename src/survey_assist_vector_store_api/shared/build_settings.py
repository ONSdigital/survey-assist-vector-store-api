"""Shared settings base classes for local artifact build scripts."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseBuildSettings(BaseSettings):
    """Common CLI and environment configuration for build scripts."""

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_kebab_case=True,
        cli_implicit_flags="dual",
        extra="ignore",
        populate_by_name=True,
        env_file=".env",
    )
