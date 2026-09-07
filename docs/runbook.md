# Getting Started Runbook

This page is a follow-along walkthrough for new developers. Unlike `guide.md`, which acts as the reference document for commands, configuration, and deployment options, this runbook starts with one small toy dataset and then shows how to extend the same flow to side-by-side SIC and SOC APIs.

## What You Will Build

The walkthrough covers the full local lifecycle for both services in this repository:

- inspect two checked-in demo CSVs
- build vector-store artifacts
- build SAYT artifacts
- run both FastAPI services locally
- call each API and inspect its response

The demo datasets are intentionally small so developers can inspect them by eye and rerun the full workflow quickly.

## Demo Datasets

The main walkthrough below uses two checked-in SIC demo sources under `data/`:

- `demo_sic_2d_condensed.csv` for the vector-store build
- `demo_sic_2d_sayt.csv` for the SAYT build

This repository also includes a matching SOC demo pair for side-by-side local runs:

- `demo_soc_2d_condensed.csv` for the vector-store build
- `demo_soc_2d_sayt.csv` for the SAYT build

The vector-store source is a local copy of the example SIC 2-digit condensed dataset already used elsewhere in the wider Survey Assist workspace. The SAYT source is a ready-to-use companion CSV with `search_text` and `display_text` columns, so the runbook stays fully copy-pasteable and does not require any preprocessing step.

Because these files live under `data/` rather than `tests/` or `docs/`, they are available to documentation, local walkthroughs, and any future smoke-style checks without looking like packaged runtime data.

## Before You Start

Install dependencies if you have not already:

```shell
poetry install
```

The commands below assume you are running from the repository root.

## 1. Inspect The Demo Inputs

Inspect the vector-store source:

```shell
head data/demo_sic_2d_condensed.csv
```

Inspect the SAYT source:

```shell
head data/demo_sic_2d_sayt.csv
```

What you are looking at:

- `demo_sic_2d_condensed.csv` matches the `label,text` shape expected by the vector-store build
- `demo_sic_2d_sayt.csv` matches the default `search_text,display_text` shape expected by the SAYT build

## 2. Build Vector-Store Artifacts

```shell
make build-vector-store \
  INDEX_SOURCE_FILE=data/demo_sic_2d_condensed.csv \
  VECTOR_STORE_DIR=data/output/vector_store_demo
```

This writes a self-contained set of vector-store artifacts under `data/output/vector_store_demo`.

## 3. Inspect The Vector-Store Output

List the generated files:

```shell
ls data/output/vector_store_demo
```

Inspect the build metadata:

```shell
cat data/output/vector_store_demo/metadata.json
```

The metadata is a good checkpoint because it confirms which source file and embedding model were used during the build.

## 4. Build SAYT Artifacts

```shell
make build-sayt \
  SAYT_SOURCE_FILE=data/demo_sic_2d_sayt.csv \
  SAYT_ARTIFACT_DIR=data/output/sayt_artifact_demo
```

This writes the persisted SAYT artifact under `data/output/sayt_artifact_demo`.

## 5. Inspect The SAYT Output

List the generated files:

```shell
ls data/output/sayt_artifact_demo
```

Inspect the cleaned corpus:

```shell
head data/output/sayt_artifact_demo/corpus.csv
```

The cleaned SAYT corpus is the easiest file to inspect when you want to understand what the suggestion API will load.

## 6. Start The Vector-Store API

In one terminal:

```shell
make run-vector-store-api \
  VECTOR_STORE_DIR=data/output/vector_store_demo \
  VECTOR_STORE_PORT=8088
```

## 7. Start The SAYT API

In a second terminal:

```shell
make run-sayt-api \
  SAYT_ARTIFACT_DIR=data/output/sayt_artifact_demo \
  SAYT_PORT=8090
```

These commands use the default local ports `8088` and `8090` for the two services.

If you want the interactive Swagger docs, open `http://127.0.0.1:8088/docs` for the vector-store API and `http://127.0.0.1:8090/docs` for the SAYT API.

## 8. Inspect The Loaded Configuration

Check the vector-store API configuration:

```shell
curl -s http://127.0.0.1:8088/v1/configuration
```

Check the SAYT API configuration:

```shell
curl -s http://127.0.0.1:8090/v1/configuration
```

The responses should show the demo artifact directories you passed into each `make run-*` command.

## 9. Exercise The Vector-Store API

```shell
curl -s http://127.0.0.1:8088/v1/search-index \
  -H 'Content-Type: application/json' \
  -d '{"query": ["software developer", "computer programming"]}'
```

