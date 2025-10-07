#!/usr/bin/env bash
set -euo pipefail
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
cd "$WS"
VENV="$WS/.venv"
PYBIN="$VENV/bin/python"
PYTEST_VER="7.4.0"
TESTFILE="$WS/.ci_test_streamlit_env.py"
LOG="$WS/pytest_install.log"
# ensure venv python exists
if [ ! -x "$PYBIN" ]; then
  echo "Error: venv python not found at $PYBIN" >&2
  exit 2
fi
# install pinned pytest (non-interactive, no cache)
"$PYBIN" -m pip install --no-cache-dir --disable-pip-version-check pytest=="$PYTEST_VER" > "$LOG" 2>&1 || (tail -n 200 "$LOG" >&2; exit 8)
# create namespaced test file (idempotent overwrite)
cat > "$TESTFILE" <<'PY'
import importlib
import pytest
# fail if streamlit cannot be imported
try:
    importlib.import_module('streamlit')
except Exception as e:
    pytest.fail(f"streamlit import failed: {e}")
# optional libs: report their absence but don't fail
for pkg in ('pandas', 'reportlab', 'fpdf'):
    try:
        importlib.import_module(pkg)
    except Exception:
        print(f"OPTIONAL_MISSING: {pkg}")
PY
# run pytest on the single file
"$PYBIN" -m pytest -q "$TESTFILE"
