#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
cd "$WORKSPACE"
VENV="$WORKSPACE/.venv"
REQ="$WORKSPACE/requirements.txt"
# Create venv if missing
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi
# Use explicit venv python for determinism
PY="$VENV/bin/python"
PIP="$VENV/bin/python -m pip"
# Ensure pip in venv exists (fallback to python -m ensurepip)
if [ ! -x "$VENV/bin/pip" ]; then
  $PY -m ensurepip --upgrade || true
fi
# Upgrade pip/setuptools and show output on failure
$PIP install --upgrade pip setuptools || { echo 'pip/setuptools upgrade failed' >&2; $PIP --version >&2 || true; exit 6; }
# Install from requirements if present and non-empty
if [ -f "$REQ" ] && [ -s "$REQ" ]; then
  $PIP install -r "$REQ" || { echo 'pip install -r requirements.txt failed' >&2; $PIP --version >&2 || true; $VENV/bin/pip list --format=columns >&2 || true; exit 4; }
fi
# Ensure pytest installed
$PIP install pytest || { echo 'pip install pytest failed' >&2; exit 5; }
# Report versions for diagnostics
$PY - <<'PY'
import sys
print('python_executable:' + sys.executable)
try:
    import pip
    print('pip_version:' + getattr(pip, '__version__', 'unknown'))
except Exception:
    print('pip_not_importable')
try:
    import streamlit as s
    print('streamlit_version:' + getattr(s, '__version__', 'unknown'))
except Exception:
    print('streamlit_not_importable')
PY
# Validate streamlit import explicitly (fail if not importable)
$PY - <<'PY'
import importlib,sys
try:
    importlib.import_module('streamlit')
except Exception as e:
    print('streamlit import failed: ' + str(e))
    sys.exit(2)
PY
