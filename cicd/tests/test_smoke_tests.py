"""Smoke Tests for the SAYT API."""

import os

import requests


class TestSicSocSaytApi:  # pylint: disable=too-few-public-methods
    """Smoke Tests for the SIC, SOC and SAYT APIs."""

    target_environment = os.environ.get("TARGET_ENVIRONMENT")
    if target_environment is None:
        print(
            """TARGET_ENVIRONMENT environment variable is not set.
            Optionally, set this to select the environment to proxy
            i.e. sandbox(default), dev or preprod."""
        )
        target_environment = "sandbox"

    sic_url_base = os.environ.get("SIC_API_URL")
    if sic_url_base is None:
        raise ValueError("SIC_API_URL environment variable is not set.")

    soc_url_base = os.environ.get("SOC_API_URL")
    if soc_url_base is None:
        raise ValueError("SOC_API_URL environment variable is not set.")

    sayt_url_base = os.environ.get("SAYT_API_URL")
    if sayt_url_base is None:
        raise ValueError("SAYT_API_URL environment variable is not set.")

    id_token = os.environ.get("UI_SA_ID_TOKEN")
    if id_token is None:
        raise ValueError("UI_SA_ID_TOKEN environment variable is not set.")

    def test_sic_api_configuration(self) -> None:
        """Test SIC API /configuration."""
        endpoint = f"{self.sic_url_base}/v1/configuration"

        print(f"Calling {endpoint}...")
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        print("Checking status code is 200..")
        assert (  # noqa: S101
            response.status_code == 200  # noqa: PLR2004
        ), f"Expected status code 200, but got {response.status_code}."

    def test_soc_api_configuration(self) -> None:
        """Test SOC API /configuration."""
        endpoint = f"{self.soc_url_base}/v1/configuration"

        print(f"Calling {endpoint}...")
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        print("Checking status code is 200..")
        assert (  # noqa: S101
            response.status_code == 200  # noqa: PLR2004
        ), f"Expected status code 200, but got {response.status_code}."

    def test_sic_api_search_index(self) -> None:
        """Test SIC API /search-index."""
        endpoint = f"{self.sic_url_base}/v1/search-index"

        print(f"Calling {endpoint}...")
        response = requests.post(
            endpoint,
            json={"query": ["school teacher", "teach maths", "school"]},
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        print("Checking status code is 200..")
        assert (  # noqa: S101
            response.status_code == 200  # noqa: PLR2004
        ), f"Expected status code 200, but got {response.status_code}."

    def test_soc_api_search_index(self) -> None:
        """Test SOC API /search-index."""
        endpoint = f"{self.soc_url_base}/v1/search-index"

        print(f"Calling {endpoint}...")
        response = requests.post(
            endpoint,
            json={"query": ["school teacher", "teach maths", "school"]},
            headers={"Authorization": f"Bearer {self.id_token}"},
            timeout=30,
        )

        print("Checking status code is 200..")
        assert (  # noqa: S101
            response.status_code == 200  # noqa: PLR2004
        ), f"Expected status code 200, but got {response.status_code}."

    def test_sayt_api_suggestions(self) -> None:
        """Test SAYT API."""
        endpoint = f"{self.sayt_url_base}/v1/suggestions"

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
