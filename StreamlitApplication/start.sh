#!/usr/bin/env bash
set -euo pipefail

# Determine working directory to app root (directory of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default to config-defined port (3000), allow override via STREAMLIT_PORT env
PORT="${STREAMLIT_PORT:-3000}"
ADDR="${STREAMLIT_ADDRESS:-0.0.0.0}"

# Ensure required directories exist relative to app/
mkdir -p app/data app/reports

# Run streamlit with explicit server args so it works even if config is ignored by environment
exec streamlit run app/app.py --server.address="${ADDR}" --server.port="${PORT}" --server.headless=true
