# Preserve exported shell overrides over `.env` while keeping
# `make VAR=value target` as the highest-precedence source.
_ENV_OVERRIDE_VARS := $(foreach v,$(.VARIABLES),$(if $(filter environment environment override,$(origin $(v))),$(v)))
$(foreach v,$(_ENV_OVERRIDE_VARS),$(eval _SAVED_ENV_$(v) := $($(v))))
-include .env
export
$(foreach v,$(_ENV_OVERRIDE_VARS),$(eval $(v) := $(_SAVED_ENV_$(v))))

.PHONY: all
all: ## Show the available make targets.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: clean
clean: ## Clean the temporary files.
	rm -rf .mypy_cache
	rm -rf .ruff_cache

# Make does not like interpreting : in the target name, so we use a variable.
# Override these with exported shell variables or `make VAR=value target`.
VECTOR_STORE_PORT?=8088
SAYT_PORT?=8090
VS_API_CMD=poetry run uvicorn survey_assist_vector_store_api.vector_store_api.main:app --host 0.0.0.0 --port $(VECTOR_STORE_PORT) --reload
SAYT_API_CMD=poetry run uvicorn survey_assist_vector_store_api.sayt_api.main:app --host 0.0.0.0 --port $(SAYT_PORT) --reload

.PHONY: build-vector-store
build-vector-store: ## Build the vector store
	poetry run python scripts/build_vector_store_artifacts.py

.PHONY: build-sayt
build-sayt: ## Build SAYT artifacts
	poetry run python scripts/build_sayt_artifacts.py

.PHONY: run-vector-store-api
run-vector-store-api: ## Run the vector-store API; optionally set/export VECTOR_STORE_PORT and VECTOR_STORE_DIR
	$(VS_API_CMD)

.PHONY: run-sayt-api
run-sayt-api: ## Run the SAYT API; optionally set/export SAYT_PORT and SAYT_ARTIFACT_DIR
	$(SAYT_API_CMD)

.PHONY: run-docs
run-docs: ## Run the mkdocs
	poetry run mkdocs serve

.PHONY: check-python
check-python: ## Format the python code (auto fix)
	poetry run ruff check . --fix
	poetry run ruff format .
	poetry run mypy --follow-untyped-imports src/survey_assist_vector_store_api
	poetry run pylint --verbose .
	poetry run bandit -r src/survey_assist_vector_store_api

.PHONY: check-python-nofix
check-python-nofix: ## Format the python code (no fix)
	poetry run ruff check .
	poetry run ruff format --check .
	poetry run mypy --follow-untyped-imports src/survey_assist_vector_store_api
	poetry run pylint --verbose .
	poetry run bandit -r src/survey_assist_vector_store_api

.PHONY: unit-tests
unit-tests: ## Run the example unit tests
	poetry run pytest --ignore=cicd -m utils --cov=utils --cov-report=term-missing --cov-fail-under=80 --cov-config=.coveragerc

.PHONY: api-tests
api-tests: ## Run the example API tests
	poetry run pytest --ignore=cicd -m api --cov=survey_assist_vector_store_api --cov-report=term-missing --cov-fail-under=80

.PHONY: all-tests
all-tests:
	poetry run pytest --ignore=cicd --cov --cov-report=term-missing --cov-fail-under=80

.PHONY: install
install: ## Install the dependencies
	poetry install --only main --no-root

.PHONY: install-dev
install-dev: ## Install the dev dependencies
	poetry install --no-root

.PHONY: colima-start
colima-start: ## Start Colima
	colima start --cpu 2 --memory 4 --disk 100

.PHONY: colima-stop
colima-stop: ## Stop Colima
	colima stop

.PHONY: docker-build
docker-build: ## Build container images; optionally set service=vector-store-api or service=sayt-api
	docker compose build $(service)

.PHONY: docker-up
docker-up: ## Run API containers; optionally set service=vector-store-api or service=sayt-api
	docker compose up --build $(service)

.PHONY: docker-down
docker-down: ## Stop the running API containers
	docker compose down

.PHONY: docker-clean
docker-clean: ## Clean Docker resources
	DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock" docker system prune -f

.PHONY: podman-up
podman-up: ## Run API containers; optionally set service=vector-store-api or service=sayt-api
	podman compose up --build $(service)

.PHONY: podman-down
podman-down: ## Stop the running API containers
	podman compose down

.PHONY: colima-status
colima-status: ## Check Colima status
	colima status

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install
	poetry run pre-commit install --hook-type pre-push

.PHONY: pre-push-run
pre-push-run:
	poetry run pre-commit run --hook-stage pre-push --all-files

.PHONY: pre-commit-run
pre-commit-run:
	poetry run pre-commit run --all-files

.PHONY: secrets-baseline
secrets-baseline:
	poetry run detect-secrets scan > .secrets.baseline
	poetry run detect-secrets audit .secrets.baseline
