#!/usr/bin/env bash
# Simple non-interactive startup script for the Streamlit app.
# Does not assume a virtualenv exists; uses environment python.
# Binds to 0.0.0.0:3000 for preview systems.

set -euo pipefail

# Default to port 3000 unless PORT env var is provided by the environment.
PORT="${PORT:-3000}"

# Ensure we're at the project root of the Streamlit application
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use python -m to avoid PATH issues; no 'source venv/bin/activate'
exec python -m streamlit run app/app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT}" \
  --server.headless=true
