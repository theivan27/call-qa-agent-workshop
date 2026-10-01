#!/usr/bin/env bash
# Sets up the workshop environment in a Codespace (or any dev container).
# Safe to re-run by hand if something went wrong during the build:
#   bash .devcontainer/post-create.sh

set -uo pipefail

cd "$(dirname "$0")/.."

echo ""
echo "Setting up the Call QA Agent workshop"
echo "====================================="

echo ""
echo "1/4  Installing Python packages..."
pip install --upgrade pip --quiet
# No virtual environment on purpose: the Azure Functions host uses the python on
# PATH, so installing into the container's interpreter keeps the two in step.
pip install --quiet -r requirements.txt -r api/requirements.txt

echo "2/4  Installing the Static Web Apps CLI and Azure Functions Core Tools..."
npm install --global --silent @azure/static-web-apps-cli azure-functions-core-tools@4

echo "3/4  Creating your settings files..."
# -n so a rebuild never overwrites values an attendee has already filled in.
cp -n .env.sample .env 2>/dev/null \
  && echo "       created .env" \
  || echo "       .env already exists, left alone"
cp -n api/local.settings.sample.json api/local.settings.json 2>/dev/null \
  && echo "       created api/local.settings.json" \
  || echo "       api/local.settings.json already exists, left alone"

echo "4/4  Checking the tools are available..."
for tool in python az swa func; do
  if command -v "$tool" > /dev/null 2>&1; then
    echo "       ok: $tool"
  else
    echo "       MISSING: $tool  (re-run this script, or rebuild the container)"
  fi
done

cat <<'MESSAGE'

=====================================
Your environment is ready.

Next, follow the workshop guide. Three things to do:

  1. Put your Foundry project endpoint in .env
     and in api/local.settings.json

  2. Sign in to Azure:
       az login --use-device-code

  3. Check everything works:
       python scripts/check_setup.py

To read the guide in here, run:
       swa start guide --port 4281
=====================================

MESSAGE