This endpoint accepts a list of cumulative query fragments. On the toy dataset, you should see the computer-programming SIC division near the top of the results.

## 10. Exercise The SAYT API

```shell
curl -s http://127.0.0.1:8090/v1/suggestions \
  -H 'Content-Type: application/json' \
  -d '{"query": "comp", "limit": 5}'
```

You should see suggestions headed by the computer-programming SIC division, using the `display_text` values from `data/demo_sic_2d_sayt.csv`.

## 11. Clean Up Generated Artifacts

When you are done, stop the two API processes and remove the generated demo outputs:

```shell
rm -rf data/output/vector_store_demo data/output/sayt_artifact_demo
```

## Run SIC And SOC Side By Side

The main walkthrough above stays on one toy dataset so the first local run is easy to follow. When you want SIC and SOC running together, keep the artifact directories separate and give each running API process its own port.

If you are starting from scratch, build four taxonomy-specific artifact directories:

```shell
make build-vector-store \
  INDEX_SOURCE_FILE=data/demo_sic_2d_condensed.csv \
  VECTOR_STORE_DIR=data/output/vector_store_sic_demo

make build-vector-store \
  INDEX_SOURCE_FILE=data/demo_soc_2d_condensed.csv \
  VECTOR_STORE_DIR=data/output/vector_store_soc_demo

make build-sayt \
  SAYT_SOURCE_FILE=data/demo_sic_2d_sayt.csv \
  SAYT_ARTIFACT_DIR=data/output/sayt_artifact_sic_demo

make build-sayt \
  SAYT_SOURCE_FILE=data/demo_soc_2d_sayt.csv \
  SAYT_ARTIFACT_DIR=data/output/sayt_artifact_soc_demo
```

If you have already followed the SIC walkthrough above, you only need to build the two SOC artifact directories before starting the extra processes.

Run the four local services in four terminals, using different ports for each process.

Terminal 1, start the SIC vector-store API:

```shell
make run-vector-store-api \
  VECTOR_STORE_DIR=data/output/vector_store_sic_demo \
  VECTOR_STORE_PORT=8088
```

Terminal 2, start the SOC vector-store API:

```shell
make run-vector-store-api \
  VECTOR_STORE_DIR=data/output/vector_store_soc_demo \
  VECTOR_STORE_PORT=8089
```

Terminal 3, start the SIC SAYT API:

```shell
make run-sayt-api \
  SAYT_ARTIFACT_DIR=data/output/sayt_artifact_sic_demo \
  SAYT_PORT=8090
```

Terminal 4, start the SOC SAYT API:

```shell
make run-sayt-api \
  SAYT_ARTIFACT_DIR=data/output/sayt_artifact_soc_demo \
  SAYT_PORT=8091
```

This side-by-side example keeps SIC on the default local ports and places the matching SOC services on the next free ports.

For interactive Swagger docs in the side-by-side setup, open `http://127.0.0.1:8088/docs`, `http://127.0.0.1:8089/docs`, `http://127.0.0.1:8090/docs`, and `http://127.0.0.1:8091/docs` for the four running services.

Check that each process loaded the expected artifact directory:

Check the SIC vector-store API configuration:

```shell
curl -s http://127.0.0.1:8088/v1/configuration
```

Check the SOC vector-store API configuration:

```shell
curl -s http://127.0.0.1:8089/v1/configuration
```

Check the SIC SAYT API configuration:

```shell
curl -s http://127.0.0.1:8090/v1/configuration
```

Check the SOC SAYT API configuration:

```shell
curl -s http://127.0.0.1:8091/v1/configuration
```

If you prefer different ports, that is fine. The important rule when running locally is that every running SIC or SOC API process gets its own port.

When you are done, stop the four processes and remove the four side-by-side demo outputs:

```shell
rm -rf \
  data/output/vector_store_sic_demo \
  data/output/vector_store_soc_demo \
  data/output/sayt_artifact_sic_demo \
  data/output/sayt_artifact_soc_demo
```

## What To Inspect Afterwards

This runbook is most useful when developers look at the intermediate outputs as well as the API responses.

High-signal files are:

- `data/demo_sic_2d_condensed.csv`
- `data/demo_sic_2d_sayt.csv`
- `data/demo_soc_2d_condensed.csv`
- `data/demo_soc_2d_sayt.csv`
- `data/output/vector_store_demo/metadata.json`
- `data/output/sayt_artifact_demo/corpus.csv`

That gives a concrete map of how this repository turns source CSV data into persisted retrieval artifacts and then into running local APIs.
