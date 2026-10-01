#!/bin/bash

# Wrapper script to run the smoke tests locally
#
# Expected Env variables: 
# CICD_PROJECT_ID - The project id for the CICD project
# SAYT_API_URL - The URL of the Survey Assist UI to run the tests against
# SA_ID_TOKEN - A valid Google Identity Token generated from your credentials (assuming you're running locally) 
#
#
# Expected parameter: [sandbox|dev]
#
# Example ./run_smoke_tests.sh dev

# Please set the environment variable CICD_PROJECT_ID i.e. export CICD_PROJECT_ID=

if [[ ! -v CICD_PROJECT_ID ]]; then
   echo "Please set the environment variable CICD_PROJECT_ID i.e. export CICD_PROJECT_ID="
   exit 1
fi

if [[ $1 = "sandbox" ]] || [[ $1 = "dev" ]] || [[ $1 = "preprod" ]]; then
   echo Test environment "$1"
   export TARGET_ENVIRONMENT=$1
else
  echo "Please pass test environment of 'sandbox', 'dev' or 'preprod' e.g. ./run_smoke_tests.sh sandbox"
  exit 1
fi

if [[ -z "${SIC_API_URL}" ]]; then
    echo Environment variable SIC_API_URL was not set, getting $1 url from parameter store:
    SIC_API_URL=$(gcloud parametermanager parameters versions describe $1 --parameter=infra-test-config --location=global --project $CICD_PROJECT_ID --format=json | python3 -c "import sys, json; print(json.load(sys.stdin)['payload']['data'])" | base64 --decode | python3 -c "import sys, json; print(json.load(sys.stdin)['cr-sic-api-url'])")
    export SIC_API_URL
    echo "$SIC_API_URL"
else
    echo Using SIC_API_URL="$SIC_API_URL"
fi

if [[ -z "${SOC_API_URL}" ]]; then
    echo Environment variable SOC_API_URL was not set, getting $1 url from parameter store:
    SOC_API_URL=$(gcloud parametermanager parameters versions describe $1 --parameter=infra-test-config --location=global --project $CICD_PROJECT_ID --format=json | python3 -c "import sys, json; print(json.load(sys.stdin)['payload']['data'])" | base64 --decode | python3 -c "import sys, json; print(json.load(sys.stdin)['cr-soc-api-url'])")
    export SOC_API_URL
    echo "$SOC_API_URL"
else
    echo Using SOC_API_URL="$SOC_API_URL"
fi

if [[ -z "${SAYT_API_URL}" ]]; then
    echo Environment variable SAYT_API_URL was not set, getting $1 url from parameter store:
    SAYT_API_URL=$(gcloud parametermanager parameters versions describe $1 --parameter=infra-test-config --location=global --project $CICD_PROJECT_ID --format=json | python3 -c "import sys, json; print(json.load(sys.stdin)['payload']['data'])" | base64 --decode | python3 -c "import sys, json; print(json.load(sys.stdin)['cr-sayt-api-url'])")
    export SAYT_API_URL
    echo "$SAYT_API_URL"
else
    echo Using SAYT_API_URL="$SAYT_API_URL"
fi

#
# Example way to set token after gcloud auth login
# export SA_ID_TOKEN=`gcloud auth print-identity-token`
if [[ -z "${UI_SA_ID_TOKEN}" ]]; then
    echo Environment variable SA_ID_TOKEN was not set, getting a new identity token from local credentials, if authenticated.
    UI_SA_ID_TOKEN=$(gcloud auth print-identity-token)   
    export UI_SA_ID_TOKEN 
else
    echo Using currently set SA_ID_TOKEN. If this becomes stale, run export UI_SA_ID_TOKEN=\`gcloud auth print-identity-token\`
fi

pytest -s