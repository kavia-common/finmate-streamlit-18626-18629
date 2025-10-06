#!/usr/bin/env bash
set -euo pipefail
# Build verification (no-op) and artifact checks for Streamlit app
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
cd "$WORKSPACE"
VENV="$WORKSPACE/.venv"
# Check venv
if [ ! -d "$VENV" ]; then
  echo ".venv missing" >&2
  exit 2
fi
# Check app entrypoint
if [ ! -f "app.py" ] && [ ! -f "main.py" ]; then
  echo "app entrypoint (app.py or main.py) missing" >&2
  exit 3
fi
# Check requirements
if [ ! -f "requirements.txt" ]; then
  echo "requirements.txt missing" >&2
  exit 4
fi
# No build required for Streamlit; verification passed
echo "build: verification passed"
