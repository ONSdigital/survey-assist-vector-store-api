"""Smoke Tests for the SAYT API."""

import os

import requests


class TestSaytApi:  # pylint: disable=too-few-public-methods
    """Smoke Tests for the SAYT API."""

    target_environment = os.environ.get("TARGET_ENVIRONMENT")
    if target_environment is None:
        print(
            """TARGET_ENVIRONMENT environment variable is not set.
            Optionally, set this to select the environment to proxy
            i.e. sandbox(default), dev or preprod."""
        )
        target_environment = "sandbox"

    url_base = os.environ.get("SAYT_API_URL")
    if url_base is None:
        raise ValueError("SAYT_API_URL environment variable is not set.")

    id_token = os.environ.get("UI_SA_ID_TOKEN")
    if id_token is None:
        raise ValueError("UI_SA_ID_TOKEN environment variable is not set.")

    def test_sayt_api_suggestions(self) -> None:
        """Test SAYT API."""
        endpoint = f"{self.url_base}/v1/suggestions"

        print(f"Calling {endpoint}...")
        response = requests.post(
            endpoint,
            json={"query": "soft"},
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        print("Checking status code is 200..")
        assert (  # noqa: S101
            response.status_code == 200  # noqa: PLR2004
        ), f"Expected status code 200, but got {response.status_code}."
