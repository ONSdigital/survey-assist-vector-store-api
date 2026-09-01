# Survey Assist Vector Store API

[![CI](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/ci.yml/badge.svg?branch=main)]

<!-- These could be split out
![CI](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/ci.yml/badge.svg)
![Tests](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/tests.yml/badge.svg)
![Bandit](https://github.com/ONSdigital/survey-assist-vector-store-api/actions/workflows/security.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/ONSdigital/survey-assist-vector-store-api)
-->

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/github/license/ONSdigital/survey-assist-vector-store-api)
![Release](https://img.shields.io/github/v/release/ONSdigital/survey-assist-vector-store-api)
![Status](https://img.shields.io/badge/code%20status-in%20development%20-red)

## Overview

This repository now hosts two related FastAPI services used by Survey Assist:

- a vector-store API backed by persisted embedding artifacts
- a search-as-you-type (SAYT) API backed by persisted SAYT artifacts

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Running Locally](#running-locally)
- [Configuration](#configuration)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Security](#security)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)
- [Maintainers](#maintainers)
- [Additional Documentation](#additional-documentation)

## Features

- FastAPI endpoints
- Industry (SIC) search over persisted vector-store artifacts
- Occupation (SOC) search over persisted vector-store artifacts
- Search-as-you-type suggestion serving
- Artifact build scripts for both service types
- API documentation

## Architecture

The services in this repository consist of:

- FastAPI endpoints
- ClassifAI used for vector-store retrieval artifacts
- SAYT retrieval components from `survey-assist-embed-core`
- all-MiniLM-L6-v2 used for embeddings where required
- Deployed as Google Cloud Run services

Depending on configuration and entrypoint, the code can deploy vector-store or SAYT serving workloads.

**Important** - In the deployed solution, this service is private to GCP services, it will only be called via the main Survey Assist API.

## Prerequisites

- Python 3.12
- Poetry 2.1.3 or later
- Git
- Make
- Docker / Colima (optional) / Podman
- Google Cloud SDK

## Local Development Setup

### Clone Repository

```shell
git clone https://github.com/ONSdigital/survey-assist-vector-store-api.git
```

### Install Dependencies

```shell
poetry install
```

### Install Git Hooks

This repository uses pre-commit hooks to perform code quality, security, and secret-scanning checks before code is committed.

```shell
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## Running Locally

### Build Artifacts

Build the vector-store artifacts:

```shell
make build-vector-store
```

Build the SAYT artifacts:

```shell
make build-sayt
```

You can also run the build scripts directly and inspect their supported CLI flags with `--help`:

```shell
poetry run python scripts/build_vector_store_artifacts.py --help
poetry run python scripts/build_sayt_artifacts.py --help
```

### Start Applications

Run the vector-store API:

```shell
make run-vector-store-api
```

Run the SAYT API:

```shell
make run-sayt-api
```

Direct `make` runs can take these values from `.env`, exported shell variables, or `make VAR=value` overrides. When more than one source is set, shell variables and `make VAR=value` overrides take precedence. This keeps the workflow taxonomy-agnostic: the same targets can run SIC, SOC, or future knowledgebases by changing artifact-directory and port variables. Docker and Podman Compose read the same values from `.env` or your shell environment:

```shell
make run-vector-store-api VECTOR_STORE_DIR=vector_store_sic VECTOR_STORE_PORT=8088
make run-vector-store-api VECTOR_STORE_DIR=vector_store_soc VECTOR_STORE_PORT=8089
make run-sayt-api SAYT_ARTIFACT_DIR=sayt_artifact_sic SAYT_PORT=8090
make run-sayt-api SAYT_ARTIFACT_DIR=sayt_artifact_soc SAYT_PORT=8091
```

### Run Containerised Services

The repository includes a root `compose.yaml` and a root multi-stage `Dockerfile` for running the vector-store and SAYT APIs locally with Docker Compose.

#### Using Docker

Build the images, start the services, and stop them again with:

```shell
make docker-build
make docker-up
make docker-down
```

#### Using Podman

Note, you may need to increase the default podman machine config to run these services - see [the guide setup section](docs/guide.md#setup) for more details.

```shell
make podman-up
make podman-down
```

#### Further Information

By default, Docker or Podman Compose publishes:

- vector-store API on `http://localhost:8088`
- SAYT API on `http://localhost:8090`

For single-service runs, artifact-directory setup, and port overrides, see [the guide setup section](docs/guide.md#setup).

### API Documentation

Vector-store docs: http://localhost:8088/docs

SAYT docs: http://localhost:8090/docs

The OpenAPI descriptions include the installed package versions for `survey-assist-vector-store-api` and `survey-assist-embed-core`.

Key endpoints:

- Vector-store search: `POST /v1/search-index`, accepting cumulative query fragments in `query`
- Vector-store configuration: `GET /v1/configuration`, returning the loaded embedding configuration
- SAYT suggestions: `POST /v1/suggestions`, accepting `query` and optional positive `limit`, and returning scored suggestions under `suggestions`
- SAYT configuration: `GET /v1/configuration`, returning the loaded SAYT configuration

For the SAYT suggestions endpoint, `limit` is an optional positive per-request override. If it is omitted, the API falls back to the default baked into the loaded SAYT artifact, which is set by `DEFAULT_NUM_SUGGESTIONS` when the artifact is built.

## Configuration

Copy `.env.example` to `.env` if you want local defaults. You can also export the same variables in your shell or pass `make VAR=value` for one-off runs. The workflow is taxonomy-agnostic: point the same build and run commands at different source files, artifact directories, and ports for SIC, SOC, or other knowledgebases.

The highest-signal variables are:

- `VECTOR_STORE_DIR` and `SAYT_ARTIFACT_DIR` for the runtime artifact locations
- `INDEX_SOURCE_FILE` for vector-store builds
- `SAYT_SOURCE_FILE`, `SEARCH_TEXT_COL`, `DISPLAY_TEXT_COL`, `MIN_CHARS`, and `DEFAULT_NUM_SUGGESTIONS` for SAYT builds

For the full runtime/build variable matrix, defaults, and notes about how `limit` interacts with `DEFAULT_NUM_SUGGESTIONS`, see [the guide configuration section](docs/guide.md#configuration).

## Repository Structure

Update as the repository evolves

```txt
survey-assist-vector-store-api/
|-- cicd/                           # GCP cloud build cicd pipelines
|-- docs/                           # mkdocs documentation
|-- scripts/                        # scripts not used inline in the application
|-- src/                            # main source
|-- tests/                          # pytest unit tests
|-- .github/                        # GitHub actions workflows
|-- README.md                       # This file
```

## Testing

Run all of the unit tests

```shell
make all-tests
```

Additional testing guidance is available in [CONTRIBUTING.md](CONTRIBUTING.md).

## Code Quality

Running validation checks:

```shell
make check-python-nofix
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards and validation requirements.

## Security

Security checks are performed using:

- Bandit
- GitHub Dependabot
- Secret scanning

Security vulnerabilities **must not** be disclosed publicly.

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Documentation

Documentation is maintained using MkDocs.

```shell
make run-docs
```

## Release Process

Release guidance is documented in [RELEASING.md](RELEASING.md).

## Contributing

Please read [the contribution guidelines](CONTRIBUTING.md) before creating a pull request.

## License

This project is licensed under the terms in [LICENSE](LICENSE).

## Maintainers

Repository ownership and review responsibility are listed in [CODEOWNERS](CODEOWNERS).

## Additional Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [RELEASING.md](RELEASING.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)
- [CODEOWNERS](CODEOWNERS)
